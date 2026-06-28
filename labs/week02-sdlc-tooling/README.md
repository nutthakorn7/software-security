# Week 2 — Secure SDLC & Tooling

**Concepts:** SAST · DAST · SCA · IAST · secret scanning · **fuzzing** · shift-left / DevSecOps

## ✅ This week — what to do
1. **Before class** — VM + Docker working (Week 1 *Lab 0*); skim last week's recap.
2. **Lecture (120 min)** — weekly quiz first (~10 min), then the lecture. Slides: `slides/week02.md`.
3. **Lab (180 min)** — play this week's game, then complete **Worksheet 2** (`worksheet.md`, Parts 1–4, incl. *Audit the AI* + *EiPE/Prompt*). Kickoff: `bash scan.sh`.
4. **Submit** — worksheet PDF → Classroom · code → GitHub · weekly quiz → Google Form. (How: [SUBMISSION.md](../../SUBMISSION.md).)
5. **Project** — apply this week's lesson to your [NoteVault project](../../project/README.md) where it fits.

*Time breakdown: [AGENDA.md](../../AGENDA.md). Grading: see the worksheet rubric.*

## Objectives
- Place security activities across the SDLC.
- Distinguish SAST vs DAST vs SCA vs **fuzzing** and when each applies.
- Run a static analyzer and a secret scanner and triage findings by CWE.
- Understand coverage-guided **fuzzing** as the dominant modern bug-finding technique.

## 🏁 Signature game — "Bug Triage Race"
Teams race to scan a flawed repo and triage accurately. Score = true positives − misclassified. Live scoreboard.
Target: an intentionally insecure repo (provided).
```bash
# SAST
docker run --rm -v "$PWD:/src" semgrep/semgrep semgrep --config p/default /src
# Secret scanning
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect -s /repo -v
```
1. Run both tools; export findings.
2. Categorize each finding by CWE and severity.
3. Mark 3 true positives and 1 likely false positive; justify.

## Mini-lab — "Fuzzing Race" (intro)
First team to make the target crash wins. A deeper fuzzing+exploit lab follows in [Week 11](../week11-memory-safety-exploitation/).
```bash
# coverage-guided fuzzing of a small provided harness
clang -fsanitize=address,fuzzer harness.c -o fuzz && ./fuzz
```

## Deliverable
A findings triage table (tool, CWE, severity, TP/FP, fix idea) + one fuzzing crash with a one-line root-cause note.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Secure_Product_Design_Cheat_Sheet.html
- https://semgrep.dev/  ·  https://github.com/gitleaks/gitleaks
- https://llvm.org/docs/LibFuzzer.html  ·  https://github.com/AFLplusplus/AFLplusplus
