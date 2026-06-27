# Software Security — Course Syllabus & Outline

**Level:** Undergraduate (3rd / 4th year)
**Credits:** 3 (2 lecture hours + 3 lab hours per week)
**Prerequisites:** Programming (Python/C), Data Structures, Operating Systems basics, Computer Networks (recommended)
**Format:** Lecture + weekly hands-on lab
**Last updated:** June 2026

---

## 1. Course Description

This course teaches students how software fails under attack and how to build software that resists it. It blends timeless fundamentals (memory safety, injection, authentication, cryptography misuse) with the threats that dominate modern systems: **software supply-chain attacks, cloud and container misconfiguration, API abuse, and the security of AI/LLM-powered applications.**

The course is deliberately hands-on. Every week pairs a lecture concept with a lab in which students either *break* an intentionally vulnerable target in a safe sandbox or *defend* code they write themselves. Students leave able to threat-model a system, find and exploit common vulnerability classes, remediate them, and integrate security checks into a CI/CD pipeline.

The course is aligned with current industry references including the **OWASP Top 10 (2025)**, the **OWASP Top 10 for LLM Applications (2025)**, the **OWASP API Security Top 10**, **MITRE ATT&CK / CWE**, and the **SLSA** supply-chain framework.

---

## 2. Learning Outcomes

By the end of the course, students will be able to:

1. **Threat-model** a software system and reason about its attack surface, trust boundaries, and adversary capabilities.
2. **Identify and exploit** common vulnerability classes (injection, broken access control, memory-safety bugs, insecure design) in a controlled environment.
3. **Write and review secure code**, applying input validation, output encoding, safe defaults, and least privilege.
4. **Apply cryptography correctly**, recognizing common misuse and selecting appropriate primitives.
5. **Secure the modern software supply chain** using dependency analysis, SBOMs, artifact signing, and build provenance.
6. **Secure cloud, container, and API workloads**, including IAM, secrets management, and configuration hardening.
7. **Assess and defend AI/LLM-powered applications** against prompt injection, insecure output handling, and excessive agency.
8. **Integrate security into the development lifecycle** (SAST, DAST, SCA, secret scanning) within a CI/CD pipeline (DevSecOps).
9. **Disclose vulnerabilities responsibly** and communicate risk to technical and non-technical stakeholders.

---

## 3. Why This Course Is "Modern"

Traditional software-security courses stop at buffer overflows and SQL injection. Those still matter and are covered here — but the 2025 threat landscape has shifted toward **design-level and dependency-level failures**. The OWASP Top 10:2025 made this explicit by adding **Software Supply Chain Failures** as a new top-tier category and elevating **Security Misconfiguration** to #2. This course reflects that shift and adds two areas most curricula still lack:

- **Software supply-chain security** (SLSA, SBOMs, Sigstore/Cosign, dependency confusion, typosquatting).
- **AI/LLM application security** (the OWASP LLM Top 10, prompt injection, RAG/vector-store risks, agentic systems).

---

## 4. Lab Environment

All offensive work is performed **only** against instructor-provided, intentionally vulnerable targets inside an isolated sandbox. Students never attack systems they do not own or lack written permission to test.

**Required toolkit (all free / open source):**

- **Kali Linux** or **Ubuntu** VM (VirtualBox/UTM) — base workstation.
- **Docker + Docker Compose** — to run vulnerable targets locally and reproducibly.
- **Git + a GitHub account** — for labs, CI/CD, and the term project.
- Browser with **Burp Suite Community** or **OWASP ZAP** — web/API testing proxy.

**Pre-built vulnerable targets used during the term:**

- **OWASP Juice Shop** — modern web app vulnerabilities.
- **OWASP WebGoat** — guided web-security lessons.
- **DVWA** (Damn Vulnerable Web Application).
- **crAPI / Damn Vulnerable Web Services** — API security.
- **pwn.college / picoCTF / OverTheWire** — binary and systems exploitation.
- **Gandalf / a self-hosted vulnerable LLM chatbot** — prompt-injection practice.

A one-page **"Lab 0" setup guide** is provided in Week 1 so the whole environment can be stood up in under an hour via a single `docker compose up`.

---

## 5. Weekly Outline (15 weeks)

> Each week: **Lecture** (concepts) → **Lab** (hands-on) → optional reading.

### Unit A — Foundations (Weeks 1–3)

**Week 1 — Security Mindset & Threat Modeling**
*Lecture:* What "secure" means; CIA triad; attacker vs. defender mindset; trust boundaries; attack surface; introduction to STRIDE and the OWASP/MITRE landscape (Top 10, CWE, ATT&CK).
*Lab 0 + Lab 1:* Stand up the VM/Docker environment. Build a STRIDE threat model and data-flow diagram for a small provided web app; enumerate its attack surface.

