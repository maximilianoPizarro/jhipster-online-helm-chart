# Chart images

Screenshots (`*.PNG`) are used in the main README.

## Architecture diagrams (`architecture-diagram.png`, `ai-rag-flow.png`)

The repo ships **PNG diagrams** for Artifact Hub and GitHub rendering.

### Option A — Nanobanana (Gemini image)

1. Install: `npm install -g @factory/nanobanana`
2. Export `GEMINI_API_KEY` (Google AI Studio).
3. Run from repo root:

```bash
nanobanana diagram "JHipster Online on OpenShift: Spring Boot app and jdl-studio nginx sidecar in one Deployment, MariaDB, Route TLS, ConfigMap nginx proxy, KServe vLLM models in sandbox-shared-models" --type=architecture --style=professional --complexity=detailed

nanobanana diagram "JDL AI: user prompt, lexical and optional semantic RAG from rag-chunks.json, system prompt, OpenAI-compatible chat completions to vLLM, JDL response, health jdlAi" --type=flowchart --style=technical --complexity=detailed
```

4. Copy files from `nanobanana-output/` (or the tool’s output dir) to `image/architecture-diagram.png` and `image/ai-rag-flow.png`.

### Option B — Local render (no API key)

```bash
python scripts/render_diagrams.py
```

This overwrites the two PNGs with blueprint-style placeholders.
