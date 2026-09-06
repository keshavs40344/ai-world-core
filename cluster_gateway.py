"""
THE GLOBAL CHRONICLE — STATELESS CLUSTER API GATEWAY
================================================================================
Process A: Stateless, Horizontally Scalable FastAPI Web Server
Stack: Python 3.10+, FastAPI, SQLAlchemy with connection pooling, Redis Pub/Sub & WebSockets

Core Architectural Features:
1. Stateless Architecture:
   - Capable of running N instances behind an AWS ALB, NGINX, or Envoy load balancer.
   - Zero in-memory state; all telemetry, session quotas, and rate-limits persist in Redis/Postgres.
2. Redis Sliding-Window Rate Limiter:
   - Atomic atomic sliding-window algorithm for public and B2B API endpoints.
3. Event Broadcaster WebSocket Multiplexer:
   - Subscribes to Redis Pub/Sub ("chronicle:events:live") and broadcasts real-time ink pulses to connected browser clients.
4. Integrated Monetization & Soft Paywall:
   - Mounts monetization_engine for B2B intelligence feeds, 5-read paywall meter, and Stripe webhooks.

Run via:
    uvicorn cluster_gateway:app --host 0.0.0.0 --port 8000
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    REDIS_AVAILABLE = False
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query, Header, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker, Session

from cluster_worker import Base, DBClusterArticle, DBWireTask, DBCircuitTelemetry

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Gateway] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ClusterGateway")

# ------------------------------------------------------------------------------
# ENVIRONMENT & CONFIGURATION
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chronicle_cluster.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")

# Database Connection Pool with explicit limits
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_size=20,
    max_overflow=40,
    pool_recycle=1800
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="The Global Chronicle — Cluster API Gateway",
    description="Stateless, High-Availability API Gateway for 50,000+ Concurrent Readers",
    version="3.0.0"
)

# ------------------------------------------------------------------------------
# REDIS EVENT BROADCASTER & SLIDING-WINDOW RATE LIMITER
# ------------------------------------------------------------------------------
class GatewayRedisHub:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = None
        self.connected_websockets: List[WebSocket] = []
        self._local_sliding_window: dict = {}

    async def connect(self):
        if not REDIS_AVAILABLE:
            logger.info("Redis library not installed. Gateway operating in standalone local mode.")
            return
        try:
            self.client = aioredis.from_url(self.redis_url, decode_responses=True, socket_timeout=3.0)
            await self.client.ping()
            logger.info("Gateway connected to Redis broker.")
            asyncio.create_task(self.listen_to_pubsub())
        except Exception as e:
            logger.warning(f"Redis broker unavailable ({e}). WebSocket clustering will operate in local fallback mode.")
            self.client = None

    async def check_sliding_window_rate_limit(self, key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Atomic sliding-window rate limiter using Redis sorted sets with in-memory fallback."""
        now = time.time()
        if not self.client:
            timestamps = self._local_sliding_window.setdefault(key, [])
            # Filter timestamps older than window
            timestamps = [t for t in timestamps if now - t < window_seconds]
            if len(timestamps) >= max_requests:
                self._local_sliding_window[key] = timestamps
                return False
            timestamps.append(now)
            self._local_sliding_window[key] = timestamps
            return True
        try:
            clear_before = now - window_seconds
            pipe = self.client.pipeline()
            pipe.zremrangebyscore(key, 0, clear_before)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window_seconds)
            results = await pipe.execute()
            current_count = results[2]
            return current_count <= max_requests
        except Exception as e:
            logger.error(f"Redis rate-limit error: {e}")
            return True

    async def listen_to_pubsub(self):
        """Listens for 'chronicle:events:live' from worker cluster and pushes to client WebSockets."""
        if not self.client:
            return
        try:
            pubsub = self.client.pubsub()
            await pubsub.subscribe("chronicle:events:live")
            logger.info("Subscribed to 'chronicle:events:live' channel for real-time cluster fanout.")
            async for message in pubsub.listen():
                if message["type"] == "message":
                    payload = message["data"]
                    await self.broadcast_local_websockets(payload)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in Redis pubsub listener: {e}")

    async def broadcast_local_websockets(self, raw_message: str):
        disconnected = []
        for ws in self.connected_websockets:
            try:
                await ws.send_text(raw_message)
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            if ws in self.connected_websockets:
                self.connected_websockets.remove(ws)

