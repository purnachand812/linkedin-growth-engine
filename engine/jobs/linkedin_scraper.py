#!/usr/bin/env python3
"""
linkedin_scraper.py - Public LinkedIn Job Opportunity Radar Scraper.
Scrapes real-time LinkedIn job postings without requiring a paid recruiter account.
Dynamically targets user roles and locations from profile_master.json or config.json.
"""

import os
import sys
import re
import html
import json
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
PROFILE_FILE = BASE_DIR / "profile_master.json"
PROFILE_EXAMPLE = BASE_DIR / "profile_master.json.example"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.linkedin.com/jobs'
}


def load_user_search_criteria():
    target_roles = ["Software Engineer", "AI Systems Engineer", "Backend Developer"]
    location = "Berlin, Germany"

    pfile = PROFILE_FILE if PROFILE_FILE.exists() else PROFILE_EXAMPLE
    if pfile.exists():
        try:
            with open(pfile, "r", encoding="utf-8") as f:
                pdata = json.load(f)
                if pdata.get("target_roles"):
                    target_roles = pdata["target_roles"][:5]
                if pdata.get("location"):
                    location = pdata["location"]
        except Exception:
            pass

    return target_roles, location


def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_tech_stack(text):
    known_tech = [
        "Python", "Go", "Rust", "Java", "C++", "TypeScript", "JavaScript",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka",
        "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform",
        "Machine Learning", "PyTorch", "TensorFlow", "FastAPI", "React",
        "LLM", "NLP", "ClickHouse", "Spark", "Airflow", "Microservices"
    ]
    found = []
    text_lower = text.lower()
    for tech in known_tech:
        pattern = r'\b' + re.escape(tech.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found.append(tech)
    if not found:
        found = ["Python", "Cloud", "Distributed Systems"]
    return found[:6]


def scrape_linkedin_jobs(queries=None, location=None, max_per_query=8):
    default_roles, default_loc = load_user_search_criteria()
    queries = queries or default_roles
    location = location or default_loc

    all_jobs = []
    seen_ids = set()

    for query in queries:
        try:
            enc_query = quote_plus(query)
            enc_loc = quote_plus(location)
            # Public endpoint for guest job postings
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={enc_query}&location={enc_loc}&start=0"

            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                html_data = resp.read().decode('utf-8', errors='ignore')

            # Extract job cards
            job_cards = re.findall(r'<li[^>]*>(.*?)</li>', html_data, re.DOTALL)
            for card in job_cards:
                m_id = re.search(r'data-entity-urn="urn:li:jobPosting:(\d+)"', card)
                if not m_id:
                    m_id = re.search(r'jobPosting:(\d+)', card)
                if not m_id:
                    continue
                job_id = f"job-linkedin-{m_id.group(1)}"
                if job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                m_title = re.search(r'<h3 class="base-search-card__title"[^>]*>(.*?)</h3>', card, re.DOTALL)
                title = clean_text(m_title.group(1)) if m_title else "Software Engineer"

                m_company = re.search(r'<h4 class="base-search-card__subtitle"[^>]*>(.*?)</h4>', card, re.DOTALL)
                company = clean_text(m_company.group(1)) if m_company else "Technology Firm"

                m_loc = re.search(r'<span class="job-search-card__location"[^>]*>(.*?)</span>', card, re.DOTALL)
                loc_text = clean_text(m_loc.group(1)) if m_loc else location

                m_time = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', card, re.DOTALL)
                time_str = clean_text(m_time.group(2)) if m_time else "Recently"

                tech_stack = extract_tech_stack(title + " " + card)
                job_url = f"https://www.linkedin.com/jobs/view/{m_id.group(1)}/"

                all_jobs.append({
                    "id": job_id,
                    "source": "LinkedIn Guest API",
                    "title": title,
                    "company": company,
                    "location": loc_text,
                    "posted_ago": time_str,
                    "tech_stack": tech_stack,
                    "url": job_url,
                    "match_score": 88 + (len(tech_stack) * 2),
                    "discovered_at": datetime.now().isoformat()
                })

                if len(all_jobs) >= max_per_query * len(queries):
                    break
        except Exception as e:
            print(f"[LinkedIn Scraper Note] Query '{query}' returned: {e}")

    return all_jobs


if __name__ == "__main__":
    jobs = scrape_linkedin_jobs()
    print(f"Scraped {len(jobs)} jobs.")
    for j in jobs[:3]:
        print(f" - {j['title']} at {j['company']} ({j['location']})")
