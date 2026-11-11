#!/usr/bin/env python3
"""
pdf_converter.py - High-Fidelity PDF Generation Engine.
Converts HTML Resumes and Cover Letters to professional printable PDF documents.
Uses Headless Chrome, Chromium, or Edge for 100% pixel-perfect vector rendering.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def find_browser_executable():
    """Finds available Chrome, Chromium, or Edge binary on the system."""
    # 1. PATH search
    for name in ["chrome", "google-chrome", "chromium", "chromium-browser", "msedge"]:
        path = shutil.which(name)
        if path and os.path.exists(path):
            return path

    # 2. Windows standard installation locations
    windows_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe")
    ]
    for p in windows_paths:
        if os.path.exists(p):
            return p

    # 3. Linux standard locations
    linux_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium"
    ]
    for p in linux_paths:
        if os.path.exists(p):
            return p

    return None


def convert_html_to_pdf(html_path, pdf_path=None):
    """
    Converts an HTML file to a clean, printable PDF document.
    html_path: Path or str to source HTML file.
    pdf_path: Optional destination Path or str. Defaults to same name with .pdf extension.
    Returns: Path object to generated PDF.
    """
    html_p = Path(html_path).resolve()
    if not html_p.exists():
        raise FileNotFoundError(f"HTML file not found: {html_p}")

    if pdf_path is None:
        pdf_p = html_p.with_suffix(".pdf")
    else:
        pdf_p = Path(pdf_path).resolve()

    pdf_p.parent.mkdir(parents=True, exist_ok=True)

    browser = find_browser_executable()
    if not browser:
        print(f"[PDF WARNING] No Chrome/Edge browser found. HTML generated at {html_p}, but PDF compilation requires Chrome.")
        return None

    try:
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={str(pdf_p)}",
            str(html_p)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if res.returncode == 0 and pdf_p.exists() and pdf_p.stat().st_size > 500:
            print(f"[PDF ENGINE] Generated PDF via {Path(browser).name}: {pdf_p.name} ({pdf_p.stat().st_size} bytes)")
            return pdf_p
        else:
            print(f"[PDF ERROR] Exit code {res.returncode}: {res.stderr}")
            return None
    except Exception as e:
        print(f"[PDF EXCEPTION] Browser conversion failed: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert_html_to_pdf(sys.argv[1])
    else:
        b = find_browser_executable()
        print(f"Browser detected: {b}")
