#!/usr/bin/env python3
"""
setup.py - Interactive Onboarding Setup Wizard for LinkedIn Growth Engine.
Guides new users through profile customization, content niche configuration,
LinkedIn API credentials, and environment verification in under 2 minutes.
"""

import os
import sys
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE = BASE_DIR / "config.json.example"
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"


def banner():
    print("""
================================================================================
     _     _       _            _ _             ____                 _   _     
    | |   (_)_ __ | | _____  __| (_)_ __       / ___|_ __ _____  _| |_| |__  
    | |   | | '_ \| |/ / _ \/ _` | | '_ \     | |  _| '__/ _ \ \ /\ / / __| '_ \ 
    | |___| | | | |   <  __/ (_| | | | | |    | |_| | | | (_) \ V  V /| |_| | | |
    |_____|_|_| |_|_|\_\___|\__,_|_|_| |_|     \____|_|  \___/ \_/\_/  \__|_| |_|
                       AUTOMATION STUDIO & GROWTH OS
================================================================================
    Welcome! This wizard will configure your personalized LinkedIn automation engine.
""")


def prompt(label, default=""):
    d_str = f" [{default}]" if default else ""
    try:
        val = input(f" > {label}{d_str}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print(default)
        return default


def check_prerequisites():
    print("\n[1/4] Checking System Prerequisites...")
    
    # Check Python version
    py_ver = sys.version_info
    if py_ver < (3, 10):
        print(f"  ❌ Error: Python 3.10+ required. Current version is {py_ver.major}.{py_ver.minor}")
        sys.exit(1)
    print(f"  ✓ Python {py_ver.major}.{py_ver.minor}.{py_ver.micro} detected.")

    # Check for Chrome / Chromium
    chrome_paths = [
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]
    has_chrome = any(p and os.path.exists(p) for p in chrome_paths)
    if has_chrome:
        print("  ✓ Google Chrome / Chromium detected (used for rendering Canva graphics).")
    else:
        print("  ⚠️ Notice: Google Chrome not found in standard PATH. Visual graphics will require Chrome installed.")


def setup_profile():
    print("\n[2/4] Profile & Personal Branding Customization:")
    full_name = prompt("Full Name", "Alex Rivera")
    initials = prompt("Initials (for graphic author badge)", "".join([w[0] for w in full_name.split()][:2]).upper())
    headline = prompt("Headline / Title", "Senior AI Systems Engineer & Distributed Architect")
    location = prompt("Location (City, Country)", "Berlin, Germany")
    timezone = prompt("Target Audience Timezone (e.g. Europe/Berlin, America/New_York, UTC)", "Europe/Berlin")

    return {
        "full_name": full_name,
        "initials": initials,
        "headline": headline,
        "location": location,
        "timezone": timezone
    }


def setup_niche():
    print("\n[3/4] Content Strategy & Niche Focus:")
    print("  1) AI Systems, LLM Inference & Open-Source Engineering")
    print("  2) Cloud Infrastructure, Kubernetes & Modern DevOps")
    print("  3) Distributed Backend, Databases & High-Throughput Systems")
    print("  4) Full-Stack Web Architecture & Performance")
    print("  5) Custom Niche")

    choice = prompt("Select primary domain (1-5)", "1")
    niche_map = {
        "1": "AI Systems, LLM Inference & Open-Source Engineering",
        "2": "Cloud Infrastructure, Kubernetes & Modern DevOps",
        "3": "Distributed Backend, Databases & High-Throughput Systems",
        "4": "Full-Stack Web Architecture & Performance"
    }

    if choice in niche_map:
        selected_niche = niche_map[choice]
    else:
        selected_niche = prompt("Enter your custom technical niche", "AI & Software Engineering")

    return selected_niche


def setup_linkedin_credentials():
    print("\n[4/4] LinkedIn Developer App Credentials:")
    print("  (If you haven't created your LinkedIn App yet, you can press ENTER to configure later via the UI)")
    client_id = prompt("LinkedIn Client ID", "")
    client_secret = prompt("LinkedIn Client Secret", "")
    redirect_uri = prompt("Redirect URI", "http://localhost:3000/api/linkedin/callback")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }


def main():
    banner()
    check_prerequisites()

    profile_data = setup_profile()
    niche = setup_niche()
    creds = setup_linkedin_credentials()

    # Build config.json
    cfg = {
        "profile": {
            "full_name": profile_data["full_name"],
            "initials": profile_data["initials"],
            "headline": profile_data["headline"],
            "location": profile_data["location"],
            "avatar_filename": ""
        },
        "content_strategy": {
            "primary_niche": niche,
            "target_audience": "Engineering Leaders, Practitioners, and Technical Founders",
            "target_timezone": profile_data["timezone"],
            "max_posts_per_day": 2,
            "posting_windows": [
                {"name": "Morning Standup (Prime)", "start": "08:30", "end": "10:00"},
                {"name": "Midday Tech Catchup", "start": "12:00", "end": "13:30"},
                {"name": "Evening Engineering Wrap", "start": "17:00", "end": "18:30"}
            ]
        },
        "voice_rules": {
            "forbid_em_dashes": True,
            "forbidden_buzzwords": [
                "delve", "leverage", "game-changer", "revolutionary", "unlock",
                "landscape", "groundbreaking", "transformative", "paradigm shift",
                "unprecedented", "seamless", "cutting-edge", "robust", "crucial"
            ],
            "require_hardware_metrics": True,
            "require_tested_declaration": True
        }
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    print("\n✓ Generated config.json with your personalized branding.")

    # Build .env
    env_content = f"""LINKEDIN_CLIENT_ID={creds['client_id']}
LINKEDIN_CLIENT_SECRET={creds['client_secret']}
LINKEDIN_REDIRECT_URI={creds['redirect_uri']}

PORT=3000
HOST=127.0.0.1
"""
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✓ Generated .env with configuration parameters.")

    # Seed initial candidates
    print("\nSeeding starter candidates and rendering Canva graphics...")
    try:
        from engine.trend_radar import seed_initial_candidates
        seed_initial_candidates()
        print("✓ Starter queue initialized with 3 approved candidates and Canva graphics.")
    except Exception as e:
        print(f"⚠️ Initial seed note: {e}")

    print("""
================================================================================
  🎉 SETUP COMPLETE! Your LinkedIn Automation Studio is Ready!
================================================================================

  To start your local studio & background scheduler:
    $ python run_hub.py

  Then open your browser at:
    http://localhost:3000

  Next Steps:
  1. If you haven't linked your LinkedIn account, click 'Connect LinkedIn' in the UI.
  2. Review your initial candidate queue and approve drafts.
  3. The background scheduler will automatically publish during your configured windows.
================================================================================
""")


if __name__ == "__main__":
    main()