**Week 2 — Secure Software Development Lifecycle (SDLC) & Tooling**
*Lecture:* Where security fits in the SDLC; security requirements; SAST vs. DAST vs. SCA vs. IAST; secret scanning; "shift left" and DevSecOps overview.
*Lab:* Run a SAST tool (Semgrep) and a secret scanner (Gitleaks) on a deliberately flawed repo; triage and categorize findings by CWE.

**Week 3 — Cryptography Used Correctly (and Misused)**
*Lecture:* Hashing vs. encryption vs. encoding; symmetric/asymmetric basics; password storage (bcrypt/argon2); TLS at a high level; common crypto failures (ECB, hardcoded keys, weak randomness, MD5/SHA-1). Maps to **A04:2025 Cryptographic Failures**.
*Lab:* Break weak crypto — crack unsalted/MD5 hashes, exploit an ECB-mode oracle, then remediate the code to use a vetted KDF and authenticated encryption.

### Unit B — Web & API Security (Weeks 4–7)

**Week 4 — Injection & Input Handling**
*Lecture:* SQL injection, command injection, and the general injection pattern; parameterized queries; output encoding. Maps to **A05:2025 Injection**.
*Lab:* Exploit SQLi and command injection in DVWA / Juice Shop; rewrite the vulnerable endpoints using prepared statements and validation.

**Week 5 — Cross-Site Scripting (XSS) & Client-Side Risks**
*Lecture:* Reflected/stored/DOM XSS; CSRF; SameSite cookies; Content Security Policy; the browser security model and same-origin policy.
*Lab:* Build and fire stored + DOM XSS payloads in Juice Shop; deploy a CSP and proper escaping to block them; demonstrate a CSRF attack and its defense.

**Week 6 — Authentication, Sessions & Access Control**
*Lecture:* Authn vs. authz; session management; JWT pitfalls; OAuth 2.0 / OIDC at a high level; IDOR and privilege escalation. Maps to **A01:2025 Broken Access Control** and **A07:2025 Authentication Failures**.
*Lab:* Exploit IDOR and broken access control to reach other users' data; forge a weak JWT; implement role-based access checks and fix the token handling.

**Week 7 — API Security**
*Lecture:* REST/GraphQL attack surface; the **OWASP API Security Top 10** (BOLA, broken authentication, excessive data exposure, mass assignment, rate-limiting/resource consumption).
*Lab:* Attack the **crAPI** target — exploit BOLA and mass assignment, then add authorization checks, schema validation, and rate limiting.

### Unit C — Systems & Memory Safety (Weeks 8–9)

**Week 8 — Memory-Safety Vulnerabilities**
*Lecture:* The C/C++ memory model; stack buffer overflows; integer overflow; use-after-free; why memory-safe languages (Rust, Go) matter; modern mitigations (ASLR, stack canaries, NX/DEP).
*Lab:* Exploit a classic stack overflow to hijack control flow in a provided binary (sandbox); observe how a canary and ASLR change the attack; rewrite the routine safely.

**Week 9 — Exploitation Mitigations & Reverse Engineering Basics**
*Lecture:* How modern defenses raise the bar; intro to disassembly/decompilation; format-string bugs; defense-in-depth thinking.
*Lab:* Use `gdb`/Ghidra to analyze a small binary, find a format-string or off-by-one bug, and write a proof-of-concept; then patch it.

### Unit D — Modern Stack: Supply Chain, Cloud & AI (Weeks 10–13)

**Week 10 — Software Supply-Chain Security I: Dependencies**
*Lecture:* Why the supply chain is now a top-tier risk (**A03:2025 Software Supply Chain Failures**); dependency confusion, typosquatting, malicious packages; transitive dependency risk; SCA tooling.
*Lab:* Run an SCA scan (OWASP Dependency-Check / `npm audit` / Trivy) on a project with known-vulnerable dependencies; reproduce a dependency-confusion scenario in a controlled registry.

**Week 11 — Software Supply-Chain Security II: Integrity & Provenance**
*Lecture:* SBOMs (CycloneDX/SPDX); the **SLSA** framework and build provenance; artifact signing with **Sigstore/Cosign**; **A08:2025 Software or Data Integrity Failures**.
*Lab:* Generate an SBOM for a container image; sign and verify an artifact with Cosign (keyless/OIDC); add a provenance/attestation step and verify it before "deploying."

**Week 12 — Cloud & Container Security**
*Lecture:* Shared-responsibility model; IAM and least privilege; secrets management; container image hardening; Kubernetes basics; **A02:2025 Security Misconfiguration**.
*Lab:* Find and fix misconfigurations — over-permissive IAM policy, exposed storage bucket, secrets in environment variables, and a vulnerable Dockerfile (scan with Trivy, harden the image).

