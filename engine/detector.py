#!/usr/bin/env python3
"""
detector.py - Config-Driven Editorial Quality & Voice Detector.
Scores post copy across 5 quality checks:
1. Sentence Burstiness & Rhythm
2. Technical Specificity (latency, VRAM, numbers, licenses)
3. Buzzword / Slop Density (from config.json)
4. AI Fingerprint Elimination
5. Voice Tells (em-dash prohibition, sandboxing disclaimers)
"""

import os
import re
import math
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_EXAMPLE = BASE_DIR / "config.json.example"


def load_voice_rules():
    target = CONFIG_FILE if CONFIG_FILE.exists() else CONFIG_EXAMPLE
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("voice_rules", {})
        except Exception:
            pass
    return {
        "forbid_em_dashes": True,
        "forbidden_buzzwords": [
            "delve", "leverage", "game-changer", "revolutionary", "seamless"
        ]
    }


def calc_burstiness(text):
    sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if len(s.strip()) > 0]
    if len(sentences) <= 1:
        return 50.0
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean if mean > 0 else 0
    return round(min(100.0, cv * 120.0), 1)


def calc_specificity(text):
    tokens = text.split()
    if not tokens:
        return 0.0

    specific_patterns = [
        r'\d+(\.\d+)?k?',
        r'\$\d+|\€\d+',
        r'\b(v\d+\.\d+|python|docker|gpu|vram|ram|api|mit|apache|llm|ollama|vllm|github|claude|gemini|openai)\b',
        r'\b[a-zA-Z0-9_-]+\.(py|json|md|txt|ts|js)\b',
        r'https?://',
        r'%',
        r'\b(tested|untested|benchmark|repo|commit|license|heuristic|script|workflow)\b'
    ]

    spec_count = 0
    for pat in specific_patterns:
        spec_count += len(re.findall(pat, text, re.IGNORECASE))

    ratio = (spec_count / len(tokens)) * 100.0
    return round(min(100.0, ratio * 6.0), 1)


def calc_slop_density(text, rules=None):
    if rules is None:
        rules = load_voice_rules()
    words = text.split()
    if not words:
        return 100.0, 0

    forbidden = rules.get("forbidden_buzzwords", [])
    slop_count = 0
    for w in forbidden:
        slop_count += len(re.findall(r'\b' + re.escape(w) + r'\b', text, re.IGNORECASE))

    per_100 = (slop_count / len(words)) * 100.0
    return round(max(0.0, 100.0 - (per_100 * 25.0)), 1), slop_count


def calc_fingerprint(text):
    score = 100.0
    # Penalty for typical LLM structure tells
    if re.search(r'\b(in summary|in conclusion|moreover|furthermore|testament to)\b', text, re.IGNORECASE):
        score -= 20.0
    if re.search(r'\b(crucial|pivotal|paramount)\b', text, re.IGNORECASE):
        score -= 15.0
    return max(0.0, score)


def calc_voice_and_tells(text, rules=None):
    if rules is None:
        rules = load_voice_rules()
    score = 100.0
    issues = []

    # Em-dash check
    if rules.get("forbid_em_dashes", True) and "—" in text:
        score -= 30.0
        issues.append("Contains forbidden em-dash ('—') character")

    # Generic engagement bait check
    lower = text.strip().lower()
    if lower.endswith("thoughts?") or lower.endswith("agree?") or lower.endswith("what do you think?"):
        score -= 35.0
        issues.append("Contains generic engagement bait ending")

    # Sandboxing disclaimer check for agent/execution posts
    if any(k in lower for k in ["agent", "code execution", "browser automation"]):
        if not any(s in lower for s in ["sandbox", "docker", "credentials", "security"]):
            score -= 25.0
            issues.append("Discusses agent execution without sandboxing/security warning")

    # Tested vs untested declaration check
    if any(k in lower for k in ["repo", "tool", "framework", "model"]):
        if not any(t in lower for t in ["tested", "haven't run", "based on", "inspection"]):
            score -= 20.0
            issues.append("Missing tested vs untested empirical disclosure")

    return max(0.0, round(score, 1)), issues


def score_draft(text):
    rules = load_voice_rules()
    b = calc_burstiness(text)
    s = calc_specificity(text)
    sl, sl_cnt = calc_slop_density(text, rules)
    fp = calc_fingerprint(text)
    v, issues = calc_voice_and_tells(text, rules)

    total = round(b * 0.2 + s * 0.2 + sl * 0.2 + fp * 0.2 + v * 0.2, 1)
    return {
        "total_score": total,
        "is_approved": total >= 80.0,
        "metrics": {
            "burstiness": b,
            "specificity": s,
            "slop_score": sl,
            "fingerprint": fp,
            "voice_score": v
        },
        "issues": issues
    }

