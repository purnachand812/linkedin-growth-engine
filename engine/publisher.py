#!/usr/bin/env python3
"""
publisher.py - Official LinkedIn API Publishing & Media Dispatch Engine.
Handles OAuth 2.0 exchange, image asset initialization, binary upload,
post publishing (/rest/posts), and automatic primary link first-commenting.
"""

import os
import sys
import re
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

HISTORY_DIR = BASE_DIR / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_FILE = HISTORY_DIR / "credentials.json"
PUBLISHING_LOG_FILE = HISTORY_DIR / "publishing_log.json"

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_IMAGES_INIT_URL = "https://api.linkedin.com/rest/images?action=initializeUpload"
LINKEDIN_POSTS_URL = "https://api.linkedin.com/rest/posts"
LINKEDIN_VERSION = "202401"


def load_credentials():
    creds = {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:3000/api/linkedin/callback"),
        "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN", ""),
        "member_urn": os.getenv("LINKEDIN_MEMBER_URN", ""),
        "member_name": os.getenv("LINKEDIN_MEMBER_NAME", ""),
        "expires_at": 0
    }
    if CREDENTIALS_FILE.exists():
        try:
            with open(CREDENTIALS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for k, v in saved.items():
                    if v:
                        creds[k] = v
        except Exception:
            pass
    return creds


def save_credentials(creds):
    CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2)


def get_auth_url():
    creds = load_credentials()
    params = {
        "response_type": "code",
        "client_id": creds["client_id"],
        "redirect_uri": creds["redirect_uri"],
        "scope": "openid profile email w_member_social",
        "state": "white_label_linkedin_auth"
    }
    req = requests.Request("GET", LINKEDIN_AUTH_URL, params=params)
    return req.prepare().url


def exchange_code_for_token(code):
    creds = load_credentials()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": creds["redirect_uri"],
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"]
    }
    resp = requests.post(LINKEDIN_TOKEN_URL, data=data, timeout=15)
    resp.raise_for_status()
    token_data = resp.json()

    access_token = token_data.get("access_token", "")
    expires_in = token_data.get("expires_in", 5184000)

    creds["access_token"] = access_token
    creds["expires_at"] = int(time.time()) + expires_in

    # Fetch user info to store member URN
    user_info = fetch_user_info(access_token)
    creds["member_urn"] = f"urn:li:person:{user_info.get('sub', '')}"
    creds["member_name"] = user_info.get("name", "")

    save_credentials(creds)
    return creds


def fetch_user_info(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(LINKEDIN_USERINFO_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_auth_headers():
    creds = load_credentials()
    token = creds.get("access_token")
    if not token:
        raise ValueError("No LinkedIn access token configured. Please connect LinkedIn via OAuth.")
    return {
        "Authorization": f"Bearer {token}",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }


def upload_image(image_path):
    headers = get_auth_headers()
    creds = load_credentials()
    member_urn = creds.get("member_urn")

    init_payload = {
        "initializeUploadRequest": {
            "owner": member_urn
        }
    }
    init_resp = requests.post(LINKEDIN_IMAGES_INIT_URL, headers=headers, json=init_payload, timeout=20)
    init_resp.raise_for_status()
    init_data = init_resp.json().get("value", {})

    upload_url = init_data.get("uploadUrl")
    image_urn = init_data.get("image")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    upload_headers = {
        "Authorization": headers["Authorization"],
        "Content-Type": "image/png"
    }
    up_resp = requests.put(upload_url, data=img_bytes, headers=upload_headers, timeout=60)
    up_resp.raise_for_status()
    return image_urn


def post_first_comment(post_urn, comment_text):
    if not comment_text:
        return None
    headers = get_auth_headers()
    creds = load_credentials()
    member_urn = creds.get("member_urn")

    comment_url = f"https://api.linkedin.com/rest/socialActions/{post_urn}/comments"
    payload = {
        "actor": member_urn,
        "message": {
            "text": comment_text
        }
    }
    resp = requests.post(comment_url, headers=headers, json=payload, timeout=15)
    if resp.status_code in (200, 201):
        return resp.json().get("id", "comment_created")
    return None


def publish_post(text, image_path=None, first_comment_text=None, candidate_id=None, topic=None):
    headers = get_auth_headers()
    creds = load_credentials()
    member_urn = creds.get("member_urn")

    image_urn = None
    if image_path and os.path.exists(image_path):
        try:
            image_urn = upload_image(image_path)
        except Exception as e:
            print(f"[WARN] Image upload failed ({e}), falling back to text-only post.")

    payload = {
        "author": member_urn,
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    if image_urn:
        payload["content"] = {
            "media": {
                "id": image_urn
            }
        }

    resp = requests.post(LINKEDIN_POSTS_URL, headers=headers, json=payload, timeout=20)
    resp.raise_for_status()

    post_urn = resp.headers.get("x-restli-id", "")
    if not post_urn and resp.text:
        try:
            post_urn = resp.json().get("id", "")
        except Exception:
            pass

    post_url = f"https://www.linkedin.com/feed/update/{post_urn}/" if post_urn else ""

    comment_id = None
    if first_comment_text and post_urn:
        try:
            comment_id = post_first_comment(post_urn, first_comment_text)
        except Exception as e:
            print(f"[WARN] First comment failed: {e}")

    result = {
        "success": True,
        "post_urn": post_urn,
        "post_url": post_url,
        "image_urn": image_urn,
        "first_comment_id": comment_id,
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    record_published_post(candidate_id, topic, text, result)
    return result


def record_published_post(candidate_id, topic, text, result):
    logs = []
    if PUBLISHING_LOG_FILE.exists():
        try:
            with open(PUBLISHING_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    entry = {
        "candidate_id": candidate_id,
        "topic": topic,
        "post_id": result.get("post_urn"),
        "post_url": result.get("post_url"),
        "published_at": result.get("published_at"),
        "has_image": bool(result.get("image_urn")),
        "status": "PUBLISHED"
    }
    logs.insert(0, entry)
    with open(PUBLISHING_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


def is_already_published(candidate_id=None, topic=None):
    if not PUBLISHING_LOG_FILE.exists():
        return False, None
    try:
        with open(PUBLISHING_LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        norm_topic = (topic or "").strip().lower()
        for entry in logs:
            if candidate_id is not None and str(entry.get("candidate_id")) == str(candidate_id):
                return True, entry
            if norm_topic and entry.get("topic", "").strip().lower() == norm_topic:
                return True, entry
    except Exception:
        pass
    return False, None
