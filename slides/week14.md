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

## LLM Top 10 — the big ones

- **LLM01** Prompt injection
- **LLM02** Sensitive info disclosure
- **LLM05** Improper output handling
- **LLM06** Excessive agency
- **LLM08** Vector/embedding weaknesses
- **LLM10** Unbounded consumption

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

## Agentic-AI / MCP risks (2025+)

- Agents call tools (e.g. via **MCP**) → real-world actions
- **Tool poisoning**, **excessive agency**, RCE via tools
- MITRE ATLAS added agent techniques (Oct 2025)

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
