---
marp: true
theme: default
paginate: true
header: "Software Security · Week 15"
---

# Week 15
## DevSecOps: Putting It Together
Software Security · Nutthakorn Chalaemwongwan

<!-- Final teaching week. Hook: everything we've learned — SAST, SCA, secrets, image scans — only works if it runs automatically on every commit. Today we wire it into one pipeline that blocks bad code. ~2 min. -->

---

## Today

- Security in the CI/CD pipeline
- Logging, monitoring & alerting
- Failing safely
- Vulnerability mgmt & disclosure
- 🎮 Game: **Break the Build** (Red vs Blue)

<!-- Roadmap, 1 min. This week ties the whole course together. Lab is the capstone of the technical units: build the gate (Blue) vs sneak past it (Red). -->

---

## The whole course in one pipeline

- SAST (Wk2) · SCA + image scan (Wk12–13) · secret scanning (Wk2)
- Automated gates instead of one-off scans
- **Secure by Design** as the default

<!-- The synthesis slide — walk back through the term: every tool we used by hand now runs automatically on every PR. Manual scanning doesn't scale and humans forget; pipelines don't. ~4 min. -->

---

## A security gate

```yaml
# .github/workflows/security-ci.yml
- semgrep   # SAST
- trivy     # SCA + image + IaC
- gitleaks  # secrets
# fail build on HIGH/CRITICAL
```

- Upload SARIF → GitHub Security tab

<!-- The worked example — this is the lab's actual pipeline. Three scanners, each catching a class we studied. The KEY line is "fail build on HIGH/CRITICAL": a gate that only warns gets ignored. SARIF feeds findings into the Security tab. ~6 min. -->

---

## Platform option — GitHub Advanced Security

- **CodeQL** code scanning (SAST) on every PR
- **Secret scanning** + push protection
- **Dependabot** for vulnerable deps
- **SonarQube** as a quality/SAST gate alongside

> Same idea as the YAML gate — managed, in the repo.

<!-- The managed equivalent they'll meet in industry. Same concept, less YAML to maintain. Mention SonarQube as the common quality-gate they'll see in internships. ~3 min. -->

---

## Logging, monitoring, alerting

- **A09:2025** — without logs you can't detect or respond
- Log security events (authn, authz failures, anomalies)
- Alert on suspicious patterns

<!-- Shift from prevention to detection. A09 (logging/monitoring failures) is a Top 10 risk because you can't respond to what you can't see. Recall W6: we read attacker actions FROM logs — but only if they were logged. ~4 min. -->

---

## Detection tooling

- **NIDS** — Snort / Suricata (network signatures)
- **HIDS** — OSSEC (host-based)
- **SIEM / stack** — Security Onion bundles them + analysis
- Network visibility: **TAP** (lossless) vs **SPAN** (cheap, can drop)

<!-- Awareness of the defender's toolkit. NIDS watches the wire, HIDS watches the host, SIEM correlates everything. TAP vs SPAN is a practical gotcha: SPAN ports drop packets under load — you miss attacks. Keep brisk. ~3 min. -->

---

## Alerts — the confusion matrix

| | Incident real | No incident |
|---|---|---|
| **Alert fired** | True positive ✅ | False positive |
| **No alert** | **False negative** 💀 | True negative |

- False negative = worst case (missed attack)
- Some false positives are inevitable — tune, don't silence

<!-- Ties back to W2 triage. The danger asymmetry: a false negative = an attack you never saw. But too many false positives → alert fatigue → analysts mute everything → effective false negatives. The skill is TUNING. ~4 min. -->

---

## When something happens (NIST SP 800-86)

**Collection → Examination → Analysis → Reporting**

- Preserve **order of volatility**: memory → temp files → disk → logs
- Failed/success logins: Windows Event **4625 / 4624**

<!-- A taste of incident response / forensics. Order of volatility: capture RAM before you pull the plug — it's gone on shutdown. 4625 (failed) / 4624 (success) are the login events they'd grep in a real investigation. ~4 min. -->

---

## Fail safely

- **A10:2025** — mishandled errors leak info / fail open
- **Fail closed:** deny on error, don't bypass checks
- Don't expose stack traces / secrets in errors

<!-- A design principle that recurs: when something breaks, DENY (fail closed), don't accidentally grant access (fail open). Verbose errors leak schema/secrets (recall W4 error-based enumeration). ~3 min. -->

---

## Vulnerability management & disclosure

- Triage by severity; track to remediation (SLAs)
- **Coordinated disclosure** & bug bounties
- security.txt; a path for researchers to report

<!-- The professional/ethical close: finding a bug is step one; managing it to a fix (with SLAs) is the job. Coordinated disclosure + security.txt = how to receive reports responsibly. Connects to the course ethics theme. ~3 min. -->

---

## 🔴🔵 Game — Break the Build

- **Blue:** build the gate (Semgrep + Trivy + Gitleaks), fail on HIGH/CRITICAL, add security logging that fails closed
- **Red:** submit PRs sneaking in a vuln/secret
- **Score:** Blue per catch, Red per bypass

<!-- The capstone game. Both roles teach: Blue learns to configure gates, Red learns where gates have blind spots. Run it as live PRs against the pipeline. Weekly quiz Q6 asks for one gate they added + what it blocks. ~3 min. -->

---

## Deliverable

> 📋 **Worksheet 15** — `labs/week15-devsecops-pipeline/worksheet.md` (Part 3) · **kickoff:** push `security-ci.yml` → GitHub Actions (· `python sample-service.py`)

- A passing PR that adds the pipeline
- Screenshot: build **failing** on an injected vulnerable dependency
- **+ Audit the AI / EiPE / Prompt Problem** (see worksheet)

<!-- The "build failing" screenshot is the proof the gate actually blocks — a green pipeline that never fails is useless. AI-resilient tasks count. This is also the last weekly quiz. -->

---

## Key takeaways

- Automate security gates — humans forget, pipelines don't
- You can't defend what you don't log
- Fail closed; disclose responsibly

<!-- Recap + course wrap of the technical units. Cold-call: "why must the gate FAIL the build, not just warn?" (warnings get ignored). ~2 min. -->

---

# Questions?
Next week: Capstone studio & CTF warm-up

<!-- Wrap: "Teaching is done — next is your capstone: ship something secure, then defend it in the final CTF. Bring your project to the studio." -->
