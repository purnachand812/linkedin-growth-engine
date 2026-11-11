#!/usr/bin/env python3
"""
resume_tailor.py - Dynamic ATS-Compliant 2-Page CV Generator.
Customizes professional tech resumes tailored specifically to targeted Job Descriptions (JD).
Matches skills, orders relevant projects, formats CEFR languages, and generates both HTML and pixel-perfect PDF.
"""

import os
import sys
import json
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


def generate_tailored_resume(job_info, make_pdf=True):
    profile = load_profile()
    jid = job_info.get("id", "job-generic")
    title = job_info.get("title", "Systems Engineer")
    company = job_info.get("company", "Tech Enterprise")
    location = job_info.get("location", profile.get("location", "Berlin, Germany"))
    tech_stack = [t.lower() for t in job_info.get("tech_stack", [])]

    full_name = profile.get("full_name", "Author")
    email = profile.get("email", "author@example.com")
    phone = profile.get("phone", "+1 000 000 0000")
    linkedin_url = profile.get("linkedin_url", "")
    github_url = profile.get("github_url", "")

    # Tailor summary
    tech_summary_mention = ", ".join(job_info.get("tech_stack", [])[:3])
    base_summary = profile.get("profile_summary", "")
    tailored_summary = f"{base_summary} Tailored for {company}'s focus on {tech_summary_mention}."

    # Sort projects by relevance to job tech stack
    projects = list(profile.get("verified_projects", []))

    def project_score(p):
        score = 0
        p_tech = [t.lower() for t in p.get("technologies", [])]
        for t in tech_stack:
            if any(t in pt for pt in p_tech):
                score += 2
        return score

    projects.sort(key=project_score, reverse=True)

    projects_html = ""
    for p in projects[:3]:
        techs = ", ".join(p.get("technologies", []))
        projects_html += f"""
        <div class="item">
          <div class="item-header">
            <strong>{p.get('name')}</strong> &middot; <span class="badge">{techs}</span>
          </div>
          <p class="desc">{p.get('description')} &bull; <strong>Impact:</strong> {p.get('impact')}</p>
        </div>"""

    # Work experience
    exp_html = ""
    for exp in profile.get("work_experience", []):
        bullets = "".join([f"<li>{r}</li>" for r in exp.get("responsibilities", [])])
        exp_html += f"""
        <div class="item">
          <div class="item-header">
            <strong>{exp.get('position')}</strong> &mdash; <em>{exp.get('company')}</em> ({exp.get('locality')})
            <span class="date">{exp.get('period')}</span>
          </div>
          <ul class="bullets">
            {bullets}
          </ul>
        </div>"""

    # Education
    edu_html = ""
    for edu in profile.get("education", []):
        pillars = ""
        if edu.get("module_pillars"):
            pillars = f"<p class='desc'><strong>Focus Pillars:</strong> {', '.join(edu.get('module_pillars'))}</p>"
        edu_html += f"""
        <div class="item">
          <div class="item-header">
            <strong>{edu.get('degree')}</strong> &mdash; <em>{edu.get('institution')}</em>
            <span class="date">{edu.get('year')}</span>
          </div>
          {pillars}
        </div>"""

    # Skills
    skills = profile.get("skills", {})
    all_skills = []
    for cat, items in skills.items():
        if isinstance(items, list):
            all_skills.extend(items)
    skills_badges = "".join([f"<span class='skill-pill'>{s}</span>" for s in all_skills[:18]])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Resume - {full_name} ({company})</title>
  <style>
    @page {{
      size: A4;
      margin: 12mm 15mm 12mm 15mm;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
      line-height: 1.45;
      font-size: 9.5pt;
      padding: 15px;
      background: #fff;
    }}
    .header {{
      border-bottom: 2px solid #0284c7;
      padding-bottom: 10px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}
    .name {{ font-size: 20pt; font-weight: 800; color: #0f172a; line-height: 1.1; }}
    .title {{ font-size: 11pt; font-weight: 600; color: #0284c7; margin-top: 2px; }}
    .contact {{ font-size: 8.5pt; color: #475569; text-align: right; line-height: 1.4; }}
    .contact a {{ color: #0284c7; text-decoration: none; }}
    h3 {{
      font-size: 10.5pt;
      font-weight: 700;
      color: #0f172a;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #cbd5e1;
      padding-bottom: 3px;
      margin: 10px 0 6px 0;
    }}
    .item {{ margin-bottom: 8px; }}
    .item-header {{ font-size: 9.5pt; display: flex; justify-content: space-between; margin-bottom: 2px; }}
    .date {{ font-size: 8.5pt; color: #64748b; font-weight: 600; }}
    .desc {{ font-size: 9pt; color: #334155; }}
    .bullets {{ list-style-type: square; margin-left: 18px; font-size: 8.8pt; color: #334155; }}
    .bullets li {{ margin-bottom: 2px; }}
    .skill-container {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; }}
    .skill-pill {{
      background: #f1f5f9;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 8pt;
      font-weight: 600;
      color: #0f172a;
    }}
    .badge {{
      font-size: 7.5pt;
      background: #e0f2fe;
      color: #0284c7;
      padding: 1px 5px;
      border-radius: 3px;
      font-weight: 600;
    }}
    @media print {{
      body {{ padding: 0; }}
    }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="name">{full_name}</div>
      <div class="title">{profile.get('title', 'Senior Systems Engineer')}</div>
    </div>
    <div class="contact">
      <div>{location} &bull; {phone}</div>
      <div><a href="mailto:{email}">{email}</a></div>
      <div>{f'<a href="{linkedin_url}">LinkedIn</a> &bull; ' if linkedin_url else ''}{f'<a href="{github_url}">GitHub</a>' if github_url else ''}</div>
    </div>
  </div>

  <h3>Professional Summary</h3>
  <p class="desc" style="margin-bottom: 8px;">{tailored_summary}</p>

  <h3>Target Alignment: {company} ({title})</h3>
  <div class="skill-container" style="margin-bottom: 8px;">
    {skills_badges}
  </div>

  <h3>Relevant Work Experience</h3>
  {exp_html}

  <h3>Key Engineered Systems & Projects</h3>
  {projects_html}

  <h3>Education & Specialized Training</h3>
  {edu_html}
</body>
</html>"""

    html_file = RESUMES_DIR / f"resume_{jid}.html"
    pdf_file = RESUMES_DIR / f"resume_{jid}.pdf"

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
    res = generate_tailored_resume({
        "id": "test-job",
        "title": "Senior AI Systems Engineer",
        "company": "DeepTech GmbH",
        "tech_stack": ["Python", "PyTorch", "Docker"]
    })
    print(f"Generated Resume: {res['html_url']}")
