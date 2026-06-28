# Weekly Agenda & Time Plan (DRAFT for review)

**Standard contact time:** 5 hrs/week = **120 min lecture + 180 min lab** (per syllabus: 2 lecture + 3 lab hrs).
**Quizzes:** 30 min each — Quiz 1 at the **end of Week 6**, Quiz 2 at the **end of Week 15** (last 30 min of those weeks' lab block).

---

## Standard teaching-week template (Weeks 1–6, 10–15)

### Lecture — 120 min
| Time | Block |
|------|-------|
| 0:00–0:10 | Recap last week + today's agenda |
| 0:10–0:55 | Core concepts |
| 0:55–1:05 | Break |
| 1:05–1:35 | Vulnerability deep-dive + real-world cases |
| 1:35–1:55 | Defenses / secure coding |
| 1:55–2:00 | Signature-game briefing → to lab |

### Lab — 180 min
| Time | Block |
|------|-------|
| 0:00–0:15 | Onboarding: stand up target (`docker compose up`), confirm it runs |
| 0:15–1:45 | Exploitation tasks (the signature game) — ~4–5 tasks |
| 1:45–2:25 | Defend / fix task (apply the secure version, prove exploit fails) |
| 2:25–2:50 | **AI-resilient tasks:** Audit-the-AI + EiPE + Prompt Problem (start in class, finish as homework) |
| 2:50–3:00 | Submit worksheet (PDF → Classroom) + push fix (GitHub) + wrap-up |

> **Every teaching week's worksheet** now has four graded parts beyond the lab tasks:
> **Evidence & Integrity** (identity-stamped proof), **Audit the AI** (critique an AI answer),
> **Explain-in-Plain-English** + **Prompt Problem**. Random **viva** spot-checks 2–3 students.
> The live **CTFd scoreboard** (if running) is shown at the start/end of class.

### Quiz weeks (Weeks 6 & 15) — lab shortened to 150 min + 30-min quiz
| Time | Block |
|------|-------|
| 0:00–0:15 | Onboarding |
| 0:15–2:30 | Exploitation + defend tasks (AI-resilient parts move to homework this week) |
| 2:30–3:00 | **Quiz** (Quiz 1 / Quiz 2 — 25 pts, 30 min) |

---

## Per-week time table

| Wk | Type | Lecture | Lab | Quiz | Exam | Total |
|----|------|:---:|:---:|:---:|:---:|:---:|
| 1 | Teach — Threat Modeling | 120 | 180* | — | — | 300 |
| 2 | Teach — SDLC + Fuzzing | 120 | 180 | — | — | 300 |
| 3 | Teach — Cryptography | 120 | 180 | — | — | 300 |
| 4 | Teach — Injection | 120 | 180 | — | — | 300 |
| 5 | Teach — XSS | 120 | 180 | — | — | 300 |
| 6 | Teach — Auth & Access | 120 | 150 | **30** | — | 300 |
| 7 | 🔁 Review (pre-midterm) | — | — | — | — | 300 |
| 8 | 📝 Midterm — Written | — | — | — | 120 | 120 |
| 9 | 📝 Midterm — CTF | — | — | — | 150 | 150 |
| 10 | Teach — API Security | 120 | 180 | — | — | 300 |
| 11 | Teach — Memory Safety | 120 | 180 | — | — | 300 |
| 12 | Teach — Supply Chain | 120 | 180 | — | — | 300 |
| 13 | Teach — Cloud/Container | 120 | 180 | — | — | 300 |
| 14 | Teach — AI/LLM | 120 | 180 | — | — | 300 |
| 15 | Teach — DevSecOps | 120 | 150 | **30** | — | 300 |
| 16 | Capstone Studio | — | 300 | — | — | 300 |
| 17 | 🔁 Review (pre-final) | — | — | — | — | 300 |
| 18 | 📝 Final — Written | — | — | — | 150 | 150 |
| 19 | 📝 Final — CTF + Demos | — | — | — | 240 | 240 |

*W1 lab includes Lab 0 environment setup (~45 min) — onboarding block is longer.

---

## Special-week agendas

### Week 7 & 17 — Review (300 min)
*(Quiz already taken at the end of Week 6 / 15.)*
| Time | Block |
|------|-------|
| 0:00–1:30 | Security Jeopardy team review |
| 1:30–1:45 | Break |
| 1:45–4:30 | Mock CTF (exact format of the upcoming exam) |
| 4:30–5:00 | Debrief: common mistakes + exam logistics |

### Week 8 / 18 — Written exam
- Single block: **120 min (midterm) / 150 min (final)**. No lab.

### Week 9 — Midterm CTF practical (150 min)
- 0:00–0:10 rules + target check · 0:10–2:30 solve challenges · submit flags.

### Week 16 — Capstone Studio (300 min)
| Time | Block |
|------|-------|
| 0:00–2:00 | Team WIP demos (attack → root cause → fix) + peer review |
| 2:00–2:15 | Break |
| 2:15–4:45 | Practice CTF tournament (previews Week 19) |
| 4:45–5:00 | Feedback + finalize checklist before the final |

### Week 19 — Final CTF + project demos (240 min)
| Time | Block |
|------|-------|
| 0:00–2:30 | Capstone CTF tournament (whole term) |
| 2:30–4:00 | Graded final project demos (10-min demo + 5-min Q&A per team) |

---

## ⚠️ Note (drift to resolve)
Current `worksheet.md` Part-3 durations vary (90–180 min). This plan standardizes **lab = 180 min** for every teaching week. Weeks 1–3 worksheets are currently lighter (~90–95 min of tasks) and would need a few more tasks / extension activities to fill the 180-min block.
