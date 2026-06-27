---
marp: true
theme: default
paginate: true
header: "Software Security · Week 14"
---

# Week 14
## Security of AI / LLM-Powered Applications
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Where AI features add attack surface
- OWASP **LLM Top 10 (2025)**
- Prompt injection (direct + indirect)
- Agentic-AI / MCP risks
- 🎮 Game: **Gandalf Challenge**

---

## Why a whole week on AI

- LLMs now sit inside real products & agents
- New, fast-moving attack surface
- OWASP LLM Top 10 + MITRE ATLAS

---

## OWASP LLM Top 10 (2025)

| | | |
|---|---|---|
| LLM01 Prompt Injection | LLM02 Sensitive Info Disclosure | LLM03 Supply Chain |
| LLM04 Data/Model Poisoning | LLM05 Improper Output Handling | LLM06 Excessive Agency |
| **LLM07 System Prompt Leakage** | LLM08 Vector/Embedding | LLM09 Misinformation |
| LLM10 Unbounded Consumption | | |

> **New in 2025:** LLM07 System Prompt Leakage · LLM08 promoted (RAG everywhere) · LLM10 replaces "DoS" with runaway *cost*.

---

## Prompt injection

> Untrusted text overrides the system's instructions — injection, again.

- **Direct:** user tells the bot to ignore its rules
- **Indirect:** malicious instructions hidden in a fetched doc / web page (RAG)

---

## Improper output handling

- Model output flows unsanitized into HTML/SQL/shell
- → XSS / injection downstream
- Treat LLM output as **untrusted input**

---

## Real-world incidents

- **Bing Chat "Sydney" (2023):** hidden page text overrode system rules
- **EchoLeak (2025):** *zero-click* indirect injection in M365 Copilot → data exfil (CVE-2025-32711)
- **Auto-GPT wallet theft (2024):** injected web/email content made an agent move crypto
- **Résumé injection:** hidden white text inflated an AI screening score

> Injection needs no exploit code — just text the model trusts.

---

## Agentic-AI / MCP risks (2025+)

- Agents call tools (e.g. via **MCP**) → real-world actions
- **Tool poisoning**, **excessive agency**, RCE via tools
- MITRE ATLAS added agent techniques (Oct 2025)
- Research: **43%** of public MCP servers had command-injection flaws

---

## Real MCP/agent incidents (2025)

- **Supabase × Cursor:** privileged agent read a support ticket with injected SQL → leaked integration tokens (privileged access + untrusted input + exfil channel)
- **Invariant Labs:** a malicious trivia MCP server's *tool description* hijacked a trusted WhatsApp MCP → exfiltrated chats
- **MCPoison (CVE-2025-54136):** approved-then-swapped MCP config in Cursor → silent RCE on every session

> The danger pattern: **privilege + untrusted input + an outbound channel.**

---

## Defenses

- Input/output **guardrails** + content filtering
- Strict output **schemas/validation**; encode before downstream use
- **Least-privilege tool access** + human-in-the-loop for sensitive actions
- Rate/consumption limits; isolate untrusted content in RAG

---

## 🧙 Game — Gandalf Challenge

1. Beat Gandalf levels via **direct + indirect prompt injection** → exfiltrate the secret (leaderboard by level)
2. Demo **tool poisoning / excessive agency** on an agent with tools
3. **Round 2:** add guardrails + least-privilege tools, re-test

---

## Deliverable

- Attack log (which injection beat which level)
- Mitigations + re-test results
- Least-privilege agent/MCP tool design

---

## Key takeaways

- Prompt injection = injection; LLM output = untrusted
- Constrain agency: least-privilege tools, human approval
- The field moves monthly — track OWASP LLM + ATLAS

---

# Questions?
Next week: DevSecOps — putting it together
