# Week 13 — Cloud & Container Security

**OWASP 2025:** A02 Security Misconfiguration · **CWE:** CWE-732, CWE-16

## Objectives
- Apply the shared-responsibility model and least privilege (IAM).
- Manage secrets safely; harden container images.
- Find and fix common cloud/container misconfigurations.

## 🔍 Signature game — "Misconfig Hunt" (CloudGoat-style)
Scavenger hunt: each misconfiguration you find **and** fix = a flag.
1. **IAM:** given an over-permissive policy (`*:*`), scope it to least privilege.
2. **Storage:** lock down a publicly-exposed bucket (provided as IaC/localstack).
3. **Secrets:** move secrets out of env/Dockerfile into a secrets manager.
4. **Image hardening:**
```bash
docker run --rm -v "$PWD:/src" aquasec/trivy config /src     # IaC/Dockerfile misconfig
docker run --rm aquasec/trivy image myapp:lab                 # image CVEs
```
Use a minimal/distroless base, drop root, pin versions; re-scan to show fewer findings.

## Deliverable
Before/after policy + Dockerfile + Trivy reports showing reduced risk.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
- https://kubernetes.io/docs/concepts/security/
