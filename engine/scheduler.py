#!/usr/bin/env python3
"""
scheduler.py - Autonomous Background Scheduling Daemon.
Monitors user-configured prime-time publishing windows across any timezone,
rate-limits posts, auto-publishes approved candidate drafts, and tracks telemetry.
"""

import os
import sys
import time
import json
import signal
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine import publisher

CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE = BASE_DIR / "config.json.example"
QUEUE_FILE = BASE_DIR / "queue" / "queue_summary.json"
HISTORY_DIR = BASE_DIR / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
STATUS_FILE = HISTORY_DIR / "daemon_status.json"

RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    print(f"\n[DAEMON] Shutdown signal ({sig}) received. Stopping cleanly...")
    RUNNING = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def load_config():
    target = CONFIG_FILE if CONFIG_FILE.exists() else CONFIG_EXAMPLE
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "content_strategy": {
            "max_posts_per_day": 2,
            "target_timezone": "UTC",
            "posting_windows": [
                {"name": "Morning Slot", "start": "08:30", "end": "10:00"},
                {"name": "Evening Slot", "start": "17:00", "end": "18:30"}
            ]
        }
    }


def is_prime_time(cfg):
    now_hour_min = time.strftime("%H:%M")
    windows = cfg.get("content_strategy", {}).get("posting_windows", [])
    for win in windows:
        if win["start"] <= now_hour_min <= win["end"]:
            return True, win
    return False, None


def count_posts_published_today():
    log_file = HISTORY_DIR / "publishing_log.json"
    if not log_file.exists():
        return 0
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            logs = json.load(f)
        today_prefix = time.strftime("%Y-%m-%d")
        return sum(1 for e in logs if e.get("published_at", "").startswith(today_prefix))
    except Exception:
        return 0


def update_status(message, extra=None):
    current = {
        "status": "RUNNING",
        "last_heartbeat": datetime.now().isoformat(),
        "log": []
    }
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                current.update(json.load(f))
        except Exception:
            pass

    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    current.setdefault("log", []).append(entry)
    current["log"] = current["log"][-50:]  # Keep rolling 50 items

    if extra:
        current.update(extra)

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)


def run_cycle():
    cfg = load_config()
    strategy = cfg.get("content_strategy", {})
    max_daily = strategy.get("max_posts_per_day", 2)

    is_prime, active_window = is_prime_time(cfg)
    today_count = count_posts_published_today()

    if not QUEUE_FILE.exists():
        return

    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            qdata = json.load(f)
    except Exception:
        return

    candidates = qdata.get("candidates", [])
    approved = [
        c for c in candidates
        if c.get("status") == "APPROVED"
        and not c.get("published_at")
        and not publisher.is_already_published(candidate_id=c.get("id"), topic=c.get("topic"))[0]
    ]

    telemetry = {
        "current_time": time.strftime("%H:%M:%S"),
        "is_prime_time": is_prime,
        "current_window": active_window["name"] if active_window else "Outside Prime Time",
        "approved_queue_count": len(approved),
        "published_today": today_count
    }

    if not is_prime:
        update_status("Standing by outside scheduled posting windows.", telemetry)
        return

    if today_count >= max_daily:
        update_status(f"Daily rate limit reached ({today_count}/{max_daily}). Standing by.", telemetry)
        return

    if not approved:
        update_status("No approved candidates in queue.", telemetry)
        return

    target = approved[0]
    cid = target.get("id")
    topic = target.get("topic")

    md_path = BASE_DIR / target.get("file", "")
    if not md_path.exists():
        update_status(f"Error: Draft file missing for #{cid}", telemetry)
        return

    content = md_path.read_text(encoding="utf-8")
    post_text = ""
    if "### COMPLETE LINKEDIN POST" in content:
        parts = content.split("### COMPLETE LINKEDIN POST")
        post_text = parts[1].split("### PRIMARY SOURCES")[0].strip()
    else:
        post_text = content.strip()

    first_comment = ""
    if "### PRIMARY SOURCES" in content:
        sources_part = content.split("### PRIMARY SOURCES")[1]
        first_comment = sources_part.split("###")[0].strip()

    img_path = None
    v_rel = target.get("visual", "")
    if v_rel:
        full_v = BASE_DIR / v_rel
        if full_v.exists():
            img_path = str(full_v)

    try:
        update_status(f"🚀 Publishing Candidate #{cid}: '{topic}' ({active_window['name']})", telemetry)
        res = publisher.publish_post(
            text=post_text,
            image_path=img_path,
            first_comment_text=first_comment,
            candidate_id=cid,
            topic=topic
        )
        target["status"] = "PUBLISHED"
        target["published_at"] = res.get("published_at")
        target["linkedin_post_id"] = res.get("post_urn")
        target["linkedin_post_url"] = res.get("post_url")

        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(qdata, f, indent=2)

        update_status(f"🎉 Successfully published Candidate #{cid}! Live: {res.get('post_url')}")
    except Exception as e:
        update_status(f"❌ Publishing error for #{cid}: {e}", telemetry)


def start_daemon(loop_interval_sec=60):
    print("=" * 65)
    print("  LinkedIn Growth Engine - Autonomous Scheduler")
    print("=" * 65)
    update_status("Scheduler daemon initialized.")
    while RUNNING:
        try:
            run_cycle()
        except Exception as e:
            print(f"[ERROR] Cycle failure: {e}")
            update_status(f"Scheduler exception: {e}")
        time.sleep(loop_interval_sec)


if __name__ == "__main__":
    if "--once" in sys.argv:
        print("[SCHEDULER] Executing single publishing evaluation cycle...")
        run_cycle()
        print("[SCHEDULER] Cycle complete.")
    else:
        start_daemon()
