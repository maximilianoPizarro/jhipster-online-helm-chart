# Deploy JHipster Online Helm Charts on Red Hat OpenShift
<link rel="icon" href="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/main/favicon-152.ico" type="image/x-icon" >
<p align="left">
<img src="https://img.shields.io/badge/redhat-CC0000?style=for-the-badge&logo=redhat&logoColor=white" alt="Redhat">
<img src="https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white" alt="kubernetes">
<img src="https://img.shields.io/badge/helm-0db7ed?style=for-the-badge&logo=helm&logoColor=white" alt="Helm">
<img src="https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white" alt="shell">
<a href="https://www.linkedin.com/in/maximiliano-gregorio-pizarro-consultor-it"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="linkedin" /></a>
<a href="https://artifacthub.io/packages/search?repo=jhipster-online"><img src="https://img.shields.io/endpoint?url=https://artifacthub.io/badge/repository/jhipster-online" alt="Artifact Hub" /></a>
</p>

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/capture.PNG" width="900" title="Run On Openshift">
</p>

Stack with JHipster Online on Red Hat OpenShift.

This stack includes:

- **JHipster Online 2.40.0** with **generator-jhipster 9.0.0** (Spring Boot generation) and **generator-jhipster-quarkus 3.6.0** (Quarkus generation).
- **JDL Studio** for adding JDL files by PR on your repo.

### Container image tags (2.40.0+)

Runtime images are published as **versioned tags** on `quay.io/maximilianopizarro/jhipster-online`:

| Mode        | `values.yaml` `image.tag`   |
|-------------|-----------------------------|
| Quarkus     | `2.40.0-quarkus` (default)    |
| Spring Boot | `2.40.0-spring-boot`          |

Set `env.JAVA_APP_JAR` to `jhonline-2.40.0.war` to match the WAR inside these images.

Chart **1.0.0** aligns with JHipster Online **appVersion 2.40.0**. Chart **0.1.0** remains available for older deployments.


## JDL Studio

<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/jdl-studio.PNG" width="900" title="Run On Openshift">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model.PNG" width="900" title="Run On Openshift">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model-2.PNG" width="900" title="Run On Openshift">
</p>
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/JDL-Model-3.PNG" width="900" title="Run On Openshift">
</p>


# Installation

## Charts Values Parameters

## OAuth GitHub configure
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/sing-repo.PNG" width="900" title="Run On Openshift">
</p>

Go to https://github.com/settings/developers to generate new OAuth App for this configuration:

```bash
-->values.yaml
...
  APPLICATION_GITHUB_HOST: https://github.com
  APPLICATION_GITHUB_CLIENT-ID: CLIENT-ID
  APPLICATION_GITHUB_CLIENT-SECRET: CLIENT-SECRET
...
```

##  Select JHipster Spring Boot or JHipster Quarkus mode generator

- JHipster Quarkus (by default)

```bash
-->values.yaml
...
  APPLICATION_JHIPSTER-CMD_CMD: jhipster-quarkus
  OPENSHIFT_TEKTON_URL-PIPELINE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/jhipster-pipeline-quarkus.yaml"
...
```

- JHipster Spring Boot 

```bash
-->values.yaml
...
  APPLICATION_JHIPSTER-CMD_CMD: jhipster
  OPENSHIFT_TEKTON_URL-PIPELINE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/jhipster-pipeline.yaml"
...
```

## Developer Hub and DevSpaces configuration for your repo

```bash
-->values.yaml
...
  OPENSHIFT_DEVSPACE_URL-DEVFILE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/jhipster-devspaces.yaml"
  OPENSHIFT_BACKSTAGE_URL-BACKSTAGE: "https://raw.githubusercontent.com/redhat-developer-demos/jhipster-online/main/src/main/kubernetes/catalog-info.yaml"
...
```

## Red Hat Developer Sandbox (local Helm chart)

From the root directory of this Helm chart (where `Chart.yaml` is located):

