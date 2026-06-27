# Week 2 — Secure SDLC & Tooling

**Concepts:** SAST · DAST · SCA · IAST · secret scanning · shift-left / DevSecOps

## Objectives
- Place security activities across the SDLC.
- Distinguish SAST vs DAST vs SCA and when each applies.
- Run a static analyzer and a secret scanner and triage findings by CWE.

## Lab — Scan a flawed repo
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

## Deliverable
A findings triage table (tool, CWE, severity, TP/FP, fix idea).

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Secure_Product_Design_Cheat_Sheet.html
- https://semgrep.dev/  ·  https://github.com/gitleaks/gitleaks
