---
marp: true
theme: default
paginate: true
header: "Software Security · Week 13"
---

# Week 13
## Cloud & Container Security
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Shared-responsibility model
- IAM & least privilege
- Secrets management
- Container/image hardening
- 🎮 Game: **Misconfig Hunt**

---

## Recap & framing

- Supply chain → what you build with
- Today → where you run it
- **OWASP A02:2025 Security Misconfiguration** (now #2)

---

## Shared responsibility

- Cloud secures *of* the cloud; you secure *in* the cloud
- Misconfig — not provider bugs — causes most breaches
- Defaults are rarely safe

---

## IAM & least privilege

```json
{ "Effect":"Allow", "Action":"*", "Resource":"*" }   // 🚩
```

- Over-broad policies = blast radius
- Grant only the actions/resources needed
- CWE-732 (bad permissions), CWE-16 (config)

---

## Secrets management

- Secrets in env vars / Dockerfile / git = leaked
- Use a secrets manager / vault; rotate
- Scan history (Gitleaks) — recall Week 2

---

## Storage & network exposure

- Public buckets, open ports, default creds
- Encrypt at rest + in transit
- Private by default; explicit allow

---

## Container image hardening

```bash
trivy config /src       # IaC/Dockerfile misconfig
trivy image myapp:lab   # image CVEs
```

- Minimal/distroless base, drop root, pin versions
- Re-scan to prove reduced findings

---

## Kubernetes basics (awareness)

- Pod security, network policies, RBAC
- Don't run privileged; limit service-account tokens

---

## 🔍 Game — Misconfig Hunt (CloudGoat-style)

Each misconfiguration **found + fixed** = a flag:

1. Over-permissive IAM (`*:*`) → least privilege
2. Exposed bucket → lock down
3. Env-var secrets → secrets manager
4. Vulnerable Dockerfile → harden + re-scan

---

## Deliverable

- Before/after IAM policy + Dockerfile
- Trivy reports showing reduced risk
- Note on secrets remediation

---

## Key takeaways

- Misconfiguration > zero-days as a breach cause
- Least privilege, private-by-default, no secrets in code
- Scan IaC and images in CI

---

# Questions?
Next week: AI / LLM application security
