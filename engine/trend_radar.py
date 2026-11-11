#!/usr/bin/env python3
"""
trend_radar.py - Technical Breakthrough Scout & Post Synthesizer.
Scouts engineering breakthroughs across AI, Cloud, Distributed Systems, and Modern DevOps.
Synthesizes contrarian, practitioner-grade copy and generates Canva comparison graphics.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine import designer, detector

QUEUE_DIR = BASE_DIR / "queue"
CANDIDATES_DIR = QUEUE_DIR / "candidates"
QUEUE_SUMMARY_FILE = QUEUE_DIR / "queue_summary.json"
CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)


DEFAULT_STARTER_BREAKTHROUGHS = [
    {
        "id": 1,
        "slug": "browser_use",
        "topic": "browser-use (Headless Vision-Web Agents & DOM Token Compression)",
        "beat": "Autonomous Agents & Automation",
        "score": 96,
        "replaces": "Raw HTML Tree Dumps & High-Cost Cloud Headless Scrapers",
        "cost": "$0 / MIT Open Source; cuts multi-turn agent token costs by 85%",
        "test_status": "Tested on local Playwright with Chromium in Docker; not tested on complex multi-factor banking portals yet",
        "catch": "Dynamic SPAs with shadow DOMs, canvas elements, or aggressive Cloudflare Turnstile bot challenges break coordinate-based bounding box detection. Always run browser agents inside headless Docker containers with strict security limits.",
        "post_copy": """Dumping raw HTML trees into an LLM context window to automate a browser is an expensive way to ignore DOM tree geometry.

When engineering teams build autonomous web agents, naive implementations fetch the full document markup and feed 80,000+ tokens into an LLM per page. A single 10-step browser trajectory blows past context windows and costs over $4.00 in cloud API calls, while failing on dynamic JavaScript buttons.

The open-source library browser-use/browser-use solves this using coordinate-based DOM compression:

1. Interactive Node Pruning: Custom JavaScript strips non-interactive elements, script tags, and hidden styles, leaving only clickable buttons, input fields, and links.
2. Visual Coordinate Bounding Boxes: Highlights every interactive element directly on a viewport screenshot with numerical IDs and pixel bounding boxes.
3. Coordinate-Based Multi-Modal Action: The model receives the stripped DOM tree and the annotated screenshot, outputting precise click coordinates (click(element_id=14)) instead of brittle XPath queries.

On paper, it slashes token consumption by 85% while executing dynamic multi-step web workflows.
In practice, there is an engineering catch:

Dynamic Single-Page Applications (SPAs) with shadow DOMs, canvas elements, or aggressive Cloudflare Turnstile bot challenges break bounding box detection. Furthermore, running headless Chromium inside a worker requires at least 2GB of RAM per concurrent browser instance. Always sandbox browser agents inside dedicated Docker containers with strict security limits and egress proxies.

Tested on local Playwright with Chromium in Docker, but haven't run this across hundreds of parallel sessions in Kubernetes yet. For self-hosted browser automation with Python and local vision models, it keeps execution costs at $0.

Full open-source repository: github.com/browser-use/browser-use

