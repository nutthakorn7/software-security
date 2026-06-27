# Week 5 — Cross-Site Scripting (XSS) & Client-Side Risks

**OWASP 2025:** A05 Injection · **CWE:** CWE-79 (XSS), CWE-352 (CSRF)

## Objectives
- Distinguish reflected, stored, and DOM-based XSS.
- Understand the same-origin policy, cookies (SameSite), and CSP.
- Build a CSRF PoC and defend against it.

## Lab — Juice Shop
1. Land a **stored** XSS and a **DOM** XSS payload.
2. Steal/abuse a session via the XSS (sandbox only).
3. Build a CSRF page that performs a state-changing request.
4. **Fix:** add contextual output encoding, a strict Content-Security-Policy, `SameSite=Lax/Strict` cookies, and CSRF tokens; verify the attacks fail.

## Deliverable
Working payloads + CSP/encoding/CSRF fixes + screenshots of blocked attacks.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html
