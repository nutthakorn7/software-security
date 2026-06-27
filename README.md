# Software Security

A modern, hands-on undergraduate course in software security. Every week pairs a lecture concept with a lab in which students either **break** an intentionally vulnerable target in a safe sandbox or **defend** code they write themselves.

Aligned with **OWASP Top 10 (2025)**, **OWASP Top 10 for LLM Applications (2025)**, the **OWASP API Security Top 10**, **MITRE CWE/ATT&CK**, and the **SLSA** supply-chain framework.

> ⚠️ **Ethics first.** All offensive techniques are taught for **defensive and authorized testing only**. Read [ETHICS.md](ETHICS.md) before starting any lab. Attack only the provided sandbox targets or systems you have **explicit written permission** to test.

---

## Quick start

```bash
git clone <this-repo-url>
cd software-security
# each lab is self-contained:
cd labs/week01-threat-modeling
cat README.md            # follow the lab guide
docker compose up        # (where a target is provided)
```

**Base requirements:** a Linux VM (Kali/Ubuntu), Docker + Docker Compose, Git, and a browser proxy (Burp Suite Community or OWASP ZAP). See [labs/week01-threat-modeling/README.md](labs/week01-threat-modeling/README.md) for the full "Lab 0" setup.

---

## Course at a glance

| Wk | Topic | OWASP 2025 | Lab target |
|----|-------|-----------|------------|
| 1  | Security mindset & threat modeling | A06 | STRIDE model of a sample app |
| 2  | Secure SDLC & tooling | — | Semgrep + Gitleaks on flawed repo |
| 3  | Cryptography used correctly | A04 | Crack weak hashes / ECB oracle |
| 4  | Injection & input handling | A05 | DVWA / Juice Shop |
| 5  | XSS & client-side risks | A05 | Juice Shop (stored/DOM XSS, CSP) |
| 6  | Authn, sessions & access control | A01, A07 | IDOR + weak JWT |
| 7  | API security | A01 | crAPI (BOLA, mass assignment) |
| 8  | Memory-safety vulnerabilities | — | Stack overflow (sandbox binary) |
| 9  | RE & exploitation mitigations | — | gdb / Ghidra format-string |
| 10 | Supply chain I: dependencies | A03 | SCA scan + dependency confusion |
| 11 | Supply chain II: integrity & provenance | A03, A08 | SBOM + Cosign signing (SLSA) |
| 12 | Cloud & container security | A02 | IAM / bucket / Dockerfile hardening |
| 13 | AI / LLM application security | LLM Top 10 | Prompt injection on sandbox chatbot |
| 14 | DevSecOps: putting it together | A09, A10 | Security CI/CD pipeline |
| 15 | Capstone presentations & review | — | Final project + CTF review |

Full details: [syllabus.md](syllabus.md).

---

## Repository layout

```
software-security/
├── README.md                 ← you are here (course landing page)
├── syllabus.md               ← full syllabus, outcomes, assessment, references
├── ETHICS.md                 ← authorized-use policy (read first)
├── slides/                   ← lecture slides (see slides/README.md)
├── labs/
│   ├── week01-threat-modeling/ … week15-capstone/   (each: README + materials)
├── project/                  ← term project brief & rubric
├── scripts/                  ← shared helper scripts
└── .github/workflows/        ← security CI pipeline (also the Week 14 demo)
```

---

## Grading

| Component | Weight |
|---|---|
| Weekly labs (13 graded) | 35% |
| Two practical CTF-style exams (Wk 7 & 13) | 20% |
| Term project | 25% |
| Capstone presentation | 10% |
| Participation / quizzes | 10% |

---

## License

Course materials (text, slides, lab guides): **CC BY-NC-SA 4.0** unless noted. Third-party vulnerable targets (Juice Shop, DVWA, crAPI, etc.) retain their own licenses and are referenced, not redistributed.