#Python #AI #LLM #SoftwareEngineering #OpenSource #DataScience""",
        "primary_sources": """1. GitHub Repository: https://github.com/browser-use/browser-use
2. Documentation: https://docs.browser-use.com
3. Playwright Core Engine: https://playwright.dev/python/docs/intro""",
        "visual_specs": {
            "category_tag": "Autonomous Agents & Web Automation",
            "main_title": "Web Agents: <span class='gradient-text-cyan'>Coordinate Bounding Boxes</span> vs Raw HTML",
            "subtitle": "Why feeding full DOM trees into LLMs burns 80,000 tokens per page and how browser-use fixes it.",
            "left_badge": "Naive HTML Dumps",
            "left_title": "Full DOM Context",
            "left_price": "80k+ Tokens",
            "left_subprice": "Per Web Page Navigation Step",
            "left_points": [
                ("Massive Token Bloat", "Sends 80k+ tokens of raw HTML, scripts, and CSS per turn"),
                ("High Cloud API Bills", "$3 to $5 per multi-turn web browsing trajectory"),
                ("Brittle XPath Breakage", "DOM hierarchy shifts break hardcoded element selectors"),
                ("No Coordinate Awareness", "Model hallucinates button positions on responsive pages")
            ],
            "left_metric": "Cost per 10-Step Run: ❌ $4.50+",
            "right_badge": "browser-use (MIT)",
            "right_title": "Interactive Vision DOM",
            "right_price": "1.2k Tokens",
            "right_subprice": "Numerical Bounding Boxes & Coordinates",
            "right_points": [
                ("85% Token Compression", "Strips non-interactive tags and extracts actionable nodes"),
                ("Annotated Screenshots", "Labels clickable buttons directly on the viewport"),
                ("Native Python API", "Clean async Playwright integration for custom tools"),
                ("Local Vision Compatible", "Runs with open-weight vision models in Docker")
            ],
            "right_metric": "Cost per 10-Step Run: ✓ $0.12 (Local: $0)",
            "specs": [
                ("Token Reduction", "Up to 85% Fewer Context Tokens"),
                ("Browser Engine", "Async Playwright & Chromium"),
                ("License & Cost", "$0 / MIT Open Source")
            ],
            "catch_title": "The Headless RAM Catch",
            "catch_text": "Headless Chromium requires 2GB RAM per concurrent browser process. Shadow DOMs and anti-bot Turnstile gates require proxy rotation and careful timeout handling.",
            "footer_repo": "github.com/browser-use/browser-use",
            "save_filename": "visual_browser_use.png"
        }
    },
    {
        "id": 2,
        "slug": "unsloth",
        "topic": "Unsloth (Fast Open-Weight LLM Fine-Tuning & Custom Triton Kernels)",
        "beat": "AI Models & Efficient Training",
        "score": 95,
        "replaces": "Native PyTorch Autograd & High-Cost Multi-GPU Cloud Clusters",
        "cost": "$0 / Apache 2.0 Open Source; cuts fine-tuning VRAM by up to 80%",
        "test_status": "Tested on Llama-3-8B and Qwen-2.5 on local 24GB RTX 3090; not tested on 70B models across multi-node InfiniBand clusters yet",
        "catch": "Handwritten Triton kernels bypass PyTorch high-level dispatchers. Introducing unsupported custom model architectures falls back to standard autograd and loses acceleration.",
        "post_copy": """Throwing more 80GB A100 GPUs at LLM fine-tuning before profiling activation memory is an expensive way to ignore PyTorch autograd overhead.

When teams train LoRA or QLoRA adapters on open-weight models like Llama-3 or Qwen-2.5, standard PyTorch training scripts allocate enormous intermediate activation tensors during the backward pass. Even with 4-bit quantization, gradient checkpointing and cross-entropy backpropagation frequently trigger CUDA Out-Of-Memory (OOM) errors on commodity 24GB GPUs.

The open-source library unslothai/unsloth addresses this at the GPU hardware layer using handcrafted OpenAI Triton kernels:

1. Fused Attention & Normalization: Combines RoPE position embeddings, QK dot products, and RMSNorm into single GPU passes, avoiding redundant global memory read/write cycles.
2. Manual Cross-Entropy Derivatives: Derives backpropagation math analytically in Triton, eliminating the massive intermediate logit tensors that standard autograd stores in VRAM.
3. Zero Loss in Accuracy: Delivers mathematically exact floating-point outputs with 2x to 5x faster training throughput and up to 80% less peak VRAM.

On paper, you can fine-tune an 8B model with 16k context on a single 16GB-24GB desktop GPU.
In practice, there is an engineering catch:

Handwritten Triton kernels bypass PyTorch high-level dispatchers. If you modify model architecture layers or use custom attention mechanisms not covered by Unsloth kernels, the engine falls back to standard PyTorch autograd, losing the VRAM and speed advantages. Always verify security credentials and base model architecture compatibility before building a fine-tuning pipeline.

Tested on Llama-3-8B and Qwen-2.5 on a local 24GB GPU in Docker, but haven't run 70B distributed runs across InfiniBand clusters yet. For self-hosted model adaptation on single-GPU hardware, it keeps cloud compute budgets at $0.

Full open-source repository: github.com/unslothai/unsloth

#MachineLearning #Python #AI #DataScience #OpenSource #DeepLearning""",
        "primary_sources": """1. GitHub Repository: https://github.com/unslothai/unsloth
2. Architecture Benchmarks: https://unsloth.ai/blog/mistral-benchmark
3. Triton Kernels Reference: https://github.com/openai/triton""",
        "visual_specs": {
            "category_tag": "AI Models & Efficient Training",
            "main_title": "LLM Fine-Tuning: <span class='gradient-text-emerald'>Handcrafted Triton Kernels</span> vs Autograd",
            "subtitle": "Why standard PyTorch backprop triggers CUDA OOM errors on 24GB GPUs and how Unsloth eliminates activation bloat.",
            "left_badge": "Standard PyTorch",
            "left_title": "Native Autograd Engine",
            "left_price": "OOM on 24GB",
            "left_subprice": "Stores Full Intermediate Activation Tensors",
            "left_points": [
                ("Activation Tensor Bloat", "Materializes massive logit matrices during cross-entropy pass"),
                ("Memory Bus Bottleneck", "Excessive GPU DRAM read/write cycles between layers"),
                ("Hardware Cost Tax", "Requires expensive 80GB A100 or H100 cloud instances"),
                ("Slow Epoch Speeds", "Unfused kernels limit overall training throughput")
            ],
            "left_metric": "Hardware Requirement: ❌ 80GB GPU ($3.50/hr)",
            "right_badge": "Unsloth (Apache 2.0)",
            "right_title": "Custom Triton Kernels",
            "right_price": "14 GB VRAM",
            "right_subprice": "Analytical Gradients & Fused Passes",
            "right_points": [
                ("80% VRAM Reduction", "Derives cross-entropy math without large logit tensors"),
                ("2x to 5x Faster Training", "Fused RoPE, RMSNorm, and attention forward/backward"),
                ("Exact Math Fidelity", "Zero loss in precision compared to standard FP16/BF16"),
                ("Commodity GPU Ready", "Fine-tune 8B models locally on a single 16GB-24GB GPU")
            ],
            "right_metric": "Hardware Requirement: ✓ 24GB GPU ($0 Local)",
            "specs": [
                ("Training Speedup", "2x to 5x Faster Throughput"),
                ("VRAM Compression", "Up to 80% Less Peak Memory"),
                ("Kernel Language", "OpenAI Triton & CUDA")
            ],
            "catch_title": "The Architecture Dispatch Catch",
            "catch_text": "Triton kernels target specific architectures (Llama, Qwen, Mistral, Gemma). Custom exotic layers drop back into standard PyTorch autograd, eliminating speed gains.",
            "footer_repo": "github.com/unslothai/unsloth",
            "save_filename": "visual_unsloth.png"
        }
    },
    {
        "id": 3,
        "slug": "fastmcp",
        "topic": "FastMCP (High-Level Python Framework for Model Context Protocol Servers)",
        "beat": "Autonomous Agents & Tool Protocols",
        "score": 95,
        "replaces": "Boilerplate JSON-RPC Protocol Handlers & Proprietary Plugin Frameworks",
        "cost": "$0 / MIT Open Source; eliminates 200+ lines of low-level MCP wire protocol code",
        "test_status": "Tested with Claude Desktop and local Python agent clients in Docker; not tested over enterprise reverse proxies with mTLS yet",
        "catch": "FastMCP simplifies tool exposure via decorators, but long-running tools that block the async event loop stall all concurrent MCP requests. Always offload heavy I/O to background workers.",
        "post_copy": """Writing 250 lines of boilerplate JSON-RPC protocol glue just to let an LLM query an internal SQLite database is an expensive way to ignore developer ergonomics.

When Anthropic released the open Model Context Protocol (MCP) standard, it unified how AI agents connect to local tools, enterprise databases, and development environments. However, the low-level Python SDK requires manual transport negotiation, complex JSON-RPC message schemas, and verbose lifecycle handlers.

The open-source library jlowin/fastmcp solves this with a FastAPI-style decorator interface:

1. Type-Inferred Tool Registration: A single `@mcp.tool()` decorator inspects Python type hints and docstrings to automatically generate valid MCP tool schemas without writing manual JSON schemas.
2. Multiple Transport Modes: Supports stdio for local agent execution (VS Code, Claude Desktop, Antigravity) and Server-Sent Events (SSE) for remote Docker microservices.
3. Native Pydantic Validation: Automatically validates tool arguments before execution, intercepting malformed LLM tool calls before they hit production databases.

On paper, you can build and expose a production tool server in under 15 lines of Python.
In practice, there is a concurrency catch:

FastMCP runs tools inside an asynchronous event loop. If your tool executes a heavy synchronous database query or slow file processing script without using `asyncio.to_thread()`, it blocks the main loop and stalls all concurrent MCP clients. Always inspect tool runtime latency and sandbox execution environments inside dedicated Docker containers.

Tested on local SQLite and REST API tool servers in Docker, but haven't run this across multi-tenant enterprise reverse proxies yet. For building custom agent tools with Python and open standards, it cuts protocol friction to $0.

Full open-source repository: github.com/jlowin/fastmcp

#Python #AI #SoftwareEngineering #OpenSource #DevOps #Docker""",
        "primary_sources": """1. GitHub Repository: https://github.com/jlowin/fastmcp
2. Official MCP Specification: https://modelcontextprotocol.io
3. Architecture Overview: https://github.com/modelcontextprotocol/python-sdk""",
        "visual_specs": {
            "category_tag": "Autonomous Agents & Tool Protocols",
            "main_title": "Agent Tooling: <span class='gradient-text-cyan'>FastMCP Decorators</span> vs Low-Level JSON-RPC",
            "subtitle": "Why writing raw protocol glue for Model Context Protocol is inefficient and how FastMCP streamlines agent tooling.",
            "left_badge": "Raw MCP SDK",
            "left_title": "Manual JSON-RPC",
            "left_price": "250+ Lines",
            "left_subprice": "Verbose Wire Protocol & Schemas",
            "left_points": [
                ("Heavy Boilerplate Tax", "Requires manual transport setup and JSON schema dicts"),
                ("High Maintenance Overhead", "Updating a tool signature requires updating schemas across files"),
                ("Error-Prone Validation", "Silent failures on malformed LLM parameter types"),
                ("Brittle Stdio Piping", "Complex IPC process negotiation across platforms")
            ],
            "left_metric": "Tool Setup: ❌ 250+ Lines Glue Code",
            "right_badge": "FastMCP (MIT)",
            "right_title": "Decorator Architecture",
            "right_price": "15 Lines",
            "right_subprice": "Type-Inferred Pydantic Tools",
            "right_points": [
                ("@mcp.tool() Decorators", "Auto-derives schemas from standard Python type hints"),
                ("Stdio & SSE Transports", "Seamless local CLI and remote Docker microservice modes"),
                ("Pydantic Argument Guard", "Validates input types before execution reaches DB"),
                ("Drop-In Agent Ready", "Instant integration with Claude, VS Code, and IDEs")
            ],
            "right_metric": "Tool Setup: ✓ 15 Lines Clean Code",
            "specs": [
                ("Interface", "Python Type Hints & Decorators"),
                ("Transports", "Stdio + Server-Sent Events (SSE)"),
                ("License & Cost", "$0 / MIT Open Source")
            ],
            "catch_title": "The Async Event Loop Catch",
            "catch_text": "Blocking synchronous code inside @mcp.tool() halts the event loop for all clients. Heavy computation or blocking I/O must run inside asyncio.to_thread().",
            "footer_repo": "github.com/jlowin/fastmcp",
            "save_filename": "visual_fastmcp_sdk.png"
        }
    }
]


