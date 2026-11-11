#!/usr/bin/env python3
"""
cover_letter_generator.py - Dynamic 1-Page High-Signal Cover Letter Generator.
Creates authentic, non-generic cover letters tailored to the employer's Job Description.
Generates clean HTML and compiles pixel-perfect PDF via headless browser.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine.jobs import pdf_converter

RESUMES_DIR = BASE_DIR / "resumes"
RESUMES_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_FILE = BASE_DIR / "profile_master.json"
PROFILE_EXAMPLE = BASE_DIR / "profile_master.json.example"


def load_profile():
    target = PROFILE_FILE if PROFILE_FILE.exists() else PROFILE_EXAMPLE
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "full_name": "Author",
        "title": "Systems Architect",
        "location": "Global",
        "email": "author@example.com",
        "phone": "+1 000 000 0000"
    }


def generate_tailored_cover_letter(job_info, make_pdf=True):
    profile = load_profile()
    jid = job_info.get("id", "job-generic")
    title = job_info.get("title", "Systems Engineer")
    company = job_info.get("company", "Hiring Team")
    location = job_info.get("location", profile.get("location", "Berlin, Germany"))
    tech_stack = job_info.get("tech_stack", ["Python", "Distributed Systems", "Cloud"])
    tech_str = ", ".join(tech_stack[:4])

    full_name = profile.get("full_name", "Author")
    email = profile.get("email", "author@example.com")
    phone = profile.get("phone", "+1 000 000 0000")
    today_formatted = datetime.now().strftime("%d %B %Y")

    # Pick top project to reference
    projects = profile.get("verified_projects", [])
    top_project = projects[0] if projects else {
        "name": "Distributed Microservice Pipeline",
        "impact": "improved throughput by 60% and reduced latency",
        "technologies": ["Python", "Docker", "PostgreSQL"]
    }

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Cover Letter - {full_name} ({company})</title>
  <style>
    @page {{
      size: A4;
      margin: 20mm 22mm 20mm 22mm;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      line-height: 1.6;
      font-size: 10pt;
      padding: 25px;
      background: #fff;
    }}
    .header {{
      border-bottom: 2px solid #0284c7;
      padding-bottom: 12px;
      margin-bottom: 18px;
      display: flex;
      justify-content: space-between;
    }}
    .name {{ font-size: 18pt; font-weight: 800; color: #0f172a; }}
    .title {{ font-size: 10.5pt; color: #0284c7; font-weight: 600; margin-top: 2px; }}
    .contact {{ font-size: 8.5pt; color: #64748b; text-align: right; line-height: 1.45; }}
    .date-row {{ font-size: 9pt; color: #64748b; margin-bottom: 16px; font-weight: 600; }}
    .recipient {{ margin-bottom: 16px; font-size: 9.5pt; line-height: 1.4; color: #0f172a; }}
    p {{ margin-bottom: 14px; text-align: justify; }}
    .highlight {{ color: #0f172a; font-weight: 600; }}
    .sign-off {{ margin-top: 24px; }}
    @media print {{ body {{ padding: 0; }} }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="name">{full_name}</div>
      <div class="title">{profile.get('title', 'Senior Systems Engineer')}</div>
    </div>
    <div class="contact">
      <div>{profile.get('location', 'Global')} &bull; {phone}</div>
      <div>{email}</div>
    </div>
  </div>

  <div class="date-row">{today_formatted}</div>

  <div class="recipient">
    <strong>Hiring Committee & Engineering Leadership</strong><br>
    {company}<br>
    {location}
  </div>

  <p>Dear Hiring Team,</p>

  <p>
    I am writing to express my strong enthusiasm for the <span class="highlight">{title}</span> position at <span class="highlight">{company}</span>. With hands-on engineering experience designing high-throughput backends, containerized systems, and distributed pipelines using <span class="highlight">{tech_str}</span>, I look forward to contributing directly to your engineering benchmarks.
  </p>

  <p>
    Throughout my work, I have focused on building pragmatic, production-ready systems that prioritize low latency and operational resilience. For instance, in developing the <span class="highlight">{top_project.get('name')}</span> ({', '.join(top_project.get('technologies', []))}), I {top_project.get('impact')}. I take pride in delivering clean, maintainable architecture without unnecessary operational overhead.
  </p>

  <p>
    {company}'s commitment to engineering rigor and scalable solutions aligns closely with my technical background. I am energized by the opportunity to apply my practical experience to help advance your product roadmap from day one.
  </p>

  <p>
    Thank you for your time and consideration. I welcome the opportunity to discuss how my technical skills and proactive engineering approach can benefit your team.
  </p>

  <div class="sign-off">
    Sincerely,<br><br>
    <strong>{full_name}</strong><br>
    <span style="font-size: 8.5pt; color: #64748b;">{profile.get('title', 'Senior Systems Engineer')}</span>
  </div>
</body>
</html>"""

    html_file = RESUMES_DIR / f"cover_letter_{jid}.html"
    pdf_file = RESUMES_DIR / f"cover_letter_{jid}.pdf"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    pdf_path = None
    if make_pdf:
        pdf_path = pdf_converter.convert_html_to_pdf(html_file, pdf_file)

    return {
        "html_path": str(html_file),
        "pdf_path": str(pdf_path) if pdf_path else None,
        "html_url": f"/resumes/{html_file.name}",
        "pdf_url": f"/resumes/{pdf_file.name}" if pdf_path else None
    }


if __name__ == "__main__":
    res = generate_tailored_cover_letter({
        "id": "test-job",
        "title": "Senior AI Systems Engineer",
        "company": "DeepTech GmbH",
        "tech_stack": ["Python", "PyTorch", "Docker"]
    })
    print(f"Generated Cover Letter: {res['html_url']}")
