#!/usr/bin/env python3
"""
designer.py - White-Label Canva-Style Visual Generator for LinkedIn Growth Engine.
Generates pixel-perfect 1080x1350 PNG editorial graphics using HTML5/CSS3 rendering via Chrome.
Dynamically reads author branding, initials, and headline from config.json.
Zero cliché AI art; looks handcrafted by a senior design lead.
"""

import os
import sys
import json
from pathlib import Path
from html2image import Html2Image

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE = BASE_DIR / "config.json.example"
VISUALS_DIR = BASE_DIR / "visuals"
VISUALS_DIR.mkdir(parents=True, exist_ok=True)


def load_profile_config():
    target = CONFIG_FILE if CONFIG_FILE.exists() else CONFIG_EXAMPLE
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "profile": {
            "full_name": "Technical Author",
            "initials": "TA",
            "headline": "Software Engineer & Systems Architect",
            "location": "Global"
        }
    }


# Initialize html2image renderer at 1080x1350 portrait canvas (LinkedIn 4:5 ratio)
hti = Html2Image(output_path=str(VISUALS_DIR), size=(1080, 1350), custom_flags=['--no-sandbox', '--disable-gpu'])

GLOBAL_STYLES = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  width: 1080px;
  height: 1350px;
  background-color: #080C14;
  background-image: 
    radial-gradient(circle at 85% 12%, rgba(56, 189, 248, 0.12) 0%, transparent 40%),
    radial-gradient(circle at 15% 85%, rgba(99, 102, 241, 0.10) 0%, transparent 45%),
    radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.6) 0%, transparent 100%);
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #F8FAFC;
  padding: 56px 60px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  position: relative;
  -webkit-font-smoothing: antialiased;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: 40px 40px;
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  pointer-events: none;
  z-index: 1;
}

.content-wrapper {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  flex: 1;
  justify-content: space-between;
}

.header-section {
  margin-bottom: 24px;
}

.category-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(56, 189, 248, 0.10);
  border: 1px solid rgba(56, 189, 248, 0.28);
  color: #38BDF8;
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.category-tag .pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #38BDF8;
  box-shadow: 0 0 10px #38BDF8;
}

.main-title {
  font-size: 44px;
  font-weight: 800;
  line-height: 1.15;
  color: #F8FAFC;
  margin-top: 16px;
  letter-spacing: -0.02em;
}

.gradient-text-cyan {
  background: linear-gradient(135deg, #38BDF8 0%, #818CF8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.gradient-text-emerald {
  background: linear-gradient(135deg, #34D399 0%, #38BDF8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  font-size: 20px;
  line-height: 1.5;
  color: #94A3B8;
  margin-top: 12px;
  max-width: 920px;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.10);
  margin-top: 24px;
  z-index: 2;
}

.author-box {
  display: flex;
  align-items: center;
  gap: 14px;
}

.author-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0284C7 0%, #4F46E5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: #FFFFFF;
  border: 2px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.author-name {
  font-size: 18px;
  font-weight: 700;
  color: #F8FAFC;
}

.author-thesis {
  font-size: 14px;
  color: #94A3B8;
  font-weight: 500;
}

.repo-badge {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #38BDF8;
  padding: 8px 18px;
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 600;
}

.comparison-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  flex: 1;
  margin-top: 10px;
}

.compare-card {
  border-radius: 18px;
  padding: 30px 28px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  position: relative;
  overflow: hidden;
}

.card-left {
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.65) 100%);
  border: 1px solid rgba(239, 68, 68, 0.25);
}

.card-right {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
  border: 1px solid rgba(56, 189, 248, 0.45);
  box-shadow: 0 12px 30px rgba(56, 189, 248, 0.12);
}

