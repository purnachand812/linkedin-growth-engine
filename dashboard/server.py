#!/usr/bin/env python3
"""
server.py - White-Label Dashboard API Server for LinkedIn Growth Engine.
Fully decoupled from personal references; dynamically serves user profile branding from config.json.
Provides endpoints for Queue Review, Publishing, Voice Quality Gate, Analytics, and LinkedIn OAuth.
"""

import os
import sys
import json
import time
import re
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / ".env")

from engine import publisher, detector

CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE = BASE_DIR / "config.json.example"
QUEUE_FILE = BASE_DIR / "queue" / "queue_summary.json"
HISTORY_DIR = BASE_DIR / "history"
PUBLISHING_LOG_FILE = HISTORY_DIR / "publishing_log.json"
STATUS_FILE = HISTORY_DIR / "daemon_status.json"
PORT = int(os.getenv("PORT", 3000))


def load_config():
    target = CONFIG_FILE if CONFIG_FILE.exists() else CONFIG_EXAMPLE
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "profile": {
            "full_name": "Author",
            "initials": "AU",
            "headline": "Systems Engineer",
            "location": "Global"
        }
    }


def parse_candidate_markdown(file_path):
    if not file_path or not file_path.exists():
        return {}
    try:
        content = file_path.read_text(encoding="utf-8")
        post_text = ""
        post_m = re.search(r'###\s*COMPLETE LINKEDIN POST[^\n]*\n(.*?)(?=\n###|\n---|\Z)', content, re.DOTALL)
        if post_m:
            post_text = post_m.group(1).strip()
        else:
            post_text = content
        return {"post_copy": post_text}
    except Exception:
        return {}


class WhiteLabelHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "dashboard"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/visuals/"):
            file_name = path.replace("/visuals/", "")
            target_file = BASE_DIR / "visuals" / file_name
            if target_file.exists():
                self.send_response(200)
                content_type = "image/png" if file_name.endswith(".png") else "application/octet-stream"
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(target_file.stat().st_size))
                self.end_headers()
                with open(target_file, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "Visual not found")
                return

        if path == "/api/status":
            self.handle_get_status()
        elif path == "/api/profile":
            self.send_json(load_config())
        elif path == "/api/queue":
            self.handle_get_queue()
        elif path == "/api/linkedin/auth-url":
            self.send_json({"auth_url": publisher.get_auth_url()})
        elif path == "/api/linkedin/callback":
            self.handle_oauth_callback(parsed.query)
        elif path == "/api/analytics":
            self.handle_get_analytics()
        elif path == "/api/daemon/status":
            self.handle_get_daemon_status()
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

        if path == "/api/publish":
            self.handle_post_publish(data)
        elif path == "/api/detect":
            self.handle_post_detect(data)
        elif path == "/api/candidate/status":
            self.handle_post_candidate_status(data)
        elif path == "/api/candidate/save":
            self.handle_post_candidate_save(data)
        elif path == "/api/profile":
            self.handle_post_profile(data)
        else:
            self.send_error(404, "API route not found")

    def send_json(self, data, code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_get_status(self):
        qdata = {}
        if QUEUE_FILE.exists():
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    qdata = json.load(f)
            except Exception:
                pass
        cands = qdata.get("candidates", [])
        active = [c for c in cands if c.get("status") in ("APPROVED", "WAITING_FOR_APPROVAL", "DRAFT") and not c.get("published_at")]
        published = [c for c in cands if c.get("status") == "PUBLISHED" or c.get("published_at")]

        creds = publisher.load_credentials()
        has_token = bool(creds.get("access_token"))

        self.send_json({
            "status": "online",
            "port": PORT,
            "linkedin_connected": has_token,
            "member_name": creds.get("member_name", "Not Connected"),
            "counts": {
                "total": len(cands),
                "active": len(active),
                "approved": sum(1 for c in active if c.get("status") == "APPROVED"),
                "published": len(published)
            }
        })

    def handle_get_queue(self):
        if not QUEUE_FILE.exists():
            self.send_json({"candidates": [], "active_candidates": [], "archived_candidates": []})
            return

        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            qdata = json.load(f)

        cands = qdata.get("candidates", [])
        active = []
        archived = []

        for c in cands:
            cid = c.get("id")
            # Parse post copy from file if not present
            if not c.get("post_copy") and c.get("file"):
                fpath = BASE_DIR / c.get("file")
                pdata = parse_candidate_markdown(fpath)
                c["post_copy"] = pdata.get("post_copy", "")

            # Format visual URL
            if c.get("visual"):
                v_file = BASE_DIR / c.get("visual")
                if v_file.exists():
                    c["visual_url"] = f"/visuals/{v_file.name}"

            pub_check, pub_entry = publisher.is_already_published(candidate_id=cid, topic=c.get("topic"))
            if pub_check or c.get("status") == "PUBLISHED" or c.get("published_at"):
                c["status"] = "PUBLISHED"
                c["is_archived"] = True
                if pub_entry:
                    c["linkedin_post_id"] = pub_entry.get("post_id", c.get("linkedin_post_id"))
                    c["linkedin_post_url"] = pub_entry.get("post_url", c.get("linkedin_post_url"))
                archived.append(c)
            else:
                c["is_archived"] = False
                active.append(c)

        self.send_json({
            "candidates": cands,
            "active_candidates": active,
            "archived_candidates": archived,
            "active_count": len(active),
            "archived_count": len(archived),
            "total_count": len(cands)
        })

    def handle_post_publish(self, data):
        cid = data.get("candidate_id")
        text = data.get("text", "")
        img = data.get("image_path", None)
        topic = data.get("topic", "")

        # If text or img missing, auto-populate from candidate
        if (not text or not img) and QUEUE_FILE.exists() and cid:
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    qdata = json.load(f)
                for c in qdata.get("candidates", []):
                    if c.get("id") == cid:
                        if not topic:
                            topic = c.get("topic", "")
                        if not text and c.get("file"):
                            pdata = parse_candidate_markdown(BASE_DIR / c.get("file"))
                            text = pdata.get("post_copy", "")
                        if not img and c.get("visual"):
                            v_file = BASE_DIR / c.get("visual")
                            if v_file.exists():
                                img = str(v_file)
                        break
            except Exception as e:
                print(f"[Publish Warning] Failed to autofill candidate data: {e}")

        try:
            res = publisher.publish_post(text=text, image_path=img, candidate_id=cid, topic=topic)
            self.send_json({"success": True, "result": res})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, code=500)

    def handle_post_detect(self, data):
        text = data.get("text", "")
        score_res = detector.score_draft(text)
        self.send_json(score_res)

    def handle_post_candidate_status(self, data):
        cid = data.get("candidate_id")
        new_status = data.get("status", "APPROVED")

        if QUEUE_FILE.exists():
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                qdata = json.load(f)
            for c in qdata.get("candidates", []):
                if c.get("id") == cid:
                    c["status"] = new_status
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(qdata, f, indent=2)

        self.send_json({"success": True})

    def handle_post_candidate_save(self, data):
        topic = data.get("topic", "Technical Deep Dive")
        beat = data.get("beat", "Software Engineering")
        post_copy = data.get("post_copy", "")
        score = data.get("score", 85)
        status = data.get("status", "APPROVED")
        cid = data.get("candidate_id")

        qdata = {"candidates": []}
        if QUEUE_FILE.exists():
            try:
                with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                    qdata = json.load(f)
            except Exception:
                pass

        cands = qdata.get("candidates", [])
        if not cid:
            existing_ids = [c.get("id", 0) for c in cands if isinstance(c.get("id"), int)]
            cid = max(existing_ids, default=0) + 1

        slug = re.sub(r'[^a-z0-9]+', '_', topic.lower()).strip('_')[:30]
        c_dir = BASE_DIR / "queue" / "candidates"
        c_dir.mkdir(parents=True, exist_ok=True)
        md_file = c_dir / f"candidate_{cid}_{slug}.md"

        md_content = f"""# Candidate {cid}: {topic}

- Status: {status}
- Beat: {beat}
- Editorial Score: {score}/100

---

### COMPLETE LINKEDIN POST

{post_copy}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Update or add in queue
        found = False
        rel_path = f"queue/candidates/candidate_{cid}_{slug}.md"
        for c in cands:
            if c.get("id") == cid:
                c["topic"] = topic
                c["beat"] = beat
                c["score"] = score
                c["status"] = status
                c["file"] = rel_path
                c["post_copy"] = post_copy
                found = True
                break
        if not found:
            cands.append({
                "id": cid,
                "topic": topic,
                "beat": beat,
                "score": score,
                "status": status,
                "file": rel_path,
                "post_copy": post_copy
            })

        qdata["candidates"] = cands
        with open(QUEUE_FILE, "w", encoding="utf-8") as f:
            json.dump(qdata, f, indent=2)

        self.send_json({"success": True, "candidate_id": cid})

    def handle_post_profile(self, data):
        cfg = load_config()
        if "profile" in data:
            cfg["profile"].update(data["profile"])
        if "content_strategy" in data:
            cfg["content_strategy"].update(data["content_strategy"])
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        self.send_json({"success": True, "config": cfg})

    def handle_oauth_callback(self, query_str):
        params = parse_qs(query_str)
        code = params.get("code", [None])[0]
        if code:
            try:
                publisher.exchange_code_for_token(code)
                self.send_response(302)
                self.send_header("Location", "/#connected")
                self.end_headers()
                return
            except Exception as e:
                self.send_error(500, f"Token exchange failed: {e}")
                return
        self.send_error(400, "Missing OAuth code parameter")

    def handle_get_analytics(self):
        log_file = PUBLISHING_LOG_FILE
        posts = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    posts = json.load(f)
            except Exception:
                pass
        self.send_json({
            "total_posts_published": len(posts),
            "posts": posts
        })

    def handle_get_daemon_status(self):
        if STATUS_FILE.exists():
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    self.send_json(json.load(f))
                    return
            except Exception:
                pass
        self.send_json({"status": "STANDBY", "log": []})


def run():
    ThreadingHTTPServer.allow_reuse_address = True
    server_address = ('', PORT)
    while True:
        try:
            httpd = ThreadingHTTPServer(server_address, WhiteLabelHandler)
            print(f"[OK] Studio Hub running at http://localhost:{PORT}", flush=True)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...", flush=True)
            try:
                httpd.server_close()
            except Exception:
                pass
            break
        except Exception as e:
            print(f"[RETRY] Socket reset ({e}). Restarting in 2s...", flush=True)
            try:
                httpd.server_close()
            except Exception:
                pass
            time.sleep(2)


if __name__ == "__main__":
    run()
