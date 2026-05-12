# JHipster Online Helm Chart for Red Hat OpenShift

<link rel="icon" href="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/main/favicon-152.ico" type="image/x-icon" >
<p align="left">
<img src="https://img.shields.io/badge/redhat-CC0000?style=for-the-badge&logo=redhat&logoColor=white" alt="Redhat">
<img src="https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white" alt="kubernetes">
<img src="https://img.shields.io/badge/helm-0db7ed?style=for-the-badge&logo=helm&logoColor=white" alt="Helm">
<img src="https://img.shields.io/badge/quay.io-40B4E5?style=for-the-badge&logo=redhat&logoColor=white" alt="Quay">
<img src="https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white" alt="shell">
<a href="https://www.linkedin.com/in/maximiliano-gregorio-pizarro-consultor-it"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="linkedin" /></a>
<a href="https://artifacthub.io/packages/search?repo=jhipster-online"><img src="https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/jhipster-online" alt="Artifact Hub" /></a>
</p>

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/capture.PNG" width="900" title="Run On Openshift">
</p>

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Container Images](#container-images)
- [Chart Versions](#chart-versions)
- [Installation](#installation)
  - [From Helm Repository](#from-helm-repository)
  - [Red Hat Developer Sandbox](#red-hat-developer-sandbox)
- [Configuration](#configuration)
  - [Startup console, JVM, and resources](#startup-console-jvm-and-resources)
  - [Generator Mode (Quarkus / Spring Boot)](#generator-mode-quarkus--spring-boot)
  - [GitHub OAuth](#github-oauth)
  - [Developer Hub and Dev Spaces](#developer-hub-and-dev-spaces)
  - [JDL AI Assistant (OpenShift AI Models)](#jdl-ai-assistant-openshift-ai-models)
  - [OpenShift Route and Kuadrant](#openshift-route-and-kuadrant)
  - [RBAC for In-Cluster Deploy](#rbac-for-in-cluster-deploy)
- [Security Considerations](#security-considerations)
- [Values Reference](#values-reference)
- [JDL Studio](#jdl-studio)
- [Packaging](#packaging)
- [Links](#links)

---

## Overview

This Helm chart deploys **JHipster Online 2.40.1** on Red Hat OpenShift. The stack includes:

- **JHipster Online 2.40.1** — web UI for generating JHipster applications without local installation
- **generator-jhipster 9.0.0** — generates Spring Boot 3.4+ / Java 21 projects
- **generator-jhipster-quarkus 3.6.0** — generates Quarkus projects
- **JDL Studio** — visual editor for JHipster Domain Language models (sidecar on port 8081)
- **JDL AI Assistant** — AI-assisted JDL drafting with RAG, powered by in-cluster vLLM models (Granite, Nemotron, Qwen)
- **MariaDB** — database for user data, JDL models, and statistics
- **Cluster requirement** — Kubernetes **≥ 1.25** (OpenShift **4.12+**); see `kubeVersion` in [Chart.yaml](Chart.yaml).
- **Developer Sandbox defaults** — a single [values.yaml](values.yaml): Route on, RBAC `edit` for the pod ServiceAccount, in-cluster deploy enabled, JDL AI URLs for `sandbox-shared-models`; set `env.APPLICATION_JDL_AI_API_KEY` at install (e.g. `oc whoami -t`). For other clusters, turn those off in the same file (see [RBAC for In-Cluster Deploy](#rbac-for-in-cluster-deploy)).
- **Runtime image (upstream)** — [redhat-developer-demos/jhipster-online](https://github.com/redhat-developer-demos/jhipster-online) `Dockerfile.quarkus` / `Dockerfile.spring-boot`: **UBI8 OpenJDK 21**, **Node 22.19**, **Maven 3.9.15**, WAR at `/deployments/jhonline.war`.

Source application: [redhat-developer-demos/jhipster-online](https://github.com/redhat-developer-demos/jhipster-online)

---

## Architecture

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/main/image/architecture-diagram.png" width="900" alt="JHipster Online on OpenShift — deployment topology (diagram)">
</p>

> Diagram source: [nanobanana](https://www.npmjs.com/package/@factory/nanobanana) (Gemini) or local script — see [image/README.md](image/README.md). Regenerate with `GEMINI_API_KEY` or run `python scripts/render_diagrams.py` from the repo root.

### Component Summary

| Component | Image | Port | Purpose |
|-----------|-------|------|---------|
| jhipster-online | `quay.io/maximilianopizarro/jhipster-online:2.40.1-quarkus` | 8080 | Spring Boot app — generation, Git push, Fabric8 deploy, JDL AI |
| jdl-studio | `quay.io/maximilianopizarro/jdl-studio` | 8081 | nginx sidecar serving JDL Studio UI |
| mariadb | `registry.redhat.io/rhel8/mariadb-103` | 3306 | Persistent database |
| AI models | KServe InferenceServices in `sandbox-shared-models` | 8443 | vLLM OpenAI-compatible endpoints |

### Deployment Topology

The chart creates the following OpenShift resources:

| Resource | Name | Condition |
|----------|------|-----------|
| Deployment | `jhipster-online` (2 containers) | Always |
| Deployment | `mariadb` | Always |
| Service | `jhipster-online` (8080) | Always |
| ConfigMap | `nginx-conf` | Always |
| Route | `jhipster-online` (TLS edge) | `route.enabled=true` |
| ServiceAccount | per fullname | `serviceAccount.create=true` |
| HPA | per fullname | `autoscaling.enabled=true` |
| Ingress | per fullname | `ingress.enabled=true` |
| RoleBinding | `edit` for SA | `openshift.grantEditRoleToServiceAccount=true` |
| HTTPRoute + RateLimitPolicy + AuthPolicy | per fullname | `kuadrant.enabled=true` |

---

## Container Images

Runtime images are published via GitHub Actions to **Quay.io**:

| Tag | Dockerfile | Base | Generators |
|-----|-----------|------|------------|
| `2.40.1-quarkus` (default) | [`Dockerfile.quarkus`](https://github.com/redhat-developer-demos/jhipster-online/blob/main/Dockerfile.quarkus) | UBI8 **OpenJDK 21** + Maven 3.9.15 + **Node 22.19** | generator-jhipster 9.0.0 + generator-jhipster-quarkus 3.6.0 |
| `2.40.1-spring-boot` | [`Dockerfile.spring-boot`](https://github.com/redhat-developer-demos/jhipster-online/blob/main/Dockerfile.spring-boot) | UBI8 **OpenJDK 21** + Maven 3.9.15 + **Node 22.19** | generator-jhipster 9.0.0 |

**Registry**: `quay.io/maximilianopizarro/jhipster-online`

Set `image.tag` in `values.yaml` and match `env.JAVA_APP_JAR` to the WAR path baked into that image (default: `/deployments/jhonline.war`).

Unversioned tags (`:quarkus`, `:spring-boot`, `:latest`) remain pinned to 2.33.0 to avoid breaking existing deployments.

---

## Chart Versions

| Chart Version | App Version | Key Changes |
|---------------|-------------|-------------|
| **1.1.0** | 2.40.1 | Quay `2.40.1-*` images (JDK **21**, **Node 22.19**, Maven 3.9.15 per upstream Dockerfiles); `JAVA_APP_JAR=/deployments/jhonline.war`; `image.pullPolicy` **Always**; `JAVA_OPTS_APPEND` UTF-8 + `MaxRAMPercentage`; **defaults centralized in `values.yaml` for Developer Sandbox** (Route, RBAC `edit`, `OPENSHIFT_DEPLOYMENT_ENABLED`, Sandbox-sized `resources`, shared-model JDL AI URLs); upstream `application-prod.yml` alignment: `APPLICATION_HELM_TEMPLATE_*`, `OPENSHIFT_DEPLOYMENT_*` Helm/Fabric8; no separate overlay file |
| **1.0.4** | 2.40.0 | JDL AI assistant with 3 sandbox models, startupProbe, jdl-studio probes, Kuadrant policies, RBAC RoleBinding |
| 1.0.0 | 2.40.0 | Initial chart for JHipster Online 2.40.0 with JHipster 9 generators |
| 0.1.0 | 2.33.0 | Legacy chart for JHipster Online 2.33.0 |

---

## Installation

### From Helm Repository

```bash
# Add repository
helm repo add jhipster-online https://maximilianopizarro.github.io/jhipster-online-helm-chart/

# Install (latest)
helm install jhipster-online jhipster-online/jhipster-online \
  --version 1.1.0 -n <your-namespace>

# With AI models token
helm install jhipster-online jhipster-online/jhipster-online \
  --version 1.1.0 -n <your-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

> **Note**: The release name `jhipster-online` is mandatory. Using a different name requires updating the nginx ConfigMap proxy target and restarting the deployment.

### Red Hat Developer Sandbox

[values.yaml](values.yaml) is written for a **first try on Red Hat Developer Sandbox**: OpenShift Route, `openshift.grantEditRoleToServiceAccount: true`, `env.OPENSHIFT_DEPLOYMENT_ENABLED: "true"`, CPU/memory limits suited to Sandbox quotas, and JDL AI model URLs under `sandbox-shared-models`. You only need a cluster token for inference.

**From this repository (recommended for Sandbox):**

```bash
oc login --token=... --server=https://api.sandbox...openshift.com:6443

helm upgrade --install jhipster-online . -n <your-dev-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

**From the Helm repository** (same packaged defaults; no extra `-f`):

```bash
oc project <your-dev-namespace>

helm repo update
helm upgrade --install jhipster-online jhipster-online/jhipster-online \
  --version 1.1.0 -n <your-dev-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

Set GitHub OAuth with `--set-string` for `env.APPLICATION_GITHUB_CLIENT-ID` and `env.APPLICATION_GITHUB_CLIENT-SECRET` (or a small secret values file). Watch rollout: `oc rollout status deployment/jhipster-online -n <your-dev-namespace>`.

**Outside Sandbox** (tighter security or no in-cluster deploy): in the same `values.yaml` (or overrides via `--set`), set `openshift.grantEditRoleToServiceAccount: false`, `env.OPENSHIFT_DEPLOYMENT_ENABLED: "false"`, and adjust `resources` / model URLs as needed.

- **JDL AI**: three models in `sandbox-shared-models` and `APPLICATION_JDL_AI_INSECURE_TLS=true` by default.
- **Same image tag, new digest**: with `image.pullPolicy: Always` (default), run `oc rollout restart deployment/jhipster-online -n <ns>` after the registry is updated.

### Uninstall

```bash
helm uninstall jhipster-online -n <your-namespace>
```

---

## Configuration

### Startup console, JVM, and resources

The **JHipster ASCII banner** stays enabled by default (Spring Boot default). The chart does **not** set `SPRING_MAIN_BANNER_MODE=off`. To make startup output easier to read in OpenShift (encoding + heap inside the cgroup) the chart sets:

| Mechanism | Default in chart | Purpose |
|-----------|------------------|---------|
| `JAVA_OPTS_APPEND` | UTF-8 system properties + `-XX:MaxRAMPercentage=72.0` | Cleaner multi-byte output and JVM heap sized to the container memory limit (UBI OpenJDK [run script](https://catalog.redhat.com/en/software/containers/ubi8/openjdk-21)). |
| `resources` | requests `768Mi` / `100m`, limits `1536Mi` / `1` CPU | Sized for Developer Sandbox; set `resources: {}` to unset or raise for production |
| `LOGGING_PATTERN_CONSOLE` | single-line pattern | Structured plain-text lines after the banner. |

Optional Spring Boot tuning via `env` (only if you need it):

```yaml
env:
  # Example: disable banner in log aggregators only (not the default in this chart)
  # SPRING_MAIN_BANNER_MODE: "off"
  # SPRING_OUTPUT_ANSI_ENABLED: "never"   # strip ANSI in captured logs
```

### Generator Mode (Quarkus / Spring Boot)

The OpenShift generator reads **Tekton pipelines, Devfile, and Helm scaffold templates from the application bundle** (classpath `helm-template/` and related resources in [redhat-developer-demos/jhipster-online](https://github.com/redhat-developer-demos/jhipster-online)). Upstream removed standalone `kubernetes/*.yaml` files that used to be referenced by URL; the chart does **not** set `OPENSHIFT_TEKTON_URL-PIPELINE`, `OPENSHIFT_DEVSPACE_URL-DEVFILE`, or `OPENSHIFT_BACKSTAGE_URL-BACKSTAGE`.

**Quarkus** (default):

```yaml
# values.yaml
env:
  APPLICATION_JHIPSTER-CMD_CMD: jhipster-quarkus
image:
  tag: "2.40.1-quarkus"
```

**Spring Boot**:

```yaml
# values.yaml
env:
  APPLICATION_JHIPSTER-CMD_CMD: jhipster
image:
  tag: "2.40.1-spring-boot"
```

### GitHub OAuth

Go to https://github.com/settings/developers to create an OAuth App:

```yaml
env:
  APPLICATION_GITHUB_HOST: https://github.com
  APPLICATION_GITHUB_CLIENT-ID: <your-client-id>
  APPLICATION_GITHUB_CLIENT-SECRET: <your-client-secret>
```

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/sing-repo.PNG" width="900" title="GitHub OAuth">
</p>

### Developer Hub and Dev Spaces

**Dev Spaces / Devfile**: the Devfile content used when generating OpenShift projects is **bundled with the application**, not loaded from a `raw.githubusercontent.com` URL.

**Backstage / Developer Hub**: if you register the service in a Backstage catalog, you can still point at the upstream **catalog entity** file in the repo: [catalog-info.yaml](https://github.com/redhat-developer-demos/jhipster-online/blob/main/src/main/kubernetes/catalog-info.yaml) (`src/main/kubernetes/catalog-info.yaml`). That is optional catalog metadata only; it is separate from the generator’s embedded templates.

### Packaged chart repository and OpenShift Helm deploy

Upstream [application-prod.yml](https://github.com/redhat-developer-demos/jhipster-online/blob/main/src/main/resources/config/application-prod.yml) exposes Spring properties that map to these chart defaults in `values.yaml`:

| Env variable | Default | Purpose |
|--------------|---------|---------|
| `APPLICATION_HELM_TEMPLATE_PACKAGE_CHART_REPOSITORY_ON_GENERATE` | `true` | After rendering the generated app’s `helm/` chart, run `helm package` and `helm repo index` so `chart-repository/` (`.tgz` + `index.yaml`) can be published (e.g. GitHub Pages). Requires the **helm** CLI on the JHipster Online image if you leave this enabled. |
| `APPLICATION_HELM_TEMPLATE_CHART_REPOSITORY_INDEX_BASE_URL` | *(empty)* | Optional `helm repo index --url` base; when empty the app uses its GitHub Pages convention. |
| `APPLICATION_HELM_TEMPLATE_HELM_BINARY` | `helm` | Binary used for packaging (separate from OpenShift deploy below). |
| `OPENSHIFT_DEPLOYMENT_USE_HELM_CLI` | `true` | When `OPENSHIFT_DEPLOYMENT_ENABLED=true`, prefer `helm upgrade --install` for in-cluster installs. |
| `OPENSHIFT_DEPLOYMENT_HELM_BINARY` | `helm` | Helm binary for deploy operations. |
| `OPENSHIFT_DEPLOYMENT_HELM_TIMEOUT_SECONDS` | `600` | Timeout passed to Helm. |
| `OPENSHIFT_DEPLOYMENT_HELM_FALLBACK_TO_FABRIC8` | `true` | If Helm CLI deploy fails, fall back to Fabric8 client apply. |

Set `OPENSHIFT_DEPLOYMENT_USE_HELM_CLI` to `false` if your runtime image has no Helm CLI and you rely on Fabric8 only (matches upstream `application-dev.yml` default).

### JDL AI Assistant (OpenShift AI Models)

The **Design Entities** page shows an **AI-assisted JDL draft** panel when `APPLICATION_JDL_AI_ENABLED=true` and at least one OpenAI-compatible completions URL is configured. The backend calls `POST .../v1/chat/completions` (vLLM, KServe, Ollama, OpenAI, etc.).

**RAG (retrieval)**:

- **Lexical** (default): keyword/token overlap over bundled chunks in `rag-chunks.json` from the application image.
- **Semantic** (optional): embeddings + cosine similarity when `APPLICATION_JDL_AI_RAG_SEMANTIC_ENABLED=true` and `APPLICATION_JDL_AI_EMBEDDINGS_URL` points to `POST .../v1/embeddings`. On failure, the app falls back to lexical ranking.

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/main/image/ai-rag-flow.png" width="900" alt="JDL AI RAG and inference flow (diagram)">
</p>

> Regenerate with nanobanana: `nanobanana diagram "RAG pipeline for JDL AI…" --type=flowchart` then save as `image/ai-rag-flow.png`.

#### Available Models (Developer Sandbox)

| Model | ID | vLLM Model ID | Context Length |
|-------|-----|---------------|----------------|
| IBM Granite 3.1 8B | `granite-31-8b` | `isvc-granite-31-8b-fp8` | 65536 |
| NVIDIA Nemotron Nano 9B v2 | `nemotron-nano-9b-v2` | `isvc-nemotron-nano-9b-v2-fp8` | 65536 |
| Qwen3 8B | `qwen3-8b` | `isvc-qwen3-8b-fp8` | 40960 |

All models are served via **KServe + RHAIIS (vLLM)** in the `sandbox-shared-models` namespace with FP8 quantization.

#### Quick start (Helm)

```bash
helm upgrade --install jhipster-online jhipster-online/jhipster-online \
  --version 1.1.0 -n <your-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

#### Full configuration reference (environment variables)

Spring maps dotted YAML to env with underscores and uppercase; the chart uses the `APPLICATION_JDL_AI_*` keys below.

| Env variable | Default in chart | Purpose |
|--------------|------------------|---------|
| `APPLICATION_JDL_AI_ENABLED` | `true` | Feature gate (assistant visible only if enabled **and** a completions URL exists). |
| `APPLICATION_JDL_AI_INSECURE_TLS` | `true` | Trust self-signed / cluster TLS for upstream HTTP clients (typical on Sandbox). Use `false` with proper CA bundles in production. |
| `APPLICATION_JDL_AI_DEFAULT_MODEL_ID` | `granite-31-8b` | Default entry in the UI model picker when `models[]` is configured. |
| `APPLICATION_JDL_AI_API_KEY` | *(empty)* | `Authorization: Bearer …` for chat **and** embeddings. Prefer `--set-string` or a Secret — never commit tokens. |
| `APPLICATION_JDL_AI_RAG_ENABLED` | `true` | Lexical RAG on/off. |
| `APPLICATION_JDL_AI_RAG_TOP_K` | `6` | Number of chunks to inject. |
| `APPLICATION_JDL_AI_RAG_MAX_CHARS` | `14000` | Character budget for RAG context in the system prompt. |
| `APPLICATION_JDL_AI_RAG_SEMANTIC_ENABLED` | `false` | When `true`, rank chunks with embeddings + cosine similarity (requires embeddings URL). |
| `APPLICATION_JDL_AI_EMBEDDINGS_URL` | *(empty)* | OpenAI-compatible `POST .../v1/embeddings` URL (required for semantic RAG). |
| `APPLICATION_JDL_AI_EMBEDDINGS_MODEL` | `text-embedding-3-small` | Model id in the embeddings JSON body. |
| `APPLICATION_JDL_AI_CONNECT_TIMEOUT_MS` | `15000` | Connect timeout to completions/embeddings upstream. |
| `APPLICATION_JDL_AI_READ_TIMEOUT_MS` | `120000` | Read timeout for long generations. |
| `APPLICATION_JDL_AI_HELP_TEXT` | *(see values.yaml)* | Hint shown under the assistant card in the UI. |
| `APPLICATION_JDL_AI_MODELS_*_{ID,LABEL,MODEL,API_URL}` | *(3 models)* | Multi-model picker; index `0`, `1`, `2` in env names as in `values.yaml`. |

For property names in YAML (e.g. `application.jdl-ai.rag-semantic-enabled`), see the [application README — JDL AI assistant](https://github.com/redhat-developer-demos/jhipster-online#jdl-ai-assistant-models-rag-embeddings).

#### Multi-model `values.yaml` example

```yaml
env:
  APPLICATION_JDL_AI_ENABLED: "true"
  APPLICATION_JDL_AI_INSECURE_TLS: "true"
  APPLICATION_JDL_AI_DEFAULT_MODEL_ID: granite-31-8b
  APPLICATION_JDL_AI_RAG_ENABLED: "true"
  APPLICATION_JDL_AI_RAG_TOP_K: "6"
  APPLICATION_JDL_AI_RAG_MAX_CHARS: "14000"
  APPLICATION_JDL_AI_RAG_SEMANTIC_ENABLED: "false"
  APPLICATION_JDL_AI_EMBEDDINGS_URL: ""
  APPLICATION_JDL_AI_EMBEDDINGS_MODEL: "text-embedding-3-small"
  APPLICATION_JDL_AI_CONNECT_TIMEOUT_MS: "15000"
  APPLICATION_JDL_AI_READ_TIMEOUT_MS: "120000"
  APPLICATION_JDL_AI_MODELS_0_ID: granite-31-8b
  APPLICATION_JDL_AI_MODELS_0_LABEL: "IBM Granite 3.1 8B (FP8)"
  APPLICATION_JDL_AI_MODELS_0_MODEL: isvc-granite-31-8b-fp8
  APPLICATION_JDL_AI_MODELS_0_API_URL: "https://isvc-granite-31-8b-fp8-predictor.sandbox-shared-models.svc.cluster.local:8443/v1/chat/completions"
  APPLICATION_JDL_AI_MODELS_1_ID: nemotron-nano-9b-v2
  APPLICATION_JDL_AI_MODELS_1_LABEL: "NVIDIA Nemotron Nano 9B v2 (FP8)"
  APPLICATION_JDL_AI_MODELS_1_MODEL: isvc-nemotron-nano-9b-v2-fp8
  APPLICATION_JDL_AI_MODELS_1_API_URL: "https://isvc-nemotron-nano-9b-v2-fp8-predictor.sandbox-shared-models.svc.cluster.local:8443/v1/chat/completions"
  APPLICATION_JDL_AI_MODELS_2_ID: qwen3-8b
  APPLICATION_JDL_AI_MODELS_2_LABEL: "Qwen3 8B (FP8)"
  APPLICATION_JDL_AI_MODELS_2_MODEL: isvc-qwen3-8b-fp8
  APPLICATION_JDL_AI_MODELS_2_API_URL: "https://isvc-qwen3-8b-fp8-predictor.sandbox-shared-models.svc.cluster.local:8443/v1/chat/completions"
  APPLICATION_JDL_AI_API_KEY: ""   # set at install with --set-string or External Secrets
```

#### Single-model / external endpoint (Ollama, OpenAI, route on cluster)

Use either one global URL (via Spring `application.jdl-ai.api-url` / matching env in your image) or a single `APPLICATION_JDL_AI_MODELS_0_*` entry. Example pattern for a single route:

```yaml
env:
  APPLICATION_JDL_AI_ENABLED: "true"
  APPLICATION_JDL_AI_DEFAULT_MODEL_ID: my-model
  APPLICATION_JDL_AI_MODELS_0_ID: my-model
  APPLICATION_JDL_AI_MODELS_0_LABEL: "My vLLM"
  APPLICATION_JDL_AI_MODELS_0_MODEL: my-serving-knative-name
  APPLICATION_JDL_AI_MODELS_0_API_URL: "https://my-model-predictor-my-ns.apps.example.com/v1/chat/completions"
```

#### Authentication and secrets

| Approach | When to use |
|----------|----------------|
| `helm --set-string env.APPLICATION_JDL_AI_API_KEY=…` | Quick Sandbox demos (`oc whoami -t`). |
| Kubernetes `Secret` + `envFrom` / workload patch | Production; rotate token without editing Helm values. |
| [External Secrets Operator](https://external-secrets.io/) | Sync from Vault / cloud secret manager; no plaintext in Git. |

Never store long-lived API keys in Git. Treat `APPLICATION_JDL_AI_API_KEY` like any other credential.

#### Semantic RAG example

```yaml
env:
  APPLICATION_JDL_AI_RAG_SEMANTIC_ENABLED: "true"
  APPLICATION_JDL_AI_EMBEDDINGS_URL: "https://your-embeddings-route.apps.example.com/v1/embeddings"
  APPLICATION_JDL_AI_EMBEDDINGS_MODEL: "text-embedding-3-small"
```

#### Health monitoring

Actuator **`GET /management/health`** includes a **`jdlAi`** component: whether a completions URL is configured and the feature is wired. Use the existing chart readiness probe on `/management/health` to surface a not-ready pod if health aggregation is configured accordingly, or scrape the JSON for dashboards.

#### REST API (application)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/jdl-ai/config` | Enabled flag, help text, RAG options, default model id, model list. |
| POST | `/api/jdl-ai/generate` | Body: `{ "prompt": "…", "modelId": "…" }` — returns JDL draft or 502/503 on misconfiguration / upstream errors. |

#### Troubleshooting

| Symptom | Things to check |
|---------|------------------|
| Assistant missing in UI | `APPLICATION_JDL_AI_ENABLED`, at least one model URL, image version supports JDL AI. |
| 401/403 from model route | `APPLICATION_JDL_AI_API_KEY`, token expiry, SAR for `sandbox-shared-models`. |
| TLS / handshake errors | `APPLICATION_JDL_AI_INSECURE_TLS=true` only if appropriate; prefer proper CA trust in prod. |
| Timeouts on long prompts | Raise `APPLICATION_JDL_AI_READ_TIMEOUT_MS`. |
| Semantic RAG does nothing | `APPLICATION_JDL_AI_EMBEDDINGS_URL` set, `RAG_SEMANTIC_ENABLED=true`, embedding model compatible. |

For full upstream documentation, see [JDL AI assistant (models, RAG, embeddings)](https://github.com/redhat-developer-demos/jhipster-online#jdl-ai-assistant-models-rag-embeddings) in the application README.

### OpenShift Route and Kuadrant

**Route** is enabled by default (`route.enabled: true`). For Kuadrant Gateway API integration:

```yaml
kuadrant:
  enabled: true
  gateway:
    name: my-gateway
    namespace: gateway-ns
    sectionName: https
  httpRouteHostname: "jhipster.apps.example.com"
  keycloakIssuerUri: "https://keycloak-.../realms/jhipster"  # enables AuthPolicy
```

### RBAC for In-Cluster Deploy

By default **`openshift.grantEditRoleToServiceAccount: true`** and **`env.OPENSHIFT_DEPLOYMENT_ENABLED: "true"`** so the JHipster Online UI can deploy generated apps on Developer Sandbox. The chart creates a RoleBinding granting the built-in `edit` ClusterRole to the ServiceAccount used by the Deployment.

To **disable** in-cluster deploy or use a narrower role elsewhere:

```yaml
openshift:
  grantEditRoleToServiceAccount: false
env:
  OPENSHIFT_DEPLOYMENT_ENABLED: "false"
```

> **Least privilege:** Prefer a dedicated ServiceAccount and the minimal `Role` / `ClusterRole` from [`src/main/kubernetes/rbac.yaml`](https://github.com/redhat-developer-demos/jhipster-online/blob/main/src/main/kubernetes/rbac.yaml) (`jhipster-online-deployer`) instead of namespace-wide `edit` when your cluster policy allows it.

---

## Security Considerations

### JWT signing (`jhipster.security.authentication.jwt`)

JHipster Online uses JWT for API security. In production:

- Configure `jhipster.security.authentication.jwt.base64-secret` (or key store) via **environment variables or mounted secrets**, not committed YAML.
- Plan **rotation** (new key + staged rollout); document who owns secrets (Vault, OpenShift secrets, ESO).

### HTTPS

Terminate TLS at the OpenShift Route / Ingress or an edge proxy. Do not expose plain HTTP for production OAuth callbacks.

### Workload identity for OpenShift deploy

The chart **defaults to granting `edit`** to the pod ServiceAccount for Sandbox try-out. That is broad. Where possible:

1. Create a **dedicated** `ServiceAccount` (`serviceAccount.create: true` + `name`).
2. Bind only the rules required from `rbac.yaml` instead of `edit`.
3. Avoid running as `default` SA in shared namespaces.

### AI credentials

Treat `APPLICATION_JDL_AI_API_KEY` like any cloud API key: short-lived tokens where possible, Secret/ESO injection, and audit access to `sandbox-shared-models`.

---

## Values Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `replicaCount` | int | `1` | Number of replicas |
| `image.repository` | string | `quay.io/maximilianopizarro/jhipster-online` | Container image registry |
| `image.tag` | string | `2.40.1-quarkus` | Image tag |
| `image.pullPolicy` | string | `Always` | Pull policy for the **jhipster-online** container (`imagePullPolicy`); use `IfNotPresent` to reduce pulls if your tag is immutable |
| `service.type` | string | `ClusterIP` | Service type |
| `service.port` | int | `8080` | Service port |
| `route.enabled` | bool | `true` | Create OpenShift Route |
| `ingress.enabled` | bool | `false` | Create Ingress |
| `autoscaling.enabled` | bool | `false` | Enable HPA |
| `openshift.grantEditRoleToServiceAccount` | bool | `true` | Bind `edit` role to pod SA (Sandbox default; set `false` for least privilege) |
| `kuadrant.enabled` | bool | `false` | Enable Kuadrant policies |
| `resources` | object | Sandbox-sized | CPU/memory for the **jhipster-online** container; set `{}` to unset |
| `env.JAVA_APP_JAR` | string | `/deployments/jhonline.war` | WAR path inside the container (must match the image layout) |
| `env.JAVA_OPTS_APPEND` | string | *(UTF-8 + MaxRAMPercentage)* | Extra JVM flags (UBI OpenJDK `run-java.sh`) |
| `env.LOGGING_PATTERN_CONSOLE` | string | *(pattern)* | Log line format (`logging.pattern.console`) |
| `env.OPENSHIFT_DEPLOYMENT_ENABLED` | string | `"true"` | Enable in-cluster deploy from UI (`openshift.deployment.enabled`) |
| `env.APPLICATION_JDL_AI_ENABLED` | string | `"true"` | Enable JDL AI assistant |
| `env.APPLICATION_JDL_AI_DEFAULT_MODEL_ID` | string | `granite-31-8b` | Default AI model |
| `env.APPLICATION_JDL_AI_API_KEY` | string | `""` | Bearer token for model auth |
| `env.APPLICATION_JDL_AI_RAG_ENABLED` | string | `"true"` | Lexical RAG |
| `env.APPLICATION_JDL_AI_RAG_SEMANTIC_ENABLED` | string | `"false"` | Semantic RAG (embeddings) |
| `env.APPLICATION_JDL_AI_EMBEDDINGS_URL` | string | `""` | Embeddings endpoint URL |
| `env.APPLICATION_JDL_AI_EMBEDDINGS_MODEL` | string | `text-embedding-3-small` | Embeddings model id |
| `env.APPLICATION_JDL_AI_CONNECT_TIMEOUT_MS` | string | `"15000"` | Upstream connect timeout |
| `env.APPLICATION_JDL_AI_READ_TIMEOUT_MS` | string | `"120000"` | Upstream read timeout |
| `env.APPLICATION_JDL_AI_INSECURE_TLS` | string | `"true"` | Trust insecure TLS to models (dev/Sandbox) |

---

## JDL Studio

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/jdl-studio.PNG" width="900" title="JDL Studio">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model.PNG" width="900" title="JDL Model">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model-2.PNG" width="900" title="JDL Model 2">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model-3.PNG" width="900" title="JDL Model 3">
</p>

---

## Packaging

To publish on **GitHub Pages** for this chart repo: after packaging, **commit** `charts/jhipster-online-*.tgz` and `index.yaml` together so `helm repo update` picks up the new digest or version.

```bash
# Optional: regenerate README / Artifact Hub diagrams (no API key)
python scripts/render_diagrams.py

# Package chart
helm package -u . -d charts

# Regenerate index (merge keeps older chart entries)
helm repo index . --url https://maximilianopizarro.github.io/jhipster-online-helm-chart/ --merge index.yaml
```

---

## Links

- [Helm Chart Repository (GitHub Pages)](https://maximilianopizarro.github.io/jhipster-online-helm-chart/)
- [Application Source Code](https://github.com/redhat-developer-demos/jhipster-online)
- [Artifact Hub](https://artifacthub.io/packages/helm/jhipster-online/jhipster-online)
- [Container Images (Quay.io)](https://quay.io/repository/maximilianopizarro/jhipster-online)
- [README diagram assets (`image/`)](image/README.md)
- [Release Notes 2.40.0](https://github.com/redhat-developer-demos/jhipster-online/blob/main/RELEASE-NOTES-2.40.0.md)

Try on Red Hat OpenShift Dev Spaces — search "JHipster Online" in the sample catalog:

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/try-source.PNG" width="900" title="Run On Openshift">
</p>

[![Open](https://img.shields.io/static/v1?label=Open%20in&message=Developer%20Sandbox&logo=eclipseche&color=FDB940&labelColor=525C86)](https://workspaces.openshift.com/#https://github.com/redhat-developer-demos/jhipster-online)

---

# Build Here. Go Anywhere.

<img src="https://raw.githubusercontent.com/redhat-developer-demos/.github/main/profile/redhat-developer-logo.jpg" width="350">

Join Red Hat Developer for product trails, hands-on learning, tools, technologies, and community.

#### <a href="https://developers.redhat.com/" style="color: #e00">JOIN NOW</a>