def seed_initial_candidates():
    """Generates starter markdown files and graphics for fresh installations."""
    queue_data = {"candidates": [], "updated_at": "", "auto_approve_enabled": True}
    if QUEUE_SUMMARY_FILE.exists():
        try:
            with open(QUEUE_SUMMARY_FILE, "r", encoding="utf-8") as f:
                queue_data = json.load(f)
        except Exception:
            pass

    existing_ids = {c["id"] for c in queue_data.get("candidates", [])}

    for item in DEFAULT_STARTER_BREAKTHROUGHS:
        cid = item["id"]
        slug = item["slug"]
        if cid in existing_ids:
            continue

        # Score with detector
        score_res = detector.score_draft(item["post_copy"])
        quality_score = score_res["total_score"]

        # Render Canva comparison graphic
        specs = item["visual_specs"]
        try:
            designer.generate_comparison_graphic(
                category_tag=specs["category_tag"],
                main_title=specs["main_title"],
                subtitle=specs["subtitle"],
                left_badge=specs["left_badge"],
                left_title=specs["left_title"],
                left_price=specs["left_price"],
                left_subprice=specs["left_subprice"],
                left_points=specs["left_points"],
                left_metric=specs["left_metric"],
                right_badge=specs["right_badge"],
                right_title=specs["right_title"],
                right_price=specs["right_price"],
                right_subprice=specs["right_subprice"],
                right_points=specs["right_points"],
                right_metric=specs["right_metric"],
                specs=specs["specs"],
                catch_title=specs["catch_title"],
                catch_text=specs["catch_text"],
                footer_repo=specs["footer_repo"],
                save_filename=specs["save_filename"]
            )
            vis_path = f"visuals/{specs['save_filename']}"
        except Exception as e:
            print(f"[WARN] Graphic generation skipped ({e})")
            vis_path = ""

        # Write markdown candidate
        md_file = CANDIDATES_DIR / f"candidate_{cid}_{slug}.md"
        md_content = f"""# CANDIDATE {cid}: {item['topic']}
- Status: APPROVED
- Format: Image-Attached (Canva-Style Design)
- Beat: {item['beat']}
- Visual Asset: {vis_path}
- Editorial Score: {item['score']}/100
- Quality Score: {quality_score}/100

---

### COMPLETE LINKEDIN POST

{item['post_copy']}

---

### PRIMARY SOURCES
{item['primary_sources']}

---

### THE CATCH / SKEPTICAL ANGLE
{item['catch']}
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        queue_data.setdefault("candidates", []).append({
            "id": cid,
            "topic": item["topic"],
            "beat": item["beat"],
            "score": item["score"],
            "human_quality_score": quality_score,
            "status": "APPROVED",
            "format": "image-attached",
            "replaces": item["replaces"],
            "cost": item["cost"],
            "test_status": item["test_status"],
            "file": f"queue/candidates/candidate_{cid}_{slug}.md",
            "visual": vis_path
        })

    with open(QUEUE_SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, indent=2)


if __name__ == "__main__":
    seed_initial_candidates()
    print("[OK] Initial starter candidates seeded successfully.")

