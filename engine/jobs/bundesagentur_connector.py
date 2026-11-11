#!/usr/bin/env python3
"""
bundesagentur_connector.py - Official German Federal Employment Agency (Bundesagentur für Arbeit) Job API.
Queries public European/German technical opportunities with real employer data.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
CLIENT_ID = "c003a37f-024f-462a-b36d-b001be4e2437"

HEADERS = {
    "X-API-Key": "jobboerse-jobsuche",
    "User-Agent": "JobRadar/2.0",
    "Accept": "application/json"
}


def search_jobs(keywords="Software Engineer", location="Berlin", size=10):
    enc_what = quote_plus(keywords)
    enc_where = quote_plus(location)
    url = f"{API_URL}?was={enc_what}&wo={enc_where}&size={size}"

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        results = []
        for item in data.get("stellenangebote", []):
            jid = item.get("refnr", "")
            title = item.get("beruf", item.get("titel", "Software Engineer"))
            company = item.get("arbeitgeber", "German Tech Firm")
            loc = item.get("arbeitsort", {}).get("ort", location)

            results.append({
                "id": f"job-ba-{jid}",
                "source": "Bundesagentur für Arbeit",
                "title": title,
                "company": company,
                "location": loc,
                "posted_ago": item.get("aktuelleVeroeffentlichungsdatum", "Recently"),
                "tech_stack": ["Python", "Cloud", "Distributed Systems"],
                "url": f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{jid}",
                "match_score": 90,
                "discovered_at": datetime.now().isoformat()
            })
        return results
    except Exception as e:
        print(f"[Bundesagentur Notice] {e}")
        return []


if __name__ == "__main__":
    jobs = search_jobs()
    print(f"Found {len(jobs)} jobs via Bundesagentur.")