```bash
oc login --token=... --server=https://api.sandbox...openshift.com:6443
oc project <your-dev-namespace>

# Edit values-openshift-sandbox.example.yaml: set APPLICATION_JDL_AI_API_KEY (e.g. oc whoami -t),
# route.host (optional), and GitHub OAuth secrets.

helm upgrade --install jhipster-online . -n <your-dev-namespace> \
  -f values.yaml -f values-openshift-sandbox.example.yaml
```

- **In-cluster OpenShift deploy**: the overlay sets `OPENSHIFT_DEPLOYMENT_ENABLED=true` and `openshift.grantEditRoleToServiceAccount=true`, which installs a **RoleBinding** to the built-in **ClusterRole `edit`** for the same ServiceAccount the Deployment uses (typically `default`). That removes manual `oc policy add-role-to-user edit ...` for **Deploy to OpenShift** from the UI.
- **JDL AI**: the overlay sets `APPLICATION_JDL_AI_*` for inference in `sandbox-shared-models` (TLS trust via `APPLICATION_JDL_AI_INSECURE_TLS=true`). Replace `REPLACE_WITH_OC_WHOAMI_TOKEN` before installing. Do **not** combine `SPRING_PROFILES_ACTIVE=prod` with the public Quay image unless you have verified that image on the cluster (known fabric8 skew); prefer an image built from your namespace (ImageStream).
- **Kuadrant** (optional): set `kuadrant.enabled: true` and fill `kuadrant.gateway` in `values.yaml` (or the overlay). This chart renders an `HTTPRoute`, a `RateLimitPolicy`, and an `AuthPolicy` only when `kuadrant.keycloakIssuerUri` is non-empty. On many Sandbox clusters Kuadrant is not installed; leave `kuadrant.enabled` false and use the OpenShift `Route` only.

## Add repository

```bash
helm repo add jhipster-online https://maximilianopizarro.github.io/jhipster-online-helm-chart/
```

## Install Chart with parameters

**JHipster Online 2.40.0 (recommended):**

```bash
helm install jhipster-online jhipster-online/jhipster-online --version 1.0.0 -f values.yaml -n <your-namespace>
```

**Legacy chart (2.33.0 app):**

```bash
helm install jhipster-online jhipster-online/jhipster-online --version 0.1.0 -f values.yaml -n <your-namespace>
```

Example (current release):

```bash
helm install jhipster-online jhipster-online/jhipster-online --version 1.0.0 -f values.yaml -n maximilianopizarro5-dev
```

NOTE.
jhipster-online name is mandatory, not use my-jhipster-online sample name. 
If you use other name change the configmap ngnix and rollout deployment jhipster-online.

```bash
...
    location /jdl-studio/ {
      proxy_pass http://jhipster-online:8081/;   <-- update by the name set instance
      proxy_set_header X-Forwarded-For $remote_addr;
      proxy_set_header Host $host;
    }
...    
```

## Uninstall Chart

```bash
helm uninstall jhipster-online -n <your-namespace>
```

## Package Steps

```bash
helm package -u . -d charts
helm repo index .
```

## Package Info

- [GitHub Page](https://maximilianopizarro.github.io/jhipster-online-helm-chart/)
- [GitHub Source Repo](https://github.com/redhat-developer-demos/jhipster-online)

Try on Red Hat OpenShift Dev Spaces, search by "JHipster Online" on the sample catalog and launch the code.
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/try-source.PNG" width="900" title="Run On Openshift">
</p>

[![Open](https://img.shields.io/static/v1?label=Open%20in&message=Developer%20Sandbox&logo=eclipseche&color=FDB940&labelColor=525C86)](https://workspaces.openshift.com/#https://github.com/redhat-developer-demos/jhipster-online)



# Build Here. Go Anywhere.

<img src="https://raw.githubusercontent.com/redhat-developer-demos/.github/main/profile/redhat-developer-logo.jpg" width="350">

Join Red Hat Developer for product trails, hands-on learning, tools, technologies, and community.

#### <a href="https://developers.redhat.com/" style="color: #e00">JOIN NOW</a>


