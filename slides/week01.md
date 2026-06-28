---
marp: true
theme: default
paginate: true
header: "Software Security · Week 1"
---

# Week 1
## Security Mindset & Threat Modeling
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- What "secure" means (CIA)
- Attacker vs. defender mindset
- Trust boundaries & attack surface
- STRIDE + the OWASP/MITRE landscape
- **Secure by Design**
- 🎲 Game: **Elevation of Privilege** · Lab 0 setup

---

## Welcome — how this course works

- Every week: **lecture concept → hands-on game/lab**
- You'll *break* sandbox targets **and** *defend* your own code
- Ethics first: attack only provided targets (see `ETHICS.md`)

---

## What does "secure" mean?

- **Confidentiality** — only the right people can read data
- **Integrity** — data/code can't be tampered with undetected
- **Availability** — the system is there when needed

> Security is not a feature you add — it's a property you design for.

---

## Attacker vs. defender mindset

- Defenders must close **every** hole
- Attackers need **one**
- Think in **misuse cases**, not just use cases
- "What can go wrong here?" at every boundary

---

## Trust boundaries & attack surface

- **Trust boundary:** where data crosses between components of different privilege
- **Attack surface:** every input an attacker can reach
  - HTTP params, headers, cookies, file uploads, APIs, env vars, dependencies

---

## STRIDE

| Letter | Threat | Property violated |
|---|---|---|
| **S** | Spoofing | Authentication |
| **T** | Tampering | Integrity |
| **R** | Repudiation | Non-repudiation |
| **I** | Information disclosure | Confidentiality |
| **D** | Denial of service | Availability |
| **E** | Elevation of privilege | Authorization |

---

## The landscape you'll use all term

- **OWASP Top 10 (2025)** — most critical web risks
- **OWASP LLM Top 10 (2025)** — AI app risks
- **MITRE CWE** — weakness catalog
- **MITRE ATT&CK** — adversary tactics & techniques

---

## Secure by Design

- **CISA "Secure by Design":** safety is the vendor's job, on by default
- Shift from "patch later" to "design out the bug class"
- Industry/government push toward **memory-safe languages** (more in Wk 11)

---

## Insecure Design (A06:2025)

- Some bugs are *design* flaws, not coding slips
- Missing trust boundary, no rate limiting, dangerous defaults
- Threat modeling catches these *before* code exists

---

## 🎲 Game — Elevation of Privilege

- Microsoft's free **STRIDE card deck**
- Play cards against the sample app's data-flow diagram
- Each valid threat = a point
- Outcome: a team-built STRIDE model

---

## Lab 0 — Environment setup (once)

1. VirtualBox/UTM + Kali or Ubuntu VM
2. Docker + Docker Compose inside the VM
3. Browser proxy: Burp Suite Community **or** OWASP ZAP
4. Verify: `docker run hello-world`, `git --version`

---

## Lab 1 — Threat-model a sample app

1. Run the provided app (`docker compose up`)
2. Draw a **DFD**: processes, stores, external entities, trust boundaries
3. Apply **STRIDE** to each element
4. Rank top 5 risks (likelihood × impact) + one mitigation each

**Deliverable:** 2–3 page threat model

---

## Using AI in this course

- AI is allowed — and you must **disclose** how you used it
- But AI **hallucinates** APIs/CVEs and writes **insecure code**
- You're graded on understanding, not on the answer:
  - random **live re-demos** — explain it or score zero
  - your **flags are unique** to you — copying is traceable
  - every lab has an **“Audit the AI”** task: find what its answer gets wrong
- Use AI to **learn faster** — never to **skip the thinking**

---

## Key takeaways

- Design for security; don't bolt it on
- Attackers need one gap — model the whole surface
- STRIDE + DFD = a repeatable way to find design flaws

---

# Questions?
Next week: Secure SDLC, tooling & fuzzing
