# Quiz 2 — Answer Key (Weeks 10–15)

> Instructor copy. Total 25 pts.

## Part A — Multiple Choice (10 × 1 pt)

| Q | Ans | Note |
|---|-----|------|
| 1 | **b** | BOLA = IDOR at API scale |
| 2 | **a** | server binds fields client shouldn't set |
| 3 | **b** | canary detects overwrite before `ret` |
| 4 | **c** | memory-safe languages remove the bug class |
| 5 | **a** | public pkg shadows internal name |
| 6 | **b** | component inventory (CycloneDX/SPDX) |
| 7 | **b** | sign & verify artifacts/images |
| 8 | **b** | misconfiguration (A02) |
| 9 | **b** | via ingested content (RAG/web/doc) |
| 10 | **c** | fail the build |

## Part B — Short Answer (3 × 3 pts)

11. **BOLA (API1)** → fix: object-level authorization / ownership check on every request. **Mass assignment (API3)** → fix: allow-list bindable fields (bind only intended fields; server sets sensitive ones). *(1.5 each.)*

12. **Least privilege** = grant only the actions/resources needed for the task, nothing more. `*:*` allows every action on every resource (huge blast radius). Least-privilege read-only S3: *allow only `s3:GetObject` (and `s3:ListBucket`) on the specific bucket/prefix, and nothing else.* *(concept 1.5 + rewrite 1.5.)*

13. LLM output is shaped by attacker-influenceable input (prompt injection), so it's **untrusted input**. Downstream harm: output rendered into HTML → **XSS**, or fed to a tool/shell → injection/RCE; excessive agency → unwanted actions. Mitigation: output validation/schemas + encoding before downstream use + least-privilege tools. *(reason 1 + harm 1 + mitigation 1.)*

## Part C — Applied (2 × 3 pts)

14. *(1 pt each)*
- `FROM ubuntu:latest` → **unpinned base** (non-reproducible, may pull vulns) → pin a digest/version.
- **Runs as root** → container breakout / excess privilege → add a non-root `USER`.
- **Secret in `ENV`** → secret leaks in image layers/history → use a secrets manager / build secrets, never bake it in.

15. **Break the Build** = a CI gate running:
- **Semgrep** (SAST) — source-code bug patterns
- **Trivy** (SCA + image + IaC) — vulnerable deps / image CVEs / misconfig
- **Gitleaks** — secrets in code/history
Condition: **fail the build on HIGH/CRITICAL findings** (and upload SARIF to the Security tab). *(scanners 2 + fail condition 1.)*
