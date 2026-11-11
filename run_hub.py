#!/usr/bin/env python3
"""
run_hub.py - 1-Click Studio & Scheduler Launcher for LinkedIn Growth Engine.
Spawns the web dashboard on port 3000 and the autonomous background scheduler.
Handles graceful shutdowns on Ctrl+C.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

processes = []


def signal_handler(sig, frame):
    print("\n[HUB] Stopping studio and scheduler gracefully...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    print("""
======================================================================
  LinkedIn Growth Engine - Studio & Autonomous Scheduler
======================================================================
  Starting local services:
    - Web Studio:      http://localhost:3000
    - Scheduler:       Active (monitoring posting windows)
======================================================================
""")

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # Start Dashboard Server
    server_cmd = [sys.executable, str(BASE_DIR / "dashboard" / "server.py")]
    p_server = subprocess.Popen(server_cmd, env=env)
    processes.append(p_server)

    # Start Scheduler Daemon
    sched_cmd = [sys.executable, str(BASE_DIR / "engine" / "scheduler.py")]
    p_sched = subprocess.Popen(sched_cmd, env=env)
    processes.append(p_sched)

    try:
        while True:
            time.sleep(1)
            # Check if any process terminated unexpectedly
            for p in processes:
                if p.poll() is not None:
                    print(f"[WARN] A background service stopped (code: {p.returncode}).")
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()

