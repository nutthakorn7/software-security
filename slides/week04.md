---
marp: true
theme: default
paginate: true
header: "Software Security · Week 4"
---

# Week 4
## Injection & Input Handling
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Why injection is still #1-class of bug
- The general injection pattern
- SQL injection — hands-on
- Command injection
- Defenses: parameterized queries + validation
- 🎮 Game: **SQLi Boss Fight**

---

## Recap — Week 3

- Crypto failures: ECB, weak hashes, hardcoded keys
- Hashing ≠ encryption ≠ encoding
- Use vetted KDFs (bcrypt/argon2) + authenticated encryption

---

## The injection pattern (one idea)

> Untrusted **data** gets interpreted as **code/commands**.

- Attacker input crosses a trust boundary into an interpreter
- SQL, OS shell, LDAP, XPath, template engines, NoSQL…
- Maps to **OWASP A05:2025 Injection**

---

## SQL injection — how it works

```sql
-- vulnerable
"SELECT * FROM users WHERE name = '" + input + "'"
```

- Input `' OR '1'='1` → always true
- Input `'; DROP TABLE users; --` → tampering
- **UNION-based** → read other tables; **blind** → infer bit by bit

---

## Auth bypass — anatomy of one payload

Inject into the **username** field:

```text
' OR 1 = 1 LIMIT 1; -- a
```

```sql
SELECT * FROM users WHERE user = '' OR 1 = 1 LIMIT 1; -- a AND password = '';
```

- `'` closes the string · `OR 1=1` always true
- `LIMIT 1` → satisfies a `num_rows == 1` check
- `-- a` comments out the password check (note the space!)

---

## Real-world impact

- **Equifax (2017):** unvalidated HTTP header → Struts RCE (CVE-2017-5638); 147M people, ~$700M settlement
- **Heartland (2008):** SQLi into payment systems → 130M+ cards
- Bulgaria: data on *almost all adults* leaked via SQLi
- Impact: data leak/modification, full DB control, DoS, reputation

---

## Validate: allow-list, not block-list

- **Allow-list (preferred):** accept only known-good (e.g. `0–9` for a phone)
- **Block-list:** ban known-bad → bypassed by new payloads
- Validate **type · length · range · format**
- Client-side for UX, **server-side for security**

---

## Demo / attack surface

- Login forms, search boxes, URL params, JSON fields, headers
- Error messages leak schema → enumeration
- Tooling: Burp Suite, `sqlmap` (sandbox only)

---

## Command injection

```php
system("ping -c 1 " . $_GET['host']);   // vulnerable
// host = 8.8.8.8; cat /etc/passwd
```

- Shell metacharacters: `; | & $() \` >`
- Leads to RCE — full server compromise

---

## Upload → RCE (a classic chain)

Attacker uploads `shell.php`:

```php
<?php system($_GET['cmd']); ?>
```

- Then: `.../uploads/shell.php?cmd=ls%20-l` → runs `ls -l`
- One file + one line = arbitrary commands
- **Fix:** validate file type via `mime_content_type()`, allow-list extensions, store uploads outside web root, no execute

---

## CWE mapping

- **CWE-89** — SQL injection
- **CWE-78** — OS command injection
- **CWE-20** — improper input validation
- **CWE-77** — command injection (general)

---

## Defenses that actually work

- **Parameterized queries / prepared statements** (the fix for SQLi)
- ORM with bound parameters
- **Allow-list** input validation (type, length, format)
- Avoid shells: use exec APIs with arg arrays, not string concat
- Least-privilege DB accounts

---

## ⚔️ Game — SQLi Boss Fight

Tiered challenges in **DVWA / Juice Shop** — easy → "boss" (stacked filters).

1. Clear each level → unlock a flag
2. Boss = bypass a naive filter / WAF
3. **Round 2:** patch endpoints with prepared statements + validation

---

## Lab steps

```bash
docker run --rm -p 80:80 vulnerables/web-dvwa   # or Juice Shop
```

1. Find an injectable parameter
2. Extract data (UNION / blind)
3. Achieve command injection where present
4. Rewrite the endpoint safely & re-test

---

## Deliverable

- Findings: each injection point + payload + impact (CWE-mapped)
- The **fixed** code (prepared statements / validation)
- Proof the payload no longer works

---

## Key takeaways

- Never build interpreter strings from untrusted input
- Parameterize first; validate as defense-in-depth
- Injection = data treated as code

---

# Questions?
Next week: XSS & client-side risks
