# Term Project — Secure Build

**Teams of 2–3 (nested in your House). 15% of the final grade.**

Take a small web/API application (provided starter, or your own with instructor approval), assess it like an attacker, fix it like a defender, and harden its build/release pipeline.

**Default target:** [`starter-app/`](starter-app/README.md) — *NoteVault*, an intentionally weak note-sharing app spanning the course's vulnerability classes. `cd project/starter-app && docker compose up`.

## Deliverables

1. **Threat model** — data-flow diagram + STRIDE analysis identifying trust boundaries and the top risks.
2. **Vulnerability report** — each finding mapped to **CWE** and the relevant **OWASP Top 10:2025** (or API / LLM Top 10) category, with severity, reproduction steps, and impact.
3. **Remediated code** — the fixes, in a branch with clear commits referencing each finding.
4. **Supply-chain hardening** — generate an **SBOM** (CycloneDX) and **sign the release artifact** with Cosign.
5. **Security CI pipeline** — a GitHub Actions workflow running SAST + SCA + secret scanning that fails on high-severity findings.
6. **Demo** — a short live walkthrough: attack → root cause → fix (WIP demo in the **Week 16** capstone studio; graded final demo in **Week 19**).

## Suggested timeline

| Milestone | Due |
|---|---|
| Team + target chosen | Week 4 |
| Threat model submitted | Week 7 |
| Vulnerability report (draft) | Week 11 |
| Remediation + SBOM + signed artifact | Week 14 |
| Capstone studio — WIP demo & peer review | Week 16 |
| Final demo & report (graded) | Week 19 |

## Rubric (100 pts)

| Criterion | Pts |
|---|---|
| Threat model quality & completeness | 20 |
| Vulnerability findings (correctness, CWE/OWASP mapping, depth) | 25 |
| Remediation quality (correct, minimal, well-explained) | 25 |
| Supply-chain hardening (SBOM + signing + provenance) | 15 |
| CI pipeline (works, fails build appropriately) | 10 |
| Presentation & report clarity | 5 |

## Peer-contribution evaluation (individual fairness)

The project is the only *graded* team work, so each member's mark is adjusted for actual
contribution:
- At submission, **each member privately rates every teammate** (including themselves) on a
  simple scale — e.g. *Full / Most / Some / Little* — with a one-line justification.
- The team mark is **scaled per member** by the averaged rating (typically ×0.8–1.1; an
  unjustified low score is discussed before it's applied).
- Per-student lab flags + each member's own commit history (see Academic Integrity) corroborate
  who did what. A "single paste-everything" contribution is a red flag.

This protects diligent students and removes the "carry a free-rider" problem — the reason team
weight is kept bounded (15%) while mastery is graded individually.

## Report

Write up the project using the fill-in [REPORT-TEMPLATE.md](REPORT-TEMPLATE.md) — it maps section-by-section to the rubric above and includes an AI-tool usage disclosure.

All work stays within the [ethics policy](../ETHICS.md).
