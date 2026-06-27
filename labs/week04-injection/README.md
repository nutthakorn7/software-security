# Week 4 — Injection & Input Handling

**OWASP 2025:** A05 Injection · **CWE:** CWE-89 (SQLi), CWE-78 (command injection)

## Objectives
- Exploit SQL and command injection.
- Explain why parameterized queries defeat injection.
- Apply input validation and output handling correctly.

## Lab — DVWA / Juice Shop
```bash
# DVWA
docker run --rm -it -p 80:80 vulnerables/web-dvwa
# OR Juice Shop
docker run --rm -p 3000:3000 bkimminich/juice-shop
```
1. Extract data via SQLi (e.g. `' OR 1=1 -- `, UNION-based).
2. Achieve command injection on a vulnerable endpoint.
3. **Fix:** rewrite the endpoints with prepared statements / parameterized APIs and allow-list validation; re-test to confirm the payloads now fail.

## Deliverable
PoC payloads + the patched code + proof the fix blocks them.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
