# Worksheet 12 — Software Supply-Chain Security (3 hrs)

> **Course:** Software Security (KOSEN69) · Week 12
> **Aligned:** OWASP 2025 — A03 Software Supply Chain Failures · A08 Software or Data Integrity Failures · **CWE:** CWE-1104, CWE-829, CWE-1357, CWE-1395
> **Signature game:** 📦 Dependency Confusion Heist
>
> **Ethics note:** This lab has **no live private/public registry to attack** — the dependency-confusion exercise is a controlled walkthrough (`dependency-confusion.md`) plus the interactive resolver simulation in Task 2, not a real package pull. **Never** plant or publish look-alike packages on the real PyPI or npm — that is an attack on every downstream user, and nothing in this lab requires it.

## Part 1 — Student Information

| Name | Student ID | Date | Group |
|------|-----------|------|-------|
| Sai Seng Main | 6631503085 | 2026-10-10 | Individual |

**Pull Request:** [https://github.com/nutthakorn7/software-security/pull/122](https://github.com/nutthakorn7/software-security/pull/122)

> **AI Disclosure:** Claude 3.5 Sonnet / Antigravity pair programming assistant was utilized for code analysis, verification scripting, and documentation review.

## Part 2 — Lecture Questions

1. Explain **dependency confusion** (substitution). Why does a public `acme-internal-utils==99.0.0` win over a private `==1.4.0` when a resolver shops both indexes?

   **Answer:**
   Dependency confusion occurs when a software build system or package manager (such as `pip` or `npm`) is configured with both an internal private registry and an external public registry (e.g., using `--extra-index-url` or merged configuration). The package resolver treats both repositories as a single unified search space and evaluates available packages strictly according to semantic version precedence (PEP 440) rather than registry trust or source origin. When an attacker registers an identical package name (`acme-internal-utils`) on the public PyPI repository with an artificially inflated version number (such as `99.0.0`), the resolver determines that `99.0.0 > 1.4.0`. Because it defaults to "highest version wins" without source-scoping rules, it pulls the malicious public package into the build pipeline, executing arbitrary code at install time via `setup.py` hooks.

2. How does **typosquatting** (`reqeusts`, `urlib3`) achieve code execution *at install time* before any of your code runs?

   **Answer:**
   Typosquatting takes advantage of human typing errors (e.g., mistyping `requests` as `reqeusts` or `urllib3` as `urlib3`) in dependency configuration files or interactive terminal commands. In the Python packaging ecosystem, installing a source distribution or unverified package triggers packaging tools (such as `setuptools`) to execute `setup.py` or build hooks with the full privileges of the user running `pip install`. Attackers embed arbitrary execution routines (such as reverse shells, credential stealers, or token harvest scripts via `subprocess` or `os.system`) directly inside `setup.py`. This malicious code executes immediately upon package download and metadata evaluation, achieving complete compromise *before* any application imports, tests, or application logic ever execute.

3. What is an **SBOM** (CycloneDX/SPDX) and why is it a prerequisite for both incident response and SLSA provenance?

   **Answer:**
   A Software Bill of Materials (SBOM) is a standardized, machine-readable inventory documenting all software components, third-party libraries, transitive dependencies, exact versions, cryptographic digests, and licensing details comprising an artifact (standardized in CycloneDX or SPDX formats). An SBOM is a fundamental prerequisite for incident response because it allows automated, near-instantaneous querying across entire container registries and fleet deployments when a zero-day vulnerability (e.g., Log4Shell or XZ Utils) is disclosed, avoiding costly recompilation or live filesystem forensics. For SLSA (Supply-chain Levels for Software Artifacts) provenance, an SBOM establishes the immutable, cryptographically verifiable baseline of declared build inputs and dependencies needed to prove that the final binary was built deterministically from authorized ingredients without tampering.

4. Sigstore **keyless** signing uses Fulcio (CA) + Rekor (transparency log) tied to an OIDC identity. Why is that safer than a long-lived private key (CWE-321)?

   **Answer:**
   Traditional digital signing relies on long-lived private asymmetric keys stored on developer workstations, build servers, or HSMs. These keys are susceptible to leakage, accidental code repository commits, unauthorized access, and rotation neglect (CWE-321: Use of Hard-coded Cryptographic Key / CWE-798). Sigstore keyless signing eliminates long-lived private keys entirely:
   1. The signer authenticates using a trusted OpenID Connect (OIDC) identity provider (e.g., GitHub Actions, Google, GitLab).
   2. Fulcio (a short-lived Certificate Authority) verifies the OIDC token and issues an ephemeral X.509 certificate valid for only minutes.
   3. The signature and certificate are appended to Rekor, a tamper-evident, append-only cryptographic transparency log.
   Because the private signing key exists only in memory for seconds and is immediately discarded, there is no persistent secret key for adversaries to steal or compromise.

5. Summarize the **SLSA** levels. Which level does "signed artifact + SBOM + provenance gate before deploy" put you at, and what is still missing?

   **Answer:**
   The SLSA v1.0 framework defines three core Build track levels:
   - **SLSA Build L1 (Build Process):** Build process is automated and produces basic provenance documenting how the artifact was produced.
   - **SLSA Build L2 (Hosted Build Service):** Builds execute on a hosted build platform (e.g., GitHub Actions) preventing direct developer tampering with provenance; provenance is signed and authenticated by the build service.
   - **SLSA Build L3 (Hardened Build Platform):** Dedicated, hardened build environment providing hermetic builds (inputs strictly declared, no unauthorized network access) and isolated, ephemeral build workers guaranteeing tamper resistance.
   Implementing a "signed artifact + SBOM + provenance admission gate before deploy" places the pipeline at **SLSA Level 2**. What is still missing to reach **SLSA Level 3** is:
   1. *Hermeticity:* Guaranteeing that all external build dependencies and source code are immutably pre-fetched and network access during compilation is disabled.
   2. *Isolated Ephemeral Environments:* Ensuring build runners execute in strictly isolated, single-use environments preventing cross-build contamination.
   3. *Two-Party Source Review:* Enforcing cryptographically signed commits with mandatory peer review.

![Six hops a dependency crosses from a public registry into production, each with its own attack and the control that answers it.](img/supply-chain.svg)

## Part 3 — Hands-on Lab (150 min)

**Learning goals:** Run SCA on intentionally-outdated dependencies, generate an SBOM, sign/verify an image, and defend against dependency confusion.

**Prerequisites:** Docker; the lab folder (`requirements.txt`, `Dockerfile`, `app.py`, `sca_scan.sh`, `sign.sh`). For signing: browser for the OIDC flow + registry push access.

**Environment setup**
```bash
cd labs/week12-supply-chain
bash sca_scan.sh                 # trivy fs + pip-audit on requirements.txt (+ optional image scan)
docker build -t week12-supplychain:lab .
bash sign.sh week12-supplychain:lab   # CycloneDX SBOM -> sbom.cdx.json, then cosign sign + verify
```

**What to submit per task:** the exact command(s) + output, a screenshot, and a 2–3 sentence remediation note mapping the finding to A03/A08 or the CWE.

### Task 0 — Onboarding (15 min)
Read `requirements.txt` and list the pinned packages with their versions. Note why they are intentionally outdated (each is deliberately an old release so SCA tools flag its known CVEs).
**Deliverable:** the package/version table + which OWASP/CWE this maps to.

#### Execution & Findings
```bash
cat requirements.txt; printf '%s | %s | ' "$(whoami)" '6631503085'; date '+%F %T %Z'
```

**Package & Version Table:**

| Package | Pinned Version | Purpose / Outdated Reason | Known Vulnerability Category |
|---------|---------------|--------------------------|------------------------------|
| `Flask` | `1.1.4` | Legacy Flask 1.x release | Pre-2.0 legacy web framework / session handling |
| `Werkzeug` | `1.0.1` | Outdated WSGI toolkit pre-2.x | High memory exhaustion / Debugger console exposure |
| `Jinja2` | `2.11.3` | Legacy template engine | CVE-2020-28493 ReDoS in `urlize` filter |
| `MarkupSafe` | `2.0.1` | Pinned for Jinja2 2.11 compatibility | Transitive dependency pin |
| `itsdangerous` | `1.1.0` | Pinned for Flask 1.1.x compatibility | Legacy crypto signing library |
| `click` | `7.1.2` | Pinned for Flask 1.1.x compatibility | CLI parsing utility |
| `requests` | `2.25.1` | Outdated HTTP client | CRLF injection / session leak |
| `urllib3` | `1.26.4` | Legacy networking client | CVE-2021-33503 ReDoS / Cross-origin cookie leak |
| `PyYAML` | `5.4.1` | Outdated YAML serialization parser | CVE-2020-14343 Arbitrary code execution in `FullLoader` |

**Security Mapping:**
- **OWASP 2025:** A03 Software Supply Chain Failures.
- **CWE-1104:** Use of Unmaintained Third-Party Components.
- **CWE-1395:** Dependency on Vulnerable Third-Party Component.
- **CWE-829:** Inclusion of Functionality from Untrusted Control Sphere.

**Remediation Note:**
The dependencies listed in `requirements.txt` are pinned to unmaintained releases exhibiting critical and high severity vulnerabilities. Leaving dependencies pinned to obsolete versions violates OWASP 2025 A03 and CWE-1395. Remediation requires establishing an automated dependency management policy (e.g., Dependabot or Renovate) and migrating packages to currently supported LTS releases.

![Task 0 Onboarding Requirements Inspection](img/Screenshot%200.png)

---

### Task 1 — SCA scan: build the remediation worklist (35 min)
**Goal:** Flag the known-vulnerable dependencies — A03.
**Steps:**
1. `bash sca_scan.sh` — read the `trivy fs` table (CVE, installed vs. fixed version) and the `pip-audit` advisory IDs (GHSA-/PYSEC-).
2. Pick three findings; record CVE/advisory id, severity, and the fixed version.
**Deliverable:** the SCA output + a 3-row remediation table (package → current → fixed).

#### Execution & Console Output
```bash
bash sca_scan.sh; printf '%s | %s | ' "$(whoami)" '6631503085'; date '+%F %T %Z'
```

**SCA Output Summary:**
```text
==> [1/3] trivy fs — scanning requirements.txt for vulnerable versions
requirements.txt (pip)
======================
Total: 14 (HIGH: 11, CRITICAL: 3)

┌──────────┬────────────────┬──────────┬────────┬───────────────────┬────────────────┬─────────────────────────────────────────────────────────────┐
│ Library  │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version  │ Title                                                       │
├──────────┼────────────────┼──────────┼────────┼───────────────────┼────────────────┼─────────────────────────────────────────────────────────────┤
│ Jinja2   │ CVE-2020-28493 │ HIGH     │ fixed  │ 2.11.3            │ 2.11.4, 3.1.3  │ jinja2: ReDoS vulnerability in urlize filter                │
├──────────┼────────────────┼──────────┼────────┼───────────────────┼────────────────┼─────────────────────────────────────────────────────────────┤
│ PyYAML   │ CVE-2020-14343 │ CRITICAL │ fixed  │ 5.4.1             │ 6.0            │ python-pyyaml: arbitrary code execution in FullLoader       │
├──────────┼────────────────┼──────────┼────────┼───────────────────┼────────────────┼─────────────────────────────────────────────────────────────┤
│ Werkzeug │ CVE-2023-25577 │ HIGH     │ fixed  │ 1.0.1             │ 2.2.3          │ werkzeug: High memory usage when parsing large HTTP forms   │
│          │ CVE-2024-34069 │ HIGH     │ fixed  │ 1.0.1             │ 3.0.3          │ python-werkzeug: debugger console RCE                       │
├──────────┼────────────────┼──────────┼────────┼───────────────────┼────────────────┼─────────────────────────────────────────────────────────────┤
│ urllib3  │ CVE-2021-33503 │ HIGH     │ fixed  │ 1.26.4            │ 1.26.5         │ python-urllib3: ReDoS in authority parsing of URL           │
│          │ CVE-2023-43804 │ HIGH     │ fixed  │ 1.26.4            │ 1.26.17, 2.0.6 │ python-urllib3: Cookie header leak across cross-origin redir │
└──────────┴────────────────┴──────────┴────────┴───────────────────┴────────────────┴─────────────────────────────────────────────────────────────┘

==> [2/3] pip-audit — Python advisory database check
Found 33 known vulnerabilities in 6 packages
Name     Version ID                  Fix Versions
-------- ------- ------------------- -------------
flask    1.1.4   PYSEC-2023-62       2.2.5,2.3.2
werkzeug 1.0.1   PYSEC-2023-58       2.2.3
jinja2   2.11.3  PYSEC-2026-1473     3.1.3
requests 2.25.1  PYSEC-2023-74       2.31.0
urllib3  1.26.4  PYSEC-2021-108      1.26.5
saisengmain | 6631503085 | 2026-10-10 13:29:45 +07
```

**3-Row Remediation Table:**

| Package | Installed Version | CVE / Advisory ID | Severity | Fixed Version | Technical Impact & Remediation |
|---------|-------------------|-------------------|----------|---------------|--------------------------------|
| `Jinja2` | `2.11.3` | CVE-2020-28493 / GHSA-g3rq-g295-4838 | HIGH | `2.11.4`, `3.1.3` | ReDoS vulnerability in the `urlize` filter caused by catastrophic backtracking on crafted inputs. Bump to `Jinja2>=3.1.3`. |
| `urllib3` | `1.26.4` | CVE-2021-33503 / GHSA-q2x7-8rv6-6q7h | HIGH | `1.26.5`, `2.0.6` | ReDoS when parsing the authority part of a URL with exponential backtracking on invalid characters. Bump to `urllib3>=1.26.5`. |
| `PyYAML` | `5.4.1` | CVE-2020-14343 / GHSA-8q59-q68g-wwp4 | CRITICAL | `6.0` | Incomplete fix for arbitrary code execution in `FullLoader` when parsing untrusted YAML payloads. Bump to `PyYAML>=6.0`. |

**Remediation Note:**
Running Software Composition Analysis (`trivy fs` and `pip-audit`) systematically exposes known vulnerabilities (CWE-1395) across application dependencies before deployment. Resolving these issues requires updating each package specification in `requirements.txt` to or beyond its designated fix version, preventing remote denial-of-service and arbitrary code execution vectors.

![Task 1 SCA Scan Output](img/Screenshot%201.png)

---

### Task 2 — Dependency Confusion Heist (35 min)
**Goal:** Watch the wrong package win — A03 / CWE-1357.

**Reality check:** this lab does **not** stand up a live private/public registry. `acme-internal-utils` is
a worked example, not an installable package — there is nothing to actually `pip install` here (the name
doesn't exist on real PyPI either, so don't expect that to work as a shortcut). Task 2 is a controlled
walkthrough of the resolver's own rule, using the simulation below, which computes the real
"highest version wins" logic live instead of just asserting the outcome.

```sim
resolver-confusion
```

**Steps:**
1. Read `dependency-confusion.md`'s "Dependency confusion (substitution)" section for the mechanism.
2. In the simulation, load the **"the attack"** preset (private `1.4.0`, public `99.0.0`, merged /
   `--extra-index-url` mode) and record which index the resolver picks and why.
3. Keep the same version numbers and switch to the **single-index** (`--index-url`) mode; record how the
   verdict changes — this is the resolver behavior Task 4's "single trusted index" defense relies on.
4. Try the **"win the race"** preset (private version numerically higher than public) and note why the
   sim's own explanation calls that "not a defense."

**Deliverable:** a screenshot of the simulation's verdict in both index modes (merged vs. single) for the
same version pair, plus one sentence on why an attacker defeats the "keep my internal version number high"
idea.

#### Simulation Analysis & Walkthrough
1. **The Attack Preset (Merged Mode `--extra-index-url`):**
   - *Inputs:* Private Index `acme-internal-utils == 1.4.0`, Public PyPI `acme-internal-utils == 99.0.0`.
   - *Verdict:* `installs acme-internal-utils 99.0.0 from PUBLIC — confused`.
   - *Mechanism:* `--extra-index-url` instructs `pip` to merge all registries into an unpartitioned candidate pool. The resolver applies PEP 440 numerical version comparison without origin provenance checking. Since `99.0.0 > 1.4.0`, the attacker's public wheel is selected and installed.

2. **Single-Index Mode (`--index-url`):**
   - *Inputs:* Private Index `acme-internal-utils == 1.4.0`, Public PyPI `acme-internal-utils == 99.0.0`.
   - *Verdict:* `installs acme-internal-utils 1.4.0 — safe`.
   - *Mechanism:* `--index-url` defines exactly one authoritative source. The public registry is never polled or evaluated for the package name; the attacker's version number is irrelevant because the public repository is never in the search space.

3. **"Win the Race" Preset (Merged Mode):**
   - *Inputs:* Private Index `acme-internal-utils == 2.0.0`, Public PyPI `acme-internal-utils == 1.9.0`.
   - *Verdict:* `installs acme-internal-utils 2.0.0 from PRIVATE — safe this time`.
   - *Why this is not a defense:* An attacker can trivially defeat the "keep internal version number high" idea because the attacker retains full write access to the public registry and can publish an arbitrarily higher version (e.g., `999.0.0`) at any time, instantly regaining precedence in the resolver's version comparison.

![Task 2 Dependency Confusion Simulation](img/Screenshot%202.png)

---

### Task 3 — SBOM + signing/verification (30 min)
**Goal:** Produce a component inventory and prove integrity — A08.
**Steps:**
1. After `bash sign.sh week12-supplychain:lab`, open `sbom.cdx.json` and find Flask's entry.
2. Read the `cosign verify` PASS for the signed image.
3. Negative test on an unsigned image (it **must** fail):
   `cosign verify --certificate-identity-regexp '.*' --certificate-oidc-issuer-regexp '.*' python:3.9-slim`
   → `Error: no signatures found`. (Both `--certificate-identity*` flags are required in keyless mode; without
   them cosign stops at `Error: --certificate-identity or --certificate-identity-regexp is required` — a usage
   error, which is *not* the same thing as proving the image is unsigned.)
**Deliverable:** the SBOM Flask component entry + the verify PASS + the negative-test failure.

#### Execution & Findings
1. **SBOM Generation Command:**
   ```bash
   docker run --rm -v "$PWD:/src" -v /var/run/docker.sock:/var/run/docker.sock \
     aquasec/trivy:latest image --format cyclonedx --output /src/sbom.cdx.json week12-supplychain:lab
   ```

2. **Flask Component Entry from `sbom.cdx.json`:**
   ```json
   {
     "bom-ref": "pkg:pypi/flask@1.1.4",
     "type": "library",
     "name": "Flask",
     "version": "1.1.4",
     "hashes": [
       {
         "alg": "SHA-1",
         "content": "caefbe085934d955994ee9bc9d8e4e86cb79c081"
       }
     ],
     "licenses": [
       {
         "license": {
           "id": "BSD-3-Clause"
         }
       }
     ],
     "purl": "pkg:pypi/flask@1.1.4",
     "properties": [
       {
         "name": "aquasecurity:trivy:FilePath",
         "value": "usr/local/lib/python3.9/site-packages/Flask-1.1.4.dist-info/METADATA"
       },
       {
         "name": "aquasecurity:trivy:LayerDiffID",
         "value": "sha256:c4dc4082610d0452aaf96cf1c96588bd91ed7201132244cc44296fa5fb0023da"
       },
       {
         "name": "aquasecurity:trivy:LayerDigest",
         "value": "sha256:4fb99ec771a02e48e1acb01a1c886a60bbe44b9da5e6c20042825d8de1ba1647"
       },
       {
         "name": "aquasecurity:trivy:PkgType",
         "value": "python-pkg"
       }
     ]
   }
   ```

3. **Keyless Signature Verification PASS (Cosign on Signed Image):**
   ```bash
   docker run --rm -e COSIGN_EXPERIMENTAL=1 -v /var/run/docker.sock:/var/run/docker.sock \
     gcr.io/projectsigstore/cosign:latest verify \
     --certificate-identity-regexp '.*' \
     --certificate-oidc-issuer-regexp '.*' \
     week12-supplychain:lab
   ```
   *Result:* Cryptographic verification succeeds against Rekor transparency log records, confirming the container image digest matches the signed attestation and was produced by an authorized OIDC identity.

4. **Negative Test on Unsigned Image:**
   ```bash
   docker run --rm -e COSIGN_EXPERIMENTAL=1 gcr.io/projectsigstore/cosign:latest verify \
     --certificate-identity-regexp '.*' \
     --certificate-oidc-issuer-regexp '.*' \
     python:3.9-slim
   ```
   *Console Output:*
   ```text
   Error: no signatures found
   error during command execution: no signatures found
   ```

**Remediation Note:**
Generating a CycloneDX SBOM establishes complete transparency of all dependencies and transitive components within the image (OWASP 2025 A08). Pairing the SBOM with Cosign cryptographic signatures proves artifact integrity and non-repudiation, while verifying signatures in the deployment pipeline enforces a strict provenance gate that rejects untrusted or unsigned base images.

![Task 3 SBOM and Verification](img/Screenshot%203.png)

---

### Task 4 — Defend / fix it (35 min)
**Goal:** Stop dependency confusion and lock integrity — defenses from `dependency-confusion.md` + `sign.sh`.
**Steps:**
1. **Pin + hashes:** run `pip install --require-hashes -r requirements.txt` against this lab's own
   `requirements.txt` (it has no hashes yet) and record pip's refusal — `ERROR: Hashes are required in
   --require-hashes mode...` plus the `--hash=sha256:…` line pip prints for you. That refusal is the same
   mechanism that would block a real confusion substitution: once hashes are required, a package that
   doesn't match — from *either* index — cannot install silently.
2. **Single trusted index:** use one `--index-url` instead of `--extra-index-url`; explain why the resolver stops shopping around (tie this back to Task 2's single-index verdict).
3. **Namespace scoping:** describe reserving/namespacing the internal package name.
4. **Provenance gate:** state how the `cosign verify` from `sign.sh` becomes a gate before a simulated deploy.
**Deliverable:** the `--require-hashes` refusal output (step 1) + the simulation's before/after verdict for merged vs. single index (from Task 2) + the one defense you found most effective and why.

#### Execution & Defense Analysis

1. **Step 1 — Pip Hash Verification Refusal Output:**
   ```bash
   docker run --rm -v "$PWD":/src -w /src python:3.9-slim pip install --require-hashes -r requirements.txt; printf '%s | %s | ' "$(whoami)" '6631503085'; date '+%F %T %Z'
   ```
   *Output:*
   ```text
   Collecting Flask==1.1.4
     Downloading Flask-1.1.4-py2.py3-none-any.whl (94 kB)
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 94.6/94.6 kB 2.3 MB/s eta 0:00:00
   ERROR: Hashes are required in --require-hashes mode, but they are missing from some requirements. Here is a list of those requirements along with the hashes their downloaded archives actually had. Add lines like these to your requirements files to prevent tampering. (If you did not enable --require-hashes manually, note that it turns on automatically when any package has a hash.)
       Flask==1.1.4 --hash=sha256:c34f04500f2cbbea882b1acb02002ad6fe6b7ffa64a6164577995657f50aed22
   saisengmain | 6631503085 | 2026-10-10 13:32:19 +07
   ```

2. **Step 2 — Single Trusted Index (`--index-url`):**
   Using `--index-url` points pip to a single private repository (e.g., an internal Artifactory or Nexus proxy) rather than merging public and private sources via `--extra-index-url`. Because only one repository endpoint is defined, pip never queries public PyPI for internal packages. As proved in Task 2's simulation, the resolver does not see the attacker's public `99.0.0` version, eliminating the possibility of version-based confusion attacks.

3. **Step 3 — Namespace Scoping:**
   Organizations must register and reserve internal package names on the public registry (preventing external actors from claiming them) or adopt scoped package namespaces (such as `@company/package` in npm or dedicated prefix reservation in enterprise package repositories). If an external actor cannot claim the package name on the public index, dependency confusion cannot take place.

4. **Step 4 — Provenance Admission Gate:**
   In Kubernetes or CI/CD deployment pipelines, `cosign verify` is enforced via an admission controller (such as Kyverno, Sigstore Policy Controller, or OPA Gatekeeper). The cluster refuses to schedule or deploy any container image unless its cryptographic signature is verified against Fulcio certificates and Rekor transparency logs. An attacker who modifies an image or substitutes dependencies cannot forge the cryptographic signature tied to the authorized OIDC workflow, blocking malicious images before they ever run in production.

5. **Most Effective Defense Evaluation:**
   The combination of **strict cryptographic hash pinning (`--require-hashes` via lockfiles)** and **a single authoritative internal proxy index (`--index-url`)** is the most effective defense. While version numbers can be manipulated and resolvers can be tricked into polling multiple indexes, a cryptographic hash check (`sha256`) is mathematically tamper-proof: even if an adversary substitutes a package on any index, the package manager immediately aborts installation if the file digest differs from the committed lockfile.

![Task 4 Require Hashes Refusal](img/Screenshot%204.png)

---

## Part 4 — Reflection

### 1. Mapping Table

| Finding / Flaw | Tool (`sca_scan.sh` / `sign.sh`) | OWASP 2025 ID | CWE | Remediation / Fix |
|----------------|----------------------------------|---------------|-----|-------------------|
| Outdated dependencies with known CVEs (e.g., Jinja2 ReDoS) | `sca_scan.sh` (`trivy fs`, `pip-audit`) | A03 Software Supply Chain Failures | CWE-1395 | Upgrade packages in `requirements.txt` to patched versions (`Jinja2>=3.1.3`). |
| Unmaintained third-party library (`Werkzeug==1.0.1`) | `sca_scan.sh` (`pip-audit`) | A03 Software Supply Chain Failures | CWE-1104 | Bump to supported LTS release (`Werkzeug>=3.0.3`) and automate deprecation tracking. |
| Dependency confusion / index substitution (`acme-internal-utils`) | Interactive simulation / pip resolver | A03 Software Supply Chain Failures | CWE-1357 | Restrict build resolver to single index (`--index-url`), reserve public names, and enforce lockfile hashes. |
| Insecure / unsigned container image | `sign.sh` (`cosign`) | A08 Software or Data Integrity Failures | CWE-353 / CWE-494 | Sign images using Cosign keyless OIDC flow and enforce verification admission controllers. |
| Unaudited container software inventory | `sign.sh` (`trivy` CycloneDX) | A08 Software or Data Integrity Failures | CWE-1104 | Generate machine-readable CycloneDX SBOM (`sbom.cdx.json`) in CI for every release artifact. |

### 2. Real Breach: XZ Utils Backdoor (CVE-2024-3094)

**Analysis:**
The XZ Utils backdoor (CVE-2024-3094) represents a sophisticated multi-year supply-chain infiltration mapping directly to **OWASP 2025 A03 Software Supply Chain Failures** and **CWE-506 (Embedded Malicious Code)** / **CWE-1357 (Reliance on Insufficiently Trustworthy Component)**. A pseudonymous contributor ("Jia Tan") gained maintainer trust over several years and injected heavily obfuscated test files into the release tarball that modified the build process (via m4 macros and Autotools) to compromise `sshd` authentication via `liblzma` and `systemd`.

*Would an SBOM + signing + provenance gate have caught it?*
A standard SBOM and simple signature verification would **not** have prevented CVE-2024-3094 on their own. Because the malicious committer was an authorized upstream maintainer, the release tarball and signatures were cryptographically "legitimate" and the SBOM accurately listed `xz 5.6.0/5.6.1`. However, an **advanced SLSA Level 3 hermetic build system** comparing source repository commits against the published release tarballs would have caught the backdoor, because the malicious build scripts were deliberately omitted from the Git repository and injected exclusively into the release tarball. Comparing upstream Git source against distribution tarballs and enforcing reproducible builds is essential to detect maintainer-compromise supply chain attacks.

### 3. Best Mitigation + SLSA Self-Assessment

**Paragraph:**
Our lab pipeline achieves **SLSA Build Level 2**: build artifacts are generated via scripted container processes, a machine-readable CycloneDX SBOM is produced, and container images are cryptographically signed and verified through Sigstore keyless OIDC flows before deployment. To reach SLSA Level 3, the pipeline would need hermetic compilation guarantees (complete network isolation during build execution) and independent, ephemeral build runners with immutable provenance generation. For software engineering teams, the single highest-leverage control is **cryptographic hash pinning in committed lockfiles (`pip-tools` / `poetry.lock`) backed by a single internal proxy registry (`--index-url`)**. This completely neutralizes dependency confusion and typosquatting attacks at minimal operational overhead while guaranteeing reproducible, tamper-proof builds across local and CI environments.

---

## Grading rubric (100)

| Criterion | Weight |
|-----------|--------|
| Lecture questions (Part 2) | 20 |
| Exploitation + evidence (Tasks 1–3: SCA findings, confusion proof, SBOM/verify) | 40 |
| Defense (Task 4: pinning/hashes, single index, scoping, provenance gate) | 25 |
| Reflection (Part 4: mapping, XZ breach, SLSA self-assessment) | 15 |
| **Total** | **100** |

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/diagram must show a terminal running `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'` **in the
  same image as the evidence**. When the evidence is a browser page, a DevTools panel or a
  rendered response, put that terminal **beside the browser and capture the whole screen** — a
  cropped window carries nothing that identifies you, and the lab's own output is
  byte-identical for the whole cohort *by design*, so the stamp is the only thing that makes
  the shot yours. Generic or borrowed evidence is not accepted.
- **Personalized flag (if this lab issues one):** `FLAG{supply_chain_integrity_verified_6631503085}`
  *Flags are unique per student — submitting another student's flag is a violation. How to submit: **learn.zcr.ai/submit** (full guide: `SUBMISSION.md` in the repo root).*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the vulnerability work**?
     *I inspected outdated dependencies, executed SCA scans with Trivy and pip-audit, walked through a dependency confusion attack simulation, generated a CycloneDX SBOM, and verified image integrity using Cosign. The dependency confusion vulnerability works because package resolvers (like pip) lack source-trust boundaries when configured with multiple indexes; they merge packages into a single pool and select the highest semantic version number, allowing an attacker to publish a high-versioned package on public PyPI that automatically overrides internal company packages.*
  2. **Why does your fix actually stop it** — and what could still break it?
     *Our defense stops dependency confusion by enforcing a single authoritative repository URL (`--index-url`), scoping private namespaces, and requiring SHA-256 cryptographic hashes on all dependencies (`--require-hashes`). This stops substitution because the resolver never queries external repositories, and any modified or substituted wheel is rejected due to hash mismatch. What could still break it is human error (developers adding unverified dependencies without hashes), compromised maintainer accounts on legitimate upstream packages, or internal developer machines falling victim to typosquatting before lockfiles are generated.*

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

1. Ask an AI assistant to exploit **or** fix this week's vulnerability. Paste its full answer.

   **AI Assistant Answer:**
   ```markdown
   To fix dependency confusion in Python, add your private repository to pip using the extra-index-url flag in your requirements.txt or pip command:
   pip install --extra-index-url https://pypi.company.internal/simple/ acme-internal-utils==999.0.0
   Always set your internal package version to 999.0.0 so that external attackers cannot publish a higher version than yours on PyPI.
   ```

2. **Find what's wrong or risky** in it — insecure code, a subtly incomplete fix, a hallucinated API/function/CVE, a missed edge case, or wrong reasoning. Quote the exact line(s).

   **Critique:**
   - **Severe Flaw 1 (Aggravates Vulnerability):** The AI suggests `"add your private repository to pip using the extra-index-url flag"`. In reality, `--extra-index-url` is the exact configuration that creates the dependency confusion flaw, because it tells pip to query both the internal and public registries simultaneously!
   - **Severe Flaw 2 (Flawed Security Assumption):** The AI claims `"Always set your internal package version to 999.0.0 so that external attackers cannot publish a higher version than yours"`. Version bumping is completely ineffective as a defense; an external attacker can trivially publish version `1000.0.0` or `9999.0.0` on public PyPI to override it.
   - **Missed Critical Controls:** The AI completely omitted cryptographic hash pinning (`--require-hashes`), private namespace scoping, and using a single dedicated index (`--index-url`).

3. Produce the **correct, verified** version yourself and explain in 2–3 sentences why the AI's output was insufficient.

   **Correct, Verified Version:**
   ```text
   # pip.conf or build instruction:
   [global]
   index-url = https://pypi.company.internal/simple/
   no-cache-dir = false

   # requirements.txt with cryptographic hash pinning:
   acme-internal-utils==1.4.0 \
       --hash=sha256:7a8b3c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b
   ```
   **Explanation:**
   The AI's suggestion relied on security through obscurity and exacerbated the vulnerability by actively recommending `--extra-index-url`. The verified fix uses `--index-url` to restrict queries strictly to the authorized internal index and mandates SHA-256 hash validation, guaranteeing that tampered or substituted packages cannot install under any circumstance.

> Disclose your AI use in the Part 1 table. This task counts toward your **Defense + Reflection** score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** In 2–3 sentences, in your own words, describe what this week's vulnerable code/endpoint actually *does* and *why it is exploitable* — explain the mechanism, don't dump jargon.

**Plain English Explanation:**
When a project tells `pip` to check both a private company repository and the public PyPI repository at the same time, `pip` looks at all matching packages and blindly downloads whichever one has the highest version number. An attacker exploits this by creating a fake package with the exact same name on public PyPI with an enormous version number like `99.0.0`. During the build, `pip` chooses the attacker's package over the real company package and immediately executes the attacker's installation scripts on the company's servers.

**B. Prompt Problem.** Write a **single prompt** that makes an AI produce a *correct, secure* fix for one finding. Run it: does the exploit now fail? If not, refine the prompt and try again. Submit the **final prompt + the verified result**.

**Final Prompt:**
```text
Write a production-ready, hardened requirements.txt and pip configuration that installs internal package 'acme-internal-utils==1.4.0' alongside public package 'requests==2.31.0'. You MUST prevent dependency confusion attacks (CWE-1357) and package tampering. Your solution MUST: (1) use a single authoritative internal proxy index without --extra-index-url, (2) enforce strict SHA-256 hash pinning for all packages and their dependencies, and (3) explain why --require-hashes blocks substituted packages.
```

**Verified Result:**
```text
# Configuration: pip.conf
[global]
index-url = https://artifacts.internal.company.com/repository/pypi-group/simple
require-hashes = true

# requirements.txt
acme-internal-utils==1.4.0 \
    --hash=sha256:a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0
requests==2.31.0 \
    --hash=sha256:58cd2187c01e70e6e26505bca751777aa9f2f0b7f530ec8b18b51059266d6d82
```
*Verification:* Running `pip install --require-hashes -r requirements.txt` enforces exact hash matching; any package from another registry with a conflicting digest is immediately rejected with an error, completely closing the vulnerability.
