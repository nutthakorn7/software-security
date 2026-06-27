---
marp: true
theme: default
paginate: true
header: "Software Security · Week 2"
---

# Week 2
## Secure SDLC, Tooling & Fuzzing
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Security across the SDLC
- SAST / DAST / SCA / secret scanning
- **Fuzzing** — the modern bug-finder
- Triaging findings by CWE
- 🎮 Game: **Bug Triage Race** + **Fuzzing Race**

---

## Recap — Week 1

- Threat modeling finds *design* flaws
- This week: find *implementation* flaws — automatically
- Shift left: catch bugs before they ship

---

## Security across the SDLC

Requirements → Design → Code → Build → Test → Deploy → Operate

- Each phase has security activities
- **Shift left:** find issues early — cheaper to fix
- DevSecOps = security automated into the pipeline

---

## The tooling families

| Tool | What it sees | When |
|---|---|---|
| **SAST** | source code | code/commit |
| **DAST** | running app | test/staging |
| **SCA** | dependencies | build |
| **Secret scanning** | secrets in code/history | commit/CI |
| **Fuzzing** | runtime + random inputs | test |

---

## SAST vs DAST in one line

- **SAST** — reads the code, finds bug patterns (no running). Many false positives.
- **DAST** — attacks the live app from outside. Fewer FPs, misses source-level issues.

> Use both — they find different things.

---

## SCA & secret scanning

- **SCA** — your dependencies' known CVEs (deep dive in Wk 12)
- **Secret scanning** — API keys/passwords committed to git history
- Both run automatically in CI

---

## Tools you'll meet

- **SonarQube** — code quality + SAST against the "7 axes" (bugs, duplication, complexity, coverage…)
- **GitHub Advanced Security (GHAS)** — CodeQL + secret scanning + Dependabot, native in the repo
- Address **technical debt** early — cheaper than re-work later

---

## Fuzzing — how real CVEs are found

- Feed **random/mutated inputs**, watch for crashes
- **Coverage-guided** (libFuzzer/AFL++) explores new paths
- Pair with sanitizers (ASan) to pinpoint the bug

```bash
clang -fsanitize=address,fuzzer harness.c -o fuzz && ./fuzz
```

---

## Triage: not every finding is a bug

- **True positive** vs **false positive**
- Map each to a **CWE** + severity
- Prioritize by exploitability × impact
- Noise kills trust in tools — triage well

---

## 🏁 Game — Bug Triage Race

- Run **Semgrep + Gitleaks** on a flawed repo
- Score = true positives − misclassified
- Live scoreboard

```bash
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep --config p/default /src
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect -s /repo -v
```

---

## 🐝 Mini-game — Fuzzing Race

- First team to make the provided target **crash** wins
- One crash → one root-cause note
- Full fuzz→exploit lab returns in **Week 11**

---

## Lab 2 — deliverable

- A findings **triage table**: tool, CWE, severity, TP/FP, fix idea
- 3 true positives + 1 false positive (justified)
- 1 fuzzing crash with a one-line root cause

---

## Key takeaways

- No single tool finds everything — layer SAST/DAST/SCA/fuzzing
- Triage by CWE + severity; kill the noise
- Fuzzing is the highest-yield bug finder — automate it

---

# Questions?
Next week: Cryptography used correctly
