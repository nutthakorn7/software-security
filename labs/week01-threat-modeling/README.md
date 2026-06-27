# Week 1 — Security Mindset & Threat Modeling

**OWASP 2025:** A06 Insecure Design · **CWE focus:** CWE-1059 (design)

## Objectives
- Explain the CIA triad, trust boundaries, and attack surface.
- Build a data-flow diagram (DFD) and apply STRIDE to a real app.
- Navigate the OWASP Top 10, MITRE CWE, and ATT&CK.
- Frame the course with **"Secure by Design"** (CISA) and the industry shift to memory-safe languages.

## 🎲 Signature game — "Elevation of Privilege"
Play Microsoft's free STRIDE threat-modeling card deck against the sample app's DFD — each valid threat scores a point.

## Lab 0 — Environment setup (do once)
1. Install VirtualBox/UTM + a Kali or Ubuntu VM.
2. Install Docker + Docker Compose inside the VM.
3. Install a browser proxy: Burp Suite Community **or** OWASP ZAP.
4. Verify: `docker run hello-world` and `git --version`.

## Lab 1 — Threat-model a sample app
You are given a small web app (source provided by instructor).
1. Draw a DFD: processes, data stores, external entities, and trust boundaries.
2. For each element, enumerate **S**poofing, **T**ampering, **R**epudiation, **I**nfo disclosure, **D**oS, **E**levation.
3. Rank the top 5 threats by likelihood × impact.
4. Propose one mitigation per top threat.

## Deliverable
A 2–3 page threat model (DFD image + STRIDE table + top-5 risk ranking).

## References
- https://owasp.org/Top10/2025/
- https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
