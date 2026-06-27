# Week 14 — DevSecOps: Putting It Together

**OWASP 2025:** A09 Security Logging & Alerting Failures, A10 Mishandling of Exceptional Conditions

## Objectives
- Add logging/monitoring/alerting and fail-safe error handling.
- Build a CI/CD pipeline that enforces security gates.
- Understand vulnerability management and coordinated disclosure.

## Lab — build a security gate
Use the repo's own pipeline as the template: [`.github/workflows/security-ci.yml`](../../.github/workflows/security-ci.yml).
1. Add **SAST** (Semgrep), **SCA + image scan** (Trivy), and **secret scanning** (Gitleaks) jobs.
2. Configure the build to **fail** on HIGH/CRITICAL findings.
3. Upload SARIF to the GitHub Security tab.
4. Add structured security logging + an alert on auth failures to a sample service; ensure errors **fail closed**, not open.

## Deliverable
A passing PR that adds the pipeline, plus a screenshot of a build failing on an injected vulnerable dependency.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- https://docs.github.com/actions
