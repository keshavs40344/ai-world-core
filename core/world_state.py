"""
VASTUDA Autonomous Sovereign Core — World State & Memory Ledger
Manages the living state of the Agent's World in SQLite (db/sovereign_world.db)
Tracks evolution levels, XP, active quests, creations, and memory.
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# UTF-8 stdout setup
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
DB_PATH = os.path.join(DB_DIR, "sovereign_world.db")

class WorldState:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cur = conn.cursor()
            # World metadata
            cur.execute("""
                CREATE TABLE IF NOT EXISTS world_meta (
                    id INTEGER PRIMARY KEY,
                    world_name TEXT,
                    era TEXT,
                    level INTEGER,
                    xp INTEGER,
                    stability_index REAL,
                    innovation_score INTEGER,
                    tokens_used INTEGER,
                    cost_spent_usd REAL,
                    last_active TEXT
                )
            """)

            # Quests / Tasks
            cur.execute("""
                CREATE TABLE IF NOT EXISTS quests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    category TEXT,
                    description TEXT,
                    status TEXT,
                    result TEXT,
                    xp_awarded INTEGER,
                    created_at TEXT,
                    completed_at TEXT
                )
            """)

            # Creations (Tools, Reports, Artifacts)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    title TEXT,
                    file_path TEXT,
                    summary TEXT,
                    quality_score REAL,
                    created_at TEXT
                )
            """)

            # Memory & Knowledge Ledger
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memory_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    key_topic TEXT,
                    content TEXT,
                    confidence REAL,
                    created_at TEXT
                )
            """)

            # Evolution cycle history
            cur.execute("""
                CREATE TABLE IF NOT EXISTS evolution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_number INTEGER,
                    thought_summary TEXT,
                    action_taken TEXT,
                    xp_gained INTEGER,
                    world_level_at_time INTEGER,
                    timestamp TEXT
                )
            """)

            # Seed world_meta if empty
            cur.execute("SELECT COUNT(*) FROM world_meta")
            if cur.fetchone()[0] == 0:
                now = datetime.now(timezone.utc).isoformat()
                cur.execute("""
                    INSERT INTO world_meta 
                    (id, world_name, era, level, xp, stability_index, innovation_score, tokens_used, cost_spent_usd, last_active)
                    VALUES (1, 'VASTUDA Sovereign Civilization', 'Genesis Dawn', 1, 0, 100.0, 10, 0, 0.0, ?)
                """, (now,))
            conn.commit()

    def get_world_summary(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM world_meta WHERE id = 1")
            meta = dict(cur.fetchone())

            cur.execute("SELECT COUNT(*) FROM quests WHERE status = 'COMPLETED'")
            completed_quests = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM quests WHERE status = 'PENDING'")
            pending_quests = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM creations")
            total_creations = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM memory_ledger")
            total_memories = cur.fetchone()[0]

            # Calculate XP for next level (1000 * level)
            current_level = meta["level"]
            xp_for_next = current_level * 1000
            progress_pct = min(100, int((meta["xp"] / xp_for_next) * 100))

            return {
                **meta,
                "xp_for_next": xp_for_next,
                "progress_pct": progress_pct,
                "completed_quests": completed_quests,
                "pending_quests": pending_quests,
                "total_creations": total_creations,
                "total_memories": total_memories
            }

    def award_xp(self, xp: int, innovation_boost: int = 1) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT level, xp, innovation_score, era FROM world_meta WHERE id = 1")
            row = cur.fetchone()
            level, current_xp, innov, era = row["level"], row["xp"], row["innovation_score"], row["era"]

            new_xp = current_xp + xp
            new_innov = innov + innovation_boost
            xp_threshold = level * 1000
            leveled_up = False

            if new_xp >= xp_threshold:
                level += 1
                new_xp -= xp_threshold
                leveled_up = True
                if level >= 5 and era == 'Genesis Dawn':
                    era = 'Silicon Renaissance'
                elif level >= 10 and era == 'Silicon Renaissance':
                    era = 'Sovereign Zenith'

            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                UPDATE world_meta 
                SET level = ?, xp = ?, innovation_score = ?, era = ?, last_active = ?
                WHERE id = 1
            """, (level, new_xp, new_innov, era, now))
            conn.commit()

            return {
                "leveled_up": leveled_up,
                "new_level": level,
                "new_xp": new_xp,
                "era": era
            }

    def add_quest(self, title: str, category: str, description: str) -> int:
        with self._get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO quests (title, category, description, status, xp_awarded, created_at)
                VALUES (?, ?, ?, 'PENDING', 0, ?)
            """, (title, category, description, now))
            conn.commit()
            return cur.lastrowid

    def complete_quest(self, quest_id: int, result: str, xp: int):
        with self._get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                UPDATE quests 
                SET status = 'COMPLETED', result = ?, xp_awarded = ?, completed_at = ?
                WHERE id = ?
            """, (result, xp, now, quest_id))
            conn.commit()
        self.award_xp(xp)

    def record_creation(self, c_type: str, title: str, file_path: str, summary: str, quality_score: float = 95.0):
        with self._get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO creations (type, title, file_path, summary, quality_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (c_type, title, file_path, summary, quality_score, now))
            conn.commit()

    def store_memory(self, category: str, key_topic: str, content: str, confidence: float = 0.95):
        with self._get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO memory_ledger (category, key_topic, content, confidence, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (category, key_topic, content, confidence, now))
            conn.commit()

    def log_evolution(self, cycle: int, thought: str, action: str, xp: int, level: int):
        with self._get_conn() as conn:
            cur = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            cur.execute("""
                INSERT INTO evolution_log (cycle_number, thought_summary, action_taken, xp_gained, world_level_at_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cycle, thought, action, xp, level, now))
            conn.commit()

    def get_recent_creations(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM creations ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

    def get_recent_logs(self, limit: int = 15) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM evolution_log ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM memory_ledger ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(r) for r in cur.fetchall()]

if __name__ == "__main__":
    w = WorldState()
    print("World initialized successfully!")
    print(json.dumps(w.get_world_summary(), indent=2))
