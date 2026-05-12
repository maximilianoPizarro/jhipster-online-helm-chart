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
  - [Red Hat Developer Sandbox (local chart)](#red-hat-developer-sandbox-local-chart)
- [Configuration](#configuration)
  - [Generator Mode (Quarkus / Spring Boot)](#generator-mode-quarkus--spring-boot)
  - [GitHub OAuth](#github-oauth)
  - [Developer Hub and Dev Spaces](#developer-hub-and-dev-spaces)
  - [JDL AI Assistant (OpenShift AI Models)](#jdl-ai-assistant-openshift-ai-models)
  - [OpenShift Route and Kuadrant](#openshift-route-and-kuadrant)
  - [RBAC for In-Cluster Deploy](#rbac-for-in-cluster-deploy)
- [Values Reference](#values-reference)
- [JDL Studio](#jdl-studio)
- [Packaging](#packaging)
- [Links](#links)

---

## Overview

This Helm chart deploys **JHipster Online 2.40.0** on Red Hat OpenShift. The stack includes:

- **JHipster Online 2.40.0** — web UI for generating JHipster applications without local installation
- **generator-jhipster 9.0.0** — generates Spring Boot 3.4+ / Java 21 projects
- **generator-jhipster-quarkus 3.6.0** — generates Quarkus projects
- **JDL Studio** — visual editor for JHipster Domain Language models (sidecar on port 8081)
- **JDL AI Assistant** — AI-assisted JDL drafting with RAG, powered by in-cluster vLLM models (Granite, Nemotron, Qwen)
- **MariaDB** — database for user data, JDL models, and statistics

Source application: [redhat-developer-demos/jhipster-online](https://github.com/redhat-developer-demos/jhipster-online)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        OpenShift Namespace                          │
│                                                                     │
│  ┌─────────────────────────────────────────────┐   ┌─────────────┐ │
│  │         Deployment: jhipster-online          │   │  MariaDB    │ │
│  │                                              │   │  Deployment │ │
│  │  ┌──────────────────┐  ┌──────────────────┐ │   │             │ │
│  │  │  jhipster-online │  │   jdl-studio     │ │   │  Port 3306  │ │
│  │  │  (Spring Boot)   │  │   (nginx)        │ │   └──────┬──────┘ │
│  │  │                  │  │                  │ │          │        │
│  │  │  Port 8080       │  │  Port 8081       │ │   jdbc://mariadb  │
│  │  │  /management/    │  │  /jdl-studio/    │ │          │        │
│  │  │  /api/*          │  │                  │ │          │        │
│  │  └────────┬─────────┘  └──────────────────┘ │          │        │
│  │           │                                  │          │        │
│  └───────────┼──────────────────────────────────┘          │        │
│              │                                             │        │
│  ┌───────────▼───────┐    ┌────────────────────┐          │        │
│  │  Service (8080)   │    │   ConfigMap:       │          │        │
│  │  + Route (TLS)    │    │   nginx-conf       │          │        │
│  └───────────────────┘    │   (proxy 8081→app) │          │        │
│                            └────────────────────┘          │        │
│                                                            │        │
│  ┌─────────────────────────────────────────────────────────┘        │
│  │  sandbox-shared-models (KServe / vLLM)                          │
│  │  ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐        │
│  │  │ Granite 3.1  │ │ Nemotron Nano 9B │ │   Qwen 3 8B  │        │
│  │  │   8B FP8     │ │    v2 FP8        │ │     FP8      │        │
│  │  │  :8443/v1/   │ │   :8443/v1/      │ │  :8443/v1/   │        │
│  │  └──────────────┘ └──────────────────┘ └──────────────┘        │
│  └─────────────────────────────────────────────────────────        │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Component | Image | Port | Purpose |
|-----------|-------|------|---------|
| jhipster-online | `quay.io/maximilianopizarro/jhipster-online:2.40.0-quarkus` | 8080 | Spring Boot app — generation, Git push, Fabric8 deploy, JDL AI |
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
| `2.40.0-quarkus` (default) | `Dockerfile.quarkus` | UBI8 OpenJDK 17 + Maven 3.9.15 + Node 20 | generator-jhipster 9.0.0 + generator-jhipster-quarkus 3.6.0 |
| `2.40.0-spring-boot` | `Dockerfile.spring-boot` | UBI8 OpenJDK 17 + Maven 3.9.15 + Node 20 | generator-jhipster 9.0.0 |

**Registry**: `quay.io/maximilianopizarro/jhipster-online`

Set `image.tag` in `values.yaml` and match `env.JAVA_APP_JAR` to `jhonline-2.40.0.war`.

Unversioned tags (`:quarkus`, `:spring-boot`, `:latest`) remain pinned to 2.33.0 to avoid breaking existing deployments.

---

## Chart Versions

| Chart Version | App Version | Key Changes |
|---------------|-------------|-------------|
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
  --version 1.0.4 -n <your-namespace>

# With AI models token
helm install jhipster-online jhipster-online/jhipster-online \
  --version 1.0.4 -n <your-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

> **Note**: The release name `jhipster-online` is mandatory. Using a different name requires updating the nginx ConfigMap proxy target and restarting the deployment.

### Red Hat Developer Sandbox (local chart)

```bash
# Login
oc login --token=... --server=https://api.sandbox...openshift.com:6443

# Install from local chart directory with AI models enabled
helm upgrade --install jhipster-online . -n <your-dev-namespace> \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

- **In-cluster deploy**: Set `openshift.grantEditRoleToServiceAccount=true` to create a RoleBinding granting `edit` to the pod's ServiceAccount.
- **JDL AI**: All three sandbox models (Granite, Nemotron, Qwen) are enabled by default with `APPLICATION_JDL_AI_INSECURE_TLS=true` for in-cluster TLS.

### Uninstall

```bash
helm uninstall jhipster-online -n <your-namespace>
```

---

## Configuration

### Generator Mode (Quarkus / Spring Boot)

**Quarkus** (default):

```yaml
# values.yaml
env:
  APPLICATION_JHIPSTER-CMD_CMD: jhipster-quarkus
  OPENSHIFT_TEKTON_URL-PIPELINE: "https://raw.githubusercontent.com/.../jhipster-pipeline-quarkus.yaml"
image:
  tag: "2.40.0-quarkus"
```

**Spring Boot**:

```yaml
# values.yaml
env:
  APPLICATION_JHIPSTER-CMD_CMD: jhipster
  OPENSHIFT_TEKTON_URL-PIPELINE: "https://raw.githubusercontent.com/.../jhipster-pipeline.yaml"
image:
  tag: "2.40.0-spring-boot"
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

```yaml
env:
  OPENSHIFT_DEVSPACE_URL-DEVFILE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/jhipster-devspaces.yaml"
  OPENSHIFT_BACKSTAGE_URL-BACKSTAGE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/catalog-info.yaml"
```

### JDL AI Assistant (OpenShift AI Models)

The **Design Entities** page includes an AI-assisted JDL draft panel when configured. It uses an OpenAI-compatible `/v1/chat/completions` endpoint with **lexical RAG** over curated JDL reference chunks.

#### Available Models (Developer Sandbox)

| Model | ID | vLLM Model ID | Context Length |
|-------|-----|---------------|----------------|
| IBM Granite 3.1 8B Instruct | `granite-31-8b` | `isvc-granite-31-8b-fp8` | 65536 |
| NVIDIA Nemotron Nano 9B v2 | `nemotron-nano-9b` | `isvc-nemotron-nano-9b-v2-fp8` | 65536 |
| Qwen 3 8B | `qwen3-8b` | `isvc-qwen3-8b-fp8` | 40960 |

All models are served via **KServe + RHAIIS (vLLM)** in the `sandbox-shared-models` namespace with FP8 quantization.

#### Configuration (values.yaml)

```yaml
env:
  APPLICATION_JDL_AI_ENABLED: "true"
  APPLICATION_JDL_AI_INSECURE_TLS: "true"
  APPLICATION_JDL_AI_DEFAULT_MODEL_ID: granite-31-8b
  APPLICATION_JDL_AI_RAG_ENABLED: "true"
  APPLICATION_JDL_AI_RAG_TOP_K: "6"
  APPLICATION_JDL_AI_RAG_MAX_CHARS: "14000"
  # Model 0
  APPLICATION_JDL_AI_MODELS_0_ID: granite-31-8b
  APPLICATION_JDL_AI_MODELS_0_LABEL: "IBM Granite 3.1 8B Instruct (FP8)"
  APPLICATION_JDL_AI_MODELS_0_MODEL: isvc-granite-31-8b-fp8
  APPLICATION_JDL_AI_MODELS_0_API_URL: "https://isvc-granite-31-8b-fp8-predictor.sandbox-shared-models.svc.cluster.local:8443/v1/chat/completions"
  # ... (models 1 and 2 follow the same pattern)
```

#### Authentication

The models require a Bearer token. Pass it at install time:

```bash
helm upgrade --install jhipster-online . \
  --set-string "env.APPLICATION_JDL_AI_API_KEY=$(oc whoami -t)"
```

For full documentation, see the [JDL AI assistant section](https://github.com/redhat-developer-demos/jhipster-online#optional-jdl-ai-assistant-openshift--sandbox-models) in the application README.

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

When the JHipster Online UI deploys applications directly to the cluster (Fabric8), the pod's ServiceAccount needs `edit` permissions:

```yaml
openshift:
  grantEditRoleToServiceAccount: true
```

This creates a RoleBinding granting the built-in `edit` ClusterRole to the ServiceAccount used by the Deployment.

---

## Values Reference

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `replicaCount` | int | `1` | Number of replicas |
| `image.repository` | string | `quay.io/maximilianopizarro/jhipster-online` | Container image registry |
| `image.tag` | string | `2.40.0-quarkus` | Image tag |
| `image.pullPolicy` | string | `IfNotPresent` | Pull policy |
| `service.type` | string | `ClusterIP` | Service type |
| `service.port` | int | `8080` | Service port |
| `route.enabled` | bool | `true` | Create OpenShift Route |
| `ingress.enabled` | bool | `false` | Create Ingress |
| `autoscaling.enabled` | bool | `false` | Enable HPA |
| `openshift.grantEditRoleToServiceAccount` | bool | `false` | Bind `edit` role to pod SA |
| `kuadrant.enabled` | bool | `false` | Enable Kuadrant policies |
| `env.APPLICATION_JDL_AI_ENABLED` | string | `"true"` | Enable JDL AI assistant |
| `env.APPLICATION_JDL_AI_DEFAULT_MODEL_ID` | string | `granite-31-8b` | Default AI model |
| `env.APPLICATION_JDL_AI_API_KEY` | string | `""` | Bearer token for model auth |
| `env.APPLICATION_JDL_AI_RAG_ENABLED` | string | `"true"` | Enable RAG context |

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

```bash
# Package chart
helm package -u . -d charts

# Regenerate index
helm repo index . --url https://maximilianopizarro.github.io/jhipster-online-helm-chart/ --merge index.yaml
```

---

## Links

- [Helm Chart Repository (GitHub Pages)](https://maximilianopizarro.github.io/jhipster-online-helm-chart/)
- [Application Source Code](https://github.com/redhat-developer-demos/jhipster-online)
- [Artifact Hub](https://artifacthub.io/packages/helm/jhipster-online/jhipster-online)
- [Container Images (Quay.io)](https://quay.io/repository/maximilianopizarro/jhipster-online)
- [Architecture Spec](https://github.com/redhat-developer-demos/jhipster-online/blob/main/ARCHITECTURE.md)
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
