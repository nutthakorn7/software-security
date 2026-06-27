# Week 11 — Supply-Chain Security II: Integrity & Provenance

**OWASP 2025:** A03 Software Supply Chain Failures, A08 Software or Data Integrity Failures

## Objectives
- Generate and read an SBOM (CycloneDX/SPDX).
- Explain the SLSA framework and build provenance levels.
- Sign and verify an artifact with Sigstore/Cosign (keyless/OIDC).

## Lab
```bash
# 1) Build an image
docker build -t myapp:lab .
# 2) Generate an SBOM
docker run --rm -v "$PWD:/src" aquasec/trivy image --format cyclonedx -o /src/sbom.json myapp:lab
# 3) Sign (keyless, OIDC) and verify with Cosign
cosign sign myapp:lab
cosign verify myapp:lab
```
1. Produce an SBOM and identify the component inventory.
2. Sign the image; show a tampered/unsigned image fails verification.
3. Add a provenance/attestation step and verify it before a simulated deploy.

## Deliverable
SBOM file + signing/verification transcript + a one-paragraph SLSA self-assessment (which level you reach and why).

## References
- https://slsa.dev/  ·  https://www.sigstore.dev/  ·  https://cyclonedx.org/
