# Week 10 — Software Supply-Chain Security I: Dependencies

**OWASP 2025:** A03 Software Supply Chain Failures · **CWE:** CWE-1104, CWE-829

## Objectives
- Explain why the supply chain is now a top-tier risk.
- Recognize dependency confusion, typosquatting, malicious packages, transitive risk.
- Run SCA tooling and interpret results.

## Lab
Target: a project with known-vulnerable dependencies (provided).
```bash
# SCA options
npm audit                                  # Node
docker run --rm -v "$PWD:/src" aquasec/trivy fs /src
# OWASP Dependency-Check (Java/multi)
docker run --rm -v "$PWD:/src" owasp/dependency-check --scan /src --format HTML
```
1. Produce a vulnerability list with CVEs and fix versions.
2. **Dependency confusion (controlled):** in an instructor-provided private registry, show how a higher-version public package can be pulled instead of the intended internal one.
3. Pin versions / add a lockfile + registry scoping to mitigate.

## Deliverable
SCA report + remediation plan + notes on the confusion scenario.

## References
- https://slsa.dev/  ·  https://owasp.org/www-project-dependency-check/
