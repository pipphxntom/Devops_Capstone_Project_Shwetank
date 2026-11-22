# Capstone DevOps Project Capstone Report

**Student:** Shwetank Pandey  
**Programme:** B.Tech Computer Science & Engineering (Data Science)  
**Year:** 2026  

## 1. Problem

Teams still treat deployment as a manual, high-risk event. Even small services need a repeatable path from commit to production with visibility and a safe way to reverse a bad release.

## 2. Approach

Build a thin incident tracker and wrap it in a full delivery system:

- Automated quality and security gates in CI
- Immutable container image
- Declarative infrastructure (Terraform)
- Kubernetes with probes and autoscaling
- Blue-green cutover as the progressive delivery mechanism
- Prometheus for basic telemetry

## 3. Implementation notes

- **Application**: Flask + SQLite, JSON logs, Prometheus client. Health endpoints used by both Docker and Kubernetes probes.
- **Container**: Multi-stage, non-root UID 10002, HEALTHCHECK.
- **CI**: Four-stage GitHub Actions workflow. Bandit and Trivy run but do not fail the build (common student choice for demo environments).
- **Kubernetes**: Blue is the live track. Green is prepared in parallel. Service selector is patched to move traffic.
- **HPA**: Targets the blue deployment at 60 % CPU.

## 4. Verification

- Unit tests cover dashboard, probes, create/list, and metrics endpoint.
- Local stack runs with `docker compose up`.
- Manifests pass kubeconform.
- Blue-green switch is a one-line bash command.

## 5. Limitations & next steps

- SQLite is not production storage; real system would use Postgres.
- No real image registry push (demo only).
- No GitOps controller (Argo CD / Flux) — manifests are applied manually or via CI.
- Blue-green still requires coordination; a traffic-management layer (Istio, Linkerd, or simple nginx) would make the cutover cleaner.

## 6. Conclusion

The project shows a working, end-to-end delivery pipeline for a small stateful service. The design choices (blue-green, non-root container, structured logs, HPA) are deliberate and documented so the system can be explained and extended.
