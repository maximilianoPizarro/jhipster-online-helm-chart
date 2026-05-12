#!/usr/bin/env python3
"""
Render static architecture PNGs for the Helm chart README / Artifact Hub.

For AI-generated artwork, set GEMINI_API_KEY and run nanobanana (see image/README.md),
then overwrite these files.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "image"


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in ("Segoe UI", "Arial", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius: int, fill, outline=None, width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def draw_architecture() -> None:
    w, h = 1200, 720
    img = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(img)
    title = _font(28)
    body = _font(18)
    small = _font(15)

    draw.text((40, 24), "JHipster Online on OpenShift — deployment topology", fill="#0f172a", font=title)
    draw.text(
        (40, 64),
        "Chart 1.1.0 · App 2.40.1 · Quay: 2.40.1-quarkus / 2.40.1-spring-boot",
        fill="#475569",
        font=small,
    )

    ns = (40, 110, w - 40, h - 40)
    _rounded_rect(draw, ns, 16, fill="#ffffff", outline="#94a3b8", width=2)
    draw.text((60, 125), "OpenShift Namespace", fill="#0f172a", font=body)

    boxes = [
        (80, 170, 520, 320, "#dbeafe", "Deployment: jhipster-online", "Spring Boot · :8080\n/management/health · /api/*"),
        (540, 170, 880, 320, "#e0e7ff", "Sidecar: jdl-studio", "nginx · :8081\n/jdl-studio/"),
        (80, 360, 520, 520, "#dcfce7", "Service + Route", "ClusterIP :8080\nTLS edge Route"),
        (540, 360, 880, 520, "#fef3c7", "ConfigMap nginx-conf", "Proxy /jdl-studio → :8081"),
        (80, 540, 520, 660, "#fce7f3", "MariaDB", "jdbc:mariadb://mariadb:3306"),
        (540, 540, 1080, 660, "#cffafe", "sandbox-shared-models (KServe/vLLM)", "Granite / Nemotron / Qwen\n:8443/v1/chat/completions"),
    ]
    for x0, y0, x1, y1, color, head, sub in boxes:
        _rounded_rect(draw, (x0, y0, x1, y1), 12, fill=color, outline="#64748b", width=1)
        draw.text((x0 + 16, y0 + 14), head, fill="#0f172a", font=body)
        draw.multiline_text((x0 + 16, y0 + 44), sub, fill="#334155", font=small, spacing=4)

    draw.line([(300, 320), (300, 360)], fill="#64748b", width=2)
    draw.line([(710, 320), (710, 360)], fill="#64748b", width=2)
    draw.polygon([(295, 360), (305, 360), (300, 370)], fill="#64748b")

    out = OUT / "architecture-diagram.png"
    img.save(out, "PNG", optimize=True)
    print("Wrote", out)


def draw_rag_flow() -> None:
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(img)
    title = _font(26)
    body = _font(17)
    small = _font(14)

    draw.text((40, 22), "JDL AI assistant — RAG and inference flow", fill="#0f172a", font=title)
    draw.text(
        (40, 58),
        "Lexical RAG (default) + optional semantic RAG (embeddings) · OpenAI-compatible APIs",
        fill="#475569",
        font=small,
    )

    steps = [
        (60, 110, 220, 200, "#e0f2fe", "1. User prompt", "Design Entities UI"),
        (260, 110, 460, 200, "#ede9fe", "2. RAG retrieve", "rag-chunks.json\nlexical / + semantic"),
        (500, 110, 720, 200, "#fef9c3", "3. System prompt", "Chunks + instructions"),
        (760, 110, 980, 200, "#ffedd5", "4. Completions", "POST …/v1/chat/completions"),
        (1020, 110, 1140, 200, "#dcfce7", "5. JDL draft", "Response to UI"),
        (260, 240, 460, 330, "#fae8ff", "Embeddings (opt.)", "POST …/v1/embeddings"),
        (500, 280, 720, 370, "#fee2e2", "Health: jdlAi", "/management/health"),
    ]
    for x0, y0, x1, y1, color, head, sub in steps:
        _rounded_rect(draw, (x0, y0, x1, y1), 12, fill=color, outline="#64748b", width=1)
        draw.text((x0 + 12, y0 + 12), head, fill="#0f172a", font=body)
        draw.multiline_text((x0 + 12, y0 + 42), sub, fill="#334155", font=small, spacing=3)

    for (x1, y1, x2, y2) in [(220, 155, 260, 155), (460, 155, 500, 155), (720, 155, 760, 155), (980, 155, 1020, 155)]:
        draw.line([(x1, y1), (x2, y2)], fill="#64748b", width=2)
        draw.polygon([(x2 - 6, y2 - 4), (x2, y2), (x2 - 6, y2 + 4)], fill="#64748b")

    draw.line([(360, 200), (360, 240)], fill="#64748b", width=2)
    draw.polygon([(355, 240), (365, 240), (360, 250)], fill="#64748b")

    draw.text((60, 400), "Env keys (chart): APPLICATION_JDL_AI_* — RAG_ENABLED, RAG_SEMANTIC_ENABLED, EMBEDDINGS_URL, CONNECT_TIMEOUT_MS, READ_TIMEOUT_MS", fill="#334155", font=small)
    draw.text((60, 430), "Regenerate with nanobanana when GEMINI_API_KEY is set (see image/README.md).", fill="#64748b", font=small)

    out = OUT / "ai-rag-flow.png"
    img.save(out, "PNG", optimize=True)
    print("Wrote", out)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    draw_architecture()
    draw_rag_flow()


if __name__ == "__main__":
    main()
