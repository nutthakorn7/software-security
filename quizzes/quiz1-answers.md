# Quiz 1 — Answer Key (Weeks 1–6)

> Instructor copy. Total 25 pts.

## Part A — Multiple Choice (10 × 1 pt)

| Q | Ans | Note |
|---|-----|------|
| 1 | **b** | I = Information disclosure → Confidentiality |
| 2 | **c** | parameterized/prepared statements |
| 3 | **b** | block patterns leak (ECB penguin) |
| 4 | **b** | SAST = static, no execution |
| 5 | **c** | stored/persistent XSS |
| 6 | **b** | `alg:none` → CWE-347 broken signature verification |
| 7 | **b** | IDOR (A01 Broken Access Control) |
| 8 | **d** | salted slow KDF |
| 9 | **b** | mutate inputs, track coverage/crashes |
| 10 | **b** | accept only known-good |

## Part B — Short Answer (3 × 3 pts)

11. **Trust boundary** — the line where data/control passes between components of different privilege or trust (e.g. browser → server, app → DB, user input → interpreter). Example: the boundary between an untrusted HTTP request and the application. *(3 pts: definition 2 + example 1.)*

12. Each output context has different special characters/parsers: HTML body needs `<>&` encoding, HTML attribute needs quote handling, JS context needs JS-string escaping, URL needs percent-encoding. Wrong/absent encoding → **XSS** (e.g. encoding for HTML but injecting into a `<script>` block still executes). *(3 pts: context idea 2 + consequence 1.)*

13. **Authentication** = verifying *who* you are (login, MFA) → failures: weak passwords, `alg:none` JWT, session fixation (A07). **Authorization** = what you're *allowed* to do → failures: IDOR, privilege escalation, missing access checks (A01). *(3 pts: 1.5 each.)*

## Part C — Spot the Vulnerability (2 × 3 pts)

14. **SQL injection (CWE-89)** — user input concatenated into the query. **Fix:** parameterized query:
```python
db.execute("SELECT * FROM users WHERE name = ?", (request.args["name"],))
```
*(flaw 1.5 + fix 1.5)*

15. **Broken signature verification (CWE-347)** — `verify_signature: False` trusts an unverified, attacker-controllable token. **Fix:** verify with a strong key + fixed algorithm and validate claims:
```python
token = jwt.decode(t, KEY, algorithms=["HS256"], audience=AUD)
```
*(flaw 1.5 + fix 1.5)*
