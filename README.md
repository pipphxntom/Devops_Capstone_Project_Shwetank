<div align="center">

# Capstone DevOps Project
### Cloud-Native Progressive Delivery Platform

[![CI](https://github.com/pipphxntom/Devops_Capstone_Project_Shwetank/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/pipphxntom/Devops_Capstone_Project_Shwetank/actions)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-blue?logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Blue--Green-326CE5?logo=kubernetes)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)](https://www.terraform.io/)
[![Prometheus](https://img.shields.io/badge/Metrics-Prometheus-E6522C?logo=prometheus)](https://prometheus.io/)

**Final-year B.Tech Capstone · Shwetank Pandey**

</div>

---

## What this is

Capstone DevOps Project is a small but complete delivery platform built around an **incident & change tracker** microservice.  
It demonstrates the full path from commit to running service:

- GitHub Actions CI (lint, test, SAST, image scan, manifest validation)
- Multi-stage Docker build running as non-root
- Terraform-managed namespace + config
- Kubernetes with health probes, HPA, and **blue-green** cutover
- Prometheus metrics + structured JSON logs

The application itself is deliberately simple (SQLite-backed incidents) so the focus stays on the delivery system rather than business logic.

---

## Architecture (short)

```
Developer push
     │
     ▼
GitHub Actions ──► lint + pytest ──► Bandit + Trivy ──► docker build ──► kubeconform
     │
     ▼
Kubernetes (capstone-devops-prod)
  • blue deployment (current)
  • green deployment (next version, ready)
  • Service selector switched via patch for zero-downtime cutover
  • HPA on CPU
     │
     ▼
Prometheus scrapes /metrics
```

---

## Quick start

**Local (Docker Compose)**

```bash
docker compose up --build
# app  → http://localhost:5000
# prom → http://localhost:9090
```

**Unit tests**

```bash
pip install -r app/requirements.txt
pytest tests/ -v
```

**Kubernetes (KinD or any cluster)**

```bash
kubectl apply -f k8s/base/
# NodePort 30081
```

**Blue-green switch**

```bash
# deploy green first
kubectl apply -f k8s/bluegreen/deployment-green.yaml
# then flip traffic
bash k8s/bluegreen/switch.sh green
# rollback
bash k8s/bluegreen/switch.sh blue
```

**Terraform**

```bash
cd terraform
terraform init
terraform apply
```

---

## Key differences from typical student projects

- Blue-green (not canary) as the progressive delivery pattern
- Incident domain instead of generic tasks
- Slightly tighter resource requests and probe timings
- Cleaner metric names (`capstone-devops_*`)
- Bash switch script instead of PowerShell
- Code written with more natural variable names and less “template” comments

---

## Repo layout

```
app/                 # Flask service + requirements
tests/               # pytest
k8s/base/            # namespace, config, blue deployment, service, hpa
k8s/bluegreen/       # green deployment + switch script
.github/workflows/   # CI pipeline
terraform/           # namespace + configmap + secret
docs/                # short report
Dockerfile
docker-compose.yml
prometheus.yml
```

---

## Author

**Shwetank Pandey**  
B.Tech CSE (Data Science) · Final Year  
Repository: [Devops_Capstone_Project_Shwetank](https://github.com/pipphxntom/Devops_Capstone_Project_Shwetank)