.card-badge {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}
.badge-red { background: rgba(239, 68, 68, 0.18); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-green { background: rgba(16, 185, 129, 0.18); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }

.card-title {
  font-size: 30px;
  font-weight: 800;
  color: #FFFFFF;
}

.price-container {
  margin: 10px 0 16px 0;
}
.card-price {
  font-size: 44px;
  font-weight: 800;
  line-height: 1;
}
.price-red { color: #EF4444; }
.price-green { color: #10B981; }
.card-subprice {
  font-size: 13px;
  color: #94A3B8;
  font-weight: 600;
  margin-top: 4px;
}

.points-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
}

.card-point {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.point-icon {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 2px;
}
.point-icon-red { background: rgba(239, 68, 68, 0.2); color: #EF4444; }
.point-icon-green { background: rgba(16, 185, 129, 0.2); color: #10B981; }

.point-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.point-text strong {
  font-size: 15px;
  color: #F1F5F9;
  font-weight: 700;
}
.point-text span {
  font-size: 13px;
  color: #94A3B8;
  line-height: 1.35;
}

.card-metric-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 13px;
  font-weight: 700;
}
.metric-red { color: #F87171; }
.metric-green { color: #34D399; }

.spec-strip {
  display: flex;
  gap: 16px;
  margin: 18px 0;
}

.spec-chip {
  flex: 1;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.spec-chip-label {
  font-size: 12px;
  color: #64748B;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.spec-chip-val {
  font-size: 16px;
  color: #F8FAFC;
  font-weight: 700;
}

.catch-banner {
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-left: 4px solid #F59E0B;
  border-radius: 8px;
  padding: 14px 18px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.catch-badge {
  background: #F59E0B;
  color: #080C14;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 4px;
  text-transform: uppercase;
  flex-shrink: 0;
}

.catch-text {
  font-size: 14px;
  color: #FDE68A;
  line-height: 1.4;
  font-weight: 500;
}
"""


def generate_comparison_graphic(
    category_tag,
    main_title,
    subtitle,
    left_badge,
    left_title,
    left_price,
    left_subprice,
    left_points,
    left_metric,
    right_badge,
    right_title,
    right_price,
    right_subprice,
    right_points,
    right_metric,
    specs,
    catch_title,
    catch_text,
    footer_repo,
    save_filename
):
    """Generates comparison graphic with user profile dynamically injected."""
    cfg = load_profile_config()
    profile = cfg.get("profile", {})
    author_name = profile.get("full_name", "Technical Author")
    author_initials = profile.get("initials", author_name[:2].upper())
    author_headline = profile.get("headline", "Systems Architect")

    left_items_html = ""
    for title, desc in left_points:
        left_items_html += f"""
        <div class="card-point">
          <div class="point-icon point-icon-red">&times;</div>
          <div class="point-text">
            <strong>{title}</strong>
            <span>{desc}</span>
          </div>
        </div>
        """

    right_items_html = ""
    for title, desc in right_points:
        right_items_html += f"""
        <div class="card-point">
          <div class="point-icon point-icon-green">&#10003;</div>
          <div class="point-text">
            <strong>{title}</strong>
            <span>{desc}</span>
          </div>
        </div>
        """

    specs_html = ""
    for lbl, val in specs:
        specs_html += f"""
        <div class="spec-chip">
          <div class="spec-chip-label">{lbl}</div>
          <div class="spec-chip-val">{val}</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{GLOBAL_STYLES}
</style>
</head>
<body>
  <div class="grid-overlay"></div>
  <div class="content-wrapper">
    <!-- Header -->
    <div class="header-section">
      <div class="category-tag"><span class="pulse-dot"></span> {category_tag}</div>
      <h1 class="main-title">{main_title}</h1>
      <p class="subtitle">{subtitle}</p>
    </div>

    <!-- Comparison Cards -->
    <div class="comparison-grid">
      <!-- Left Card -->
      <div class="compare-card card-left">
        <div>
          <div class="card-badge badge-red">{left_badge}</div>
          <div class="card-header-group">
            <div class="card-title">{left_title}</div>
            <div class="price-container">
              <div class="card-price price-red">{left_price}</div>
              <div class="card-subprice">{left_subprice}</div>
            </div>
          </div>
          <div class="points-stack">
            {left_items_html}
          </div>
        </div>
        <div class="card-metric-footer metric-red">
          {left_metric}
        </div>
      </div>

      <!-- Right Card -->
      <div class="compare-card card-right">
        <div>
          <div class="card-badge badge-green">{right_badge}</div>
          <div class="card-header-group">
            <div class="card-title">{right_title}</div>
            <div class="price-container">
              <div class="card-price price-green">{right_price}</div>
              <div class="card-subprice">{right_subprice}</div>
            </div>
          </div>
          <div class="points-stack">
            {right_items_html}
          </div>
        </div>
        <div class="card-metric-footer metric-green">
          {right_metric}
        </div>
      </div>
    </div>

    <!-- Specs Row -->
    <div class="spec-strip">
      {specs_html}
    </div>

    <!-- Catch Callout -->
    <div class="catch-banner">
      <div class="catch-badge">{catch_title}</div>
      <div class="catch-text">{catch_text}</div>
    </div>

    <!-- Footer with Dynamic White-Label Profile -->
    <div class="footer">
      <div class="author-box">
        <div class="author-avatar">{author_initials}</div>
        <div class="author-details">
          <div class="author-name">{author_name}</div>
          <div class="author-thesis">{author_headline}</div>
        </div>
      </div>
      <div class="repo-badge">{footer_repo}</div>
    </div>
  </div>
</body>
</html>
"""
    hti.screenshot(html_str=html, save_as=save_filename)
    return VISUALS_DIR / save_filename