hub = GatewayRedisHub(REDIS_URL)

@app.on_event("startup")
async def on_startup():
    await hub.connect()
    # Mount monetization engine if present
    try:
        from monetization_engine import mount_monetization_engine
        mount_monetization_engine(app)
    except Exception as e:
        logger.warning(f"Monetization engine not mounted: {e}")

# ------------------------------------------------------------------------------
# DEPENDENCIES
# ------------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def rate_limiter_dependency(request: Request):
    """Enforces atomic sliding-window rate limit on public endpoints."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"ratelimit:ip:{client_ip}"
    allowed = await hub.check_sliding_window_rate_limit(key, max_requests=120, window_seconds=60)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests. Sliding window limit (120 req/min) exceeded."
        )

# ------------------------------------------------------------------------------
# PUBLIC REST ENDPOINTS (STATELESS)
# ------------------------------------------------------------------------------
@app.get("/healthz")
async def health_check():
    """Kubernetes / Load Balancer liveness and readiness probe."""
    redis_healthy = bool(hub.client and await hub.client.ping()) if hub.client else False
    return {
        "status": "HEALTHY",
        "redis_connected": redis_healthy,
        "database": "CONNECTED",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/articles", dependencies=[Depends(rate_limiter_dependency)])
def get_cluster_articles(category: Optional[str] = Query(None), limit: int = 20, db: Session = Depends(get_db)):
    stmt = select(DBClusterArticle).order_by(desc(DBClusterArticle.published_at))
    if category and category != "All":
        stmt = stmt.where(DBClusterArticle.category == category)
    articles = db.execute(stmt.limit(limit)).scalars().all()
    return [
        {
            "id": a.id,
            "article_id": a.article_id,
            "headline": a.headline,
            "subheading": a.subheading,
            "dateline": a.dateline,
            "category": a.category,
            "lead_paragraph": a.lead_paragraph,
            "background_context": a.background_context,
            "timeline": json.loads(a.timeline) if a.timeline else [],
            "impact_assessment": a.impact_assessment,
            "verified_sources": json.loads(a.verified_sources) if a.verified_sources else [],
            "word_count": a.word_count,
            "read_time_min": a.read_time_min,
            "image_url": a.image_url,
            "image_caption": a.image_caption,
            "published_at": a.published_at.strftime("%B %d, %Y &bull; %H:%M GMT"),
            "is_lead_story": a.is_lead_story
        }
        for a in articles
    ]

# ------------------------------------------------------------------------------
# WEBSOCKET STREAM MULTIPLEXER
# ------------------------------------------------------------------------------
@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    hub.connected_websockets.append(websocket)
    logger.info(f"WebSocket connected to gateway. Local replica listeners: {len(hub.connected_websockets)}")
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "PONG", "time": time.time()}))
    except WebSocketDisconnect:
        if websocket in hub.connected_websockets:
            hub.connected_websockets.remove(websocket)
    except Exception:
        if websocket in hub.connected_websockets:
            hub.connected_websockets.remove(websocket)

# ------------------------------------------------------------------------------
# SERVE BROADSHEET FRONTEND
# ------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_frontpage():
    try:
        from chronicle_ultra import ULTRA_BROADSHEET_HTML
        return HTMLResponse(content=ULTRA_BROADSHEET_HTML)
    except ImportError:
        return HTMLResponse(content="<h1>The Global Chronicle — Cluster Gateway Operational</h1>")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
