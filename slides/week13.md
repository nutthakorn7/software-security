---
marp: true
theme: default
paginate: true
header: "Software Security · Week 13"
---

# Week 13
## Cloud & Container Security
Software Security · Nutthakorn Chalaemwongwan

<!-- Hook: most cloud breaches aren't clever zero-days — they're a public S3 bucket or a `*:*` IAM policy. Today we hunt and fix those misconfigs. ~2 min. -->

---

## Today

- Shared-responsibility model
- IAM & least privilege
- Secrets management
- Container/image hardening
- 🎮 Game: **Misconfig Hunt**

<!-- Roadmap, 1 min. Theme: the cloud is secure; your CONFIGURATION usually isn't. Lab = find + fix misconfigurations, each one a flag. -->

---

## Recap & framing

- Supply chain → what you build with
- Today → where you run it
- **OWASP A02:2025 Security Misconfiguration** (now #2)

<!-- 1-min bridge. Misconfiguration jumped to A02 in 2025 — it's not a footnote, it's the second most critical web risk. ~2 min. -->

---

## Shared responsibility

- Cloud secures *of* the cloud; you secure *in* the cloud
- Misconfig — not provider bugs — causes most breaches
- Defaults are rarely safe

<!-- The mental model students most misunderstand: AWS secures the hardware/hypervisor; YOU secure your buckets, IAM, security groups. Almost every headline cloud breach is the customer's config, not the provider. ~4 min. -->

---

## IAM & least privilege

```json
{ "Effect":"Allow", "Action":"*", "Resource":"*" }   // 🚩
```

- Over-broad policies = blast radius
- Grant only the actions/resources needed
- CWE-732 (bad permissions), CWE-16 (config)

<!-- The worked example — this `*:*` policy is the Misconfig Hunt round 1 and the quiz. If a credential with this leaks, the attacker owns everything. Ask the class to rewrite it as read-only on one bucket. Least privilege = smallest possible blast radius. ~6 min. -->

---

## Secrets management

- Secrets in env vars / Dockerfile / git = leaked
- Use a secrets manager / vault; rotate
- Scan history (Gitleaks) — recall Week 2

<!-- Connect to W2 (Gitleaks) and W12. A secret baked into an image layer is in every copy of that image forever — `docker history` reveals it. Fix = inject at runtime from a vault + rotate. ~4 min. -->

---

## Storage & network exposure

- Public buckets, open ports, default creds
- Encrypt at rest + in transit
- Private by default; explicit allow

<!-- The classic trio behind most breaches. `0.0.0.0/0` on a DB port = the internet can reach your database. Default creds = free entry. Principle: deny by default, open deliberately (echoes W6 access control). ~4 min. -->

---

## Container image hardening

```bash
trivy config /src       # IaC/Dockerfile misconfig
trivy image myapp:lab   # image CVEs
```

- Minimal/distroless base, drop root, pin versions
- Re-scan to prove reduced findings

<!-- Hands-on — this is the lab's insecure→hardened Dockerfile. `trivy config` finds the misconfig (root user, latest tag); `trivy image` finds CVEs in the base. Drop root + distroless = container escape gives far less. Re-scan to prove improvement. ~5 min. -->

---

## Kubernetes basics (awareness)

- Pod security, network policies, RBAC
- Don't run privileged; limit service-account tokens

<!-- Awareness only (K8s is its own course). Key takeaways: a privileged pod ≈ host root; mounted service-account tokens are a lateral-movement prize. Keep it brief. ~3 min. -->

---

## 🔍 Game — Misconfig Hunt (CloudGoat-style)

Each misconfiguration **found + fixed** = a flag:

1. Over-permissive IAM (`*:*`) → least privilege
2. Exposed bucket → lock down
3. Env-var secrets → secrets manager
4. Vulnerable Dockerfile → harden + re-scan

<!-- Explain before lab. Find AND fix = the flag (defending is the point). Q6 of the quiz asks for one misconfig they fixed + the principle it violated. ~3 min. -->

---

## Deliverable

> 📋 **Worksheet 13** — `labs/week13-cloud-container/worksheet.md` (Part 3) · **kickoff:** `bash scan.sh` (trivy config over Dockerfiles + IAM JSON)

- Before/after IAM policy + Dockerfile
- Trivy reports showing reduced risk
- Note on secrets remediation
- **+ Audit the AI / EiPE / Prompt Problem** (see worksheet)

<!-- Before/after artifacts + the trivy delta prove the fix. AI-resilient tasks count. -->

---

## Key takeaways

- Misconfiguration > zero-days as a breach cause
- Least privilege, private-by-default, no secrets in code
- Scan IaC and images in CI

<!-- Recap. Cold-call: "what does a `*:*` IAM policy cost you if the key leaks?" (everything — full blast radius). "Scan in CI" sets up W15. ~2 min. -->

---

# Questions?
Next week: AI / LLM application security

<!-- Cliffhanger: "Next week — the newest attack surface: make an AI assistant ignore its rules and leak secrets, with nothing but text." -->