**Week 13 — Security of AI / LLM-Powered Applications**
*Lecture:* The **OWASP Top 10 for LLM Applications (2025)** — prompt injection (LLM01), sensitive information disclosure, insecure output handling, excessive agency, RAG/vector & embedding weaknesses, and unbounded consumption; defenses for AI features in real products.
*Lab:* Perform direct and indirect **prompt-injection** attacks against a sandboxed chatbot to exfiltrate a hidden secret/system prompt; then add input/output guardrails, output validation, and least-privilege tool access, and re-test.

### Unit E — Defense in Practice & Assessment (Weeks 14–15)

**Week 14 — DevSecOps: Putting It Together**
*Lecture:* Logging, monitoring & alerting (**A09:2025**); failing safely / **A10:2025 Mishandling of Exceptional Conditions**; building a secure CI/CD pipeline; vulnerability management and responsible disclosure / coordinated disclosure & bug bounties.
*Lab:* Build a GitHub Actions pipeline that runs SAST (Semgrep), SCA (Trivy/Dependency-Check), and secret scanning (Gitleaks), and **fails the build** on high-severity findings.

**Week 15 — Capstone Presentations & Review**
*Lecture/Studio:* Team capstone presentations; live walkthrough of attack → root cause → fix; course-wide review and the security landscape ahead.
*No new lab* — final project demos and a capture-the-flag style review challenge.

---

## 6. Assessment

| Component | Weight |
|---|---|
| Weekly labs (13 graded) | 35% |
| Two practical exams (CTF-style, hands-on) — Week 7 & Week 13 | 20% |
| Term project (secure build + threat model + remediation report) | 25% |
| Capstone presentation | 10% |
| Participation / quizzes | 10% |

**Term project.** In teams of 2–3, students take a small web/API application, threat-model it, find and document its vulnerabilities, remediate them, generate an SBOM, sign the release artifact, and wire up a security CI pipeline. Deliverables: a threat model, a vulnerability report mapped to CWE/OWASP, the fixed code, and a short demo.

---

## 7. Academic Integrity & Ethics Policy

All offensive techniques are taught for **defensive and authorized testing** purposes only. Students must:

- Attack only the targets provided in the course sandbox or systems for which they hold **explicit written authorization**.
- Never use course material against third-party systems, the university network, or fellow students.
- Follow **responsible/coordinated disclosure** if they incidentally discover a real vulnerability.

Violations are treated as serious academic-integrity and conduct breaches. Students sign an ethics acknowledgment in Week 1.

---

## 8. Reference Materials

**Primary references (free, current):**

- OWASP Top 10:2025 — https://owasp.org/Top10/2025/
- OWASP Top 10 for LLM Applications (2025) — https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- OWASP API Security Top 10 — https://owasp.org/API-Security/
- OWASP Cheat Sheet Series — https://cheatsheetseries.owasp.org/
- MITRE CWE Top 25 & ATT&CK — https://cwe.mitre.org/ , https://attack.mitre.org/
- SLSA (Supply-chain Levels for Software Artifacts) — https://slsa.dev/
- Sigstore — https://www.sigstore.dev/

**Recommended books:**

- *The Web Application Hacker's Handbook* — Stuttard & Pinto.
- *Hacking: The Art of Exploitation* — Jon Erickson (for the memory-safety unit).
- *Alice and Bob Learn Application Security* — Tanya Janca (modern, beginner-friendly).
- *Building Secure and Reliable Systems* — Google/O'Reilly (free online).

**Practice platforms:** PortSwigger Web Security Academy (free), picoCTF, OverTheWire, pwn.college, Hack The Box / TryHackMe (intro tracks).

---

## 9. Mapping to OWASP Top 10:2025

| OWASP 2025 Category | Where covered |
|---|---|
| A01 Broken Access Control | Week 6 |
| A02 Security Misconfiguration | Week 12 |
| A03 Software Supply Chain Failures | Weeks 10–11 |
| A04 Cryptographic Failures | Week 3 |
| A05 Injection | Weeks 4–5 |
| A06 Insecure Design | Weeks 1, 14 |
| A07 Authentication Failures | Week 6 |
| A08 Software or Data Integrity Failures | Week 11 |
| A09 Security Logging & Alerting Failures | Week 14 |
| A10 Mishandling of Exceptional Conditions | Week 14 |

*Plus dedicated modern coverage beyond the core Top 10: API Security (Week 7), memory safety/exploitation (Weeks 8–9), and AI/LLM security (Week 13).*
