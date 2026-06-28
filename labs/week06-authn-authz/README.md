# Week 6 — Authentication, Sessions & Access Control

**OWASP 2025:** A01 Broken Access Control, A07 Authentication Failures · **CWE:** CWE-639 (IDOR), CWE-287

## Objectives
- Distinguish authentication vs authorization.
- Exploit IDOR and broken access control.
- Identify JWT pitfalls (alg=none, weak secret) and fix token handling.

## 🗺️ Signature game — "IDOR Treasure Hunt + JWT Forgery"
Target: provided app with user objects and JWT auth (or Juice Shop).
1. **IDOR:** change an object/user id in a request to read another user's data.
2. **Privilege escalation:** reach an admin-only function as a normal user.
3. **JWT:** forge a token (none-alg or brute weak HMAC secret).
4. **Fix:** enforce server-side authorization on every object access (RBAC/ABAC), validate JWT alg + signature with a strong secret/key, and add deny-by-default checks.

## Run the local target
```bash
docker compose up        # vulnerable_app.py on http://localhost:5000  (the / page lists endpoints)
```
The fixed version is `solution_app.py`. **macOS:** port 5000 is used by AirPlay Receiver — if you
see `address already in use`, disable *System Settings → General → AirDrop & Handoff → AirPlay
Receiver*, or (recommended) run the labs inside the course VM, where there is no conflict.

## Deliverable
Exploits + the access-control middleware/fixes + re-test results.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
