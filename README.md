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

Stack with JHipster Online on . 

This stack include:
 - JHipster 8.8.0. for generate Spring Boot 3.4.1 projects. 
 - generator-jhipster-quarkus 3.4.0 for generate Quarkus 3.11.1 projects.
 - JDL Studio for add JDL files by PR on your repo.

OAuth GitHub configure
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/sing-repo.PNG" width="900" title="Run On Openshift">
</p>

JDL Studio

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

Try on Red Hat OpenShift Dev Spaces, search "JHipster Online" and see the source.
<p align="left">
<img src="https://raw.githubusercontent.com/maximilianoPizarro/jhipster-online-helm-chart/refs/heads/main/image/try-source.PNG" width="900" title="Run On Openshift">
</p>


# Installation

## Charts Values Parameters


## Add repository

```bash
helm repo add jhipster-online https://maximilianopizarro.github.io/jhipster-online-helm-chart/
```

## Install Chart with parameters

```bash
helm install jhipster-online jhipster-online/jhipster-online 
```

```bash
Example:
helm install jhipster-online jhipster-online/jhipster-online --version 0.1.0
```


## Uninstall Chart

```bash
helm uninstall jhipster-online
```

## Package Info

- [GitHub Page](https://maximilianopizarro.github.io/jhipster-online-helm-chart/)
- [GitHub Repo](https://github.com/maximilianoPizarro/jhipster-online-helm-chart)

## Package Steps

```bash
helm package -u . -d charts
helm repo index .
```