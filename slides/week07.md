---
marp: true
theme: default
paginate: true
header: "Software Security · Week 7 · Review"
---

# Week 7
## Reflection & Review
Pre-Midterm · Weeks 1–6

---

## Goal today

- Consolidate Weeks 1–6
- 🎯 **Security Jeopardy** team quiz-show
- 🧪 **Mock CTF** in the midterm format
- Build your one-page cheat sheet

---

## Map of the half

| Wk | Topic | One-line |
|---|---|---|
| 1 | Threat modeling | think like an attacker; STRIDE |
| 2 | SDLC & tooling | SAST/DAST/SCA/fuzzing; shift left |
| 3 | Crypto | KDFs, AEAD; avoid ECB/MD5 |
| 4 | Injection | data ≠ code; parameterize |
| 5 | XSS | encode per context; CSP |
| 6 | Auth & access | authorize every request |

---

## 🎯 Security Jeopardy

Categories × point values:

| Threat Modeling | Tooling | Crypto | Injection | XSS | Auth |
|---|---|---|---|---|---|

- Teams pick; wrong answers lose points
- Final wager round

---

## 🧪 Mock CTF

Same format as Week 9:

- Injection (SQLi / command)
- XSS (reflected/stored/DOM)
- Auth / IDOR / JWT
- Crypto (crack a hash / ECB oracle)

> No surprises on exam day.

---

## Common mistakes to avoid

- Confusing encoding vs encryption vs hashing
- "Validated input" ≠ safe → still parameterize
- Authentication without authorization
- Trusting client-side checks

---

## Deliverable

A **one-page cheat sheet** (your own) — may be allowed in the exam at instructor's discretion.

---

# Midterm next week
Wk 8 = written · Wk 9 = hands-on CTF · covers Weeks 1–6
