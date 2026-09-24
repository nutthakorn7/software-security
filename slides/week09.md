---
marp: true
theme: default
paginate: true
header: "Software Security · Week 9 · Midterm"
---

# Week 9
## Midterm — Hands-on CTF Practical
Covers Weeks 1–6 · Individual

<!-- Proctor deck. BEFORE class: graded flags come only from each student's own hosted CTFd instance (see docs/lesson-plans/week09-midterm-practical.md §3.1) — local Docker is practice and serves demo flags. Confirm in the first 5 min that everyone can log in to CTFd and reach a spawned instance. -->

---

## Format

- Timed, in the sandbox
- Each solved challenge = a flag = points
- Partial credit for documented progress

<!-- State the time (150 min) + that graded flags are per-student and come only from your own hosted instance (a flag issued to someone else is traceable via seed_flags.py verify). A local FLAG{..._demo} flag is not a valid submission. Submit via CTFd or the Form. ~2 min. -->

---

## Challenge areas — 100 pts, 7 challenges

![Four categories: Injection (30 pts) from Week 4 — Boolean Bypass SQLi and Shell Out command injection, 15 each. Auth and Access Control (30 pts) from Week 6 — Not Your Order IDOR and Forge Ahead JWT forgery, 15 each. Cryptography (25 pts) from Week 3 — Crack It password cracking (15) and Penguin ECB oracle (10). XSS (15 pts) from Week 5 — Pop the Alert, stored only. Not against DVWA or Juice Shop — this course's own apps, the only targets a flag is actually planted on.](img/ctf-categories.svg)

<!-- Same targets as the W7 mock, weighted unevenly — don't present these as equal-weight. DVWA appears in this week's own README but isn't deployed anywhere in ctf.md's target list — correct it here so no one hunts for a container that isn't running. Juice Shop is similar: ctf.md's Targets line used to list it as an "(or OWASP Juice Shop)" alternative for the XSS slot, but no flag was ever planted there (seed_flags.py / the answer key only seed this course's own apps) — so it wasn't actually part of the graded surface, and that line has been removed from ctf.md. If a student asks, week05's app is the only XSS target; Juice Shop earns no credit. Extra challenges available in exams/item-bank.md (CTF pool) if you rotate. -->

---

## Rules

- Sandbox targets only — ethics policy applies
- Submit **3 fields per challenge**: flag/proof, payload/command, one-line mitigation
- No collaboration

<!-- Stress: attack only provided targets; three separate required fields, not one combined note — the mitigation line is graded separately from the method. Then start the clock. -->

---

# Submit your flags
Next: Week 10, API security

<!-- Close: collect submissions; grade with the answer key + seed_flags.py verify for copied flags (hosted-instance flags only — a _demo flag proves nothing). Preview W10 (APIs). -->
