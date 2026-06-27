# Week 13 — Security of AI / LLM-Powered Applications  (Practical Exam #2)

**OWASP Top 10 for LLM Applications (2025):** LLM01 Prompt Injection · LLM02 Sensitive Info Disclosure · LLM05 Improper Output Handling · LLM06 Excessive Agency · LLM08 Vector/Embedding Weaknesses · LLM10 Unbounded Consumption

## Objectives
- Explain the LLM Top 10 and where AI features add attack surface.
- Perform direct and indirect prompt injection.
- Add guardrails: input/output validation, least-privilege tools, output handling.

## Lab — sandboxed vulnerable chatbot
1. **Direct prompt injection:** override the system prompt to reveal a hidden secret (e.g. Gandalf-style levels).
2. **Indirect injection:** plant a malicious instruction in a document the bot ingests (RAG) and trigger it.
3. **Improper output handling:** show model output flowing unsanitized into a downstream action (XSS/command).
4. **Fix:** input/output guardrails, strict output schemas/validation, least-privilege tool access, and rate/consumption limits; re-test.

## Deliverable + Exam
Attack log + mitigations + re-test. A timed prompt-injection challenge is graded as Practical Exam #2.

## References
- https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/
- https://gandalf.lakera.ai/
