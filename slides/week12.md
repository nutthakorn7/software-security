---
marp: true
theme: default
paginate: true
header: "Software Security · Week 12"
---

# Week 12
## Software Supply-Chain Security
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Why the supply chain is now top-tier
- Dependency confusion & typosquatting
- SBOMs, SLSA provenance
- Signing with Sigstore/Cosign
- 🎮 Game: **Dependency Confusion Heist**

---

## The new #1 design risk

- Your code is ~10% yours, ~90% dependencies
- One bad package → thousands of victims (xz, event-stream, SolarWinds)
- **OWASP A03:2025 Software Supply Chain Failures**

---

## Real supply-chain attacks

| Case | What happened |
|---|---|
| **SolarWinds** (2020) | trojanized vendor update → 18k orgs |
| **Log4Shell** (2021) | RCE in a ubiquitous logging dep |
| **event-stream** (npm) | malicious dep stole crypto-wallet keys |
| **XZ Utils** (2024) | backdoor planted in `liblzma` upstream |
| **CircleCI** (2023) | stolen CI tokens → customer secrets |

> Attacks are shifting **upstream**: registry → maintainer → CI/CD.

---

## Attack vectors

- **Typosquatting** — `reqeusts` vs `requests`
- **Dependency confusion** — public pkg shadows internal name
- **Malicious updates** — compromised maintainer
- **Transitive risk** — deps of deps you never chose

---

## SCA — find vulnerable deps

```bash
npm audit
docker run --rm -v "$PWD:/src" aquasec/trivy fs /src
owasp/dependency-check --scan /src --format HTML
```

- Produces CVEs + fix versions
- CWE-1104 (unmaintained), CWE-829 (untrusted inclusion)

---

## Integrity: prove what you shipped

- **SBOM** (CycloneDX/SPDX) — ingredient list of the build
- **SLSA** — levels of build provenance & tamper-resistance
- **A08:2025** Software/Data Integrity Failures

---

## Signing with Cosign (keyless)

```bash
trivy image --format cyclonedx -o sbom.json myapp:lab   # SBOM
cosign sign myapp:lab                                   # sign (OIDC)
cosign verify myapp:lab                                 # verify
```

- Unsigned/tampered image → verification fails

---

## Tooling — GitHub Advanced Security (GHAS)

- **Secret scanning** + **push protection** — block secrets before commit
- **CodeQL** code scanning — semantic SAST queries
- **Dependabot** — alerts + auto-PRs for vulnerable deps
- Native in the repo → results in the Security tab

---

## Defenses

- Pin versions + lockfiles; scope internal registries
- Verify signatures before deploy (admission policy)
- Generate + store SBOMs per release
- 2FA/MFA on dev/CI/cloud accounts; least privilege
- Automate SCA in CI (next week)

---

## 📦 Game — Dependency Confusion Heist

1. **Attack:** in a controlled registry, plant/identify a typosquat or higher-version public pkg that gets pulled in
2. **Defend:** pin + scope; generate SBOM; sign & verify with Cosign; add a provenance gate

---

## Deliverable

- SCA report + remediation plan
- SBOM file + sign/verify transcript
- One-paragraph SLSA self-assessment (which level + why)

---

## Key takeaways

- Most of your attack surface is other people's code
- Know your ingredients (SBOM), prove your build (SLSA), sign your artifacts
- Verify before you trust

---

# Questions?
Next week: Cloud & container security
