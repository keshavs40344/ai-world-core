"""Strips the corrupted duplicate tail from planetary_governance_daemon.py
and rewrites a clean entrypoint."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

src = open("planetary_governance_daemon.py", encoding="utf-8", errors="replace").read()

# Find the first occurrence of the entrypoint section
MARKER = "# ═══════════════════════════════════════════════════════════════════════════\n# SECTION 10 ▸ INTEGRATION HOOKS"

idx = src.find(MARKER)
if idx == -1:
    print("MARKER NOT FOUND — checking alternate...")
    MARKER = "# SECTION 10"
    idx = src.find(MARKER)

print(f"Clean cut at index: {idx} / {len(src)}")
clean_body = src[:idx]

# Append clean entrypoint
tail = '''# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10 ▸ INTEGRATION HOOKS
# ═══════════════════════════════════════════════════════════════════════════
def get_daemon_task():
    """
    Integration hook for sentinel_self_healing_watchdog.py.
    Call from inside an existing asyncio event loop:
        from planetary_governance_daemon import get_daemon_task
        asyncio.create_task(get_daemon_task())
    """
    senate = PlanetaryAdministrationCore()
    return senate.start_planetary_council_loop(interval_seconds=3600)


async def _boot_immediate_then_hourly():
    """Run one decree immediately, then hand off to hourly loop."""
    senate = PlanetaryAdministrationCore()
    await senate.ratify_hourly_decree()
    await asyncio.sleep(3600)
    await senate.start_planetary_council_loop()


# ═══════════════════════════════════════════════════════════════════════════
# ENTRYPOINT
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GPAA-2026 Planetary Administration Daemon")
    parser.add_argument("--once",     action="store_true", help="Run one decree cycle and exit")
    parser.add_argument("--all",      action="store_true", help="Deploy ALL 7 faculty terminals immediately")
    parser.add_argument("--interval", type=int, default=3600, help="Loop interval in seconds (default: 3600)")
    args = parser.parse_args()

    senate = PlanetaryAdministrationCore()

    if args.all:
        log.info("BOOTSTRAP MODE — deploying all 7 faculty terminals...")
        async def deploy_all():
            for _ in range(len(GLOBAL_FACULTIES)):
                await senate.ratify_hourly_decree()
                await asyncio.sleep(0.1)
        asyncio.run(deploy_all())
        log.info("All 7 faculty terminals deployed.")
        tg.notify_all_bootstrap(len(GLOBAL_FACULTIES))
    elif args.once:
        asyncio.run(senate.ratify_hourly_decree())
    else:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(senate.start_planetary_council_loop(interval_seconds=args.interval))
'''

final = clean_body.rstrip() + "\n\n" + tail

open("planetary_governance_daemon.py", "w", encoding="utf-8").write(final)
print("File rewritten. Lines:", final.count("\n"))

# Verify compile
import py_compile, tempfile, os
tf = tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8")
tf.write(final); tf.close()
try:
    py_compile.compile(tf.name, doraise=True)
    print("AST COMPILE: PASS")
except Exception as e:
    print("AST COMPILE: FAIL —", e)
finally:
    os.unlink(tf.name)
