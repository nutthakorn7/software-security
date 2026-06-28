---
marp: true
theme: default
paginate: true
header: "Software Security · Week 4"
---

# Week 4
## Injection & Input Handling
Software Security · Nutthakorn Chalaemwongwan

<!-- Hook: type one quote mark into a login box and become admin — promise that demo. Injection is the oldest trick that still works. Today they exploit it, then fix it for real. ~2 min. -->

---

## Today

- Why injection is still #1-class of bug
- The general injection pattern
- SQL injection — hands-on
- Command injection
- Defenses: parameterized queries + validation
- 🎮 Game: **SQLi Boss Fight**

<!-- Roadmap, 1 min. Tell them the one big idea (data becomes code) unifies SQLi, command injection, and even XSS next week. Lab = exploit DVWA/Juice Shop then patch it. -->

---

## Recap — Week 3

- Crypto failures: ECB, weak hashes, hardcoded keys
- Hashing ≠ encryption ≠ encoding
- Use vetted KDFs (bcrypt/argon2) + authenticated encryption

<!-- 1-min bridge. Last week we protected data at rest; today the attacker sends malicious data IN. Cold-call: "how should we store passwords?" to check W3 stuck. -->

---

## The injection pattern (one idea)

> Untrusted **data** gets interpreted as **code/commands**.

- Attacker input crosses a trust boundary into an interpreter
- SQL, OS shell, LDAP, XPath, template engines, NoSQL…
- Maps to **OWASP A05:2025 Injection**

<!-- This is THE mental model for the whole week — say it twice. Every injection is the same shape: an interpreter can't tell your data from its own instructions. Ask the class to name interpreters in a typical app (DB, shell, template). ~5 min. -->

---

## SQL injection — how it works

```sql
-- vulnerable
"SELECT * FROM users WHERE name = '" + input + "'"
```

- Input `' OR '1'='1` → always true
- Input `'; DROP TABLE users; --` → tampering
- **UNION-based** → read other tables; **blind** → infer bit by bit

<!-- Walk the string-concatenation on the board: show how the quote in the input lands inside the SQL string and breaks out. Distinguish UNION (read other tables in one shot) vs blind (no output → infer via true/false or timing). ~7 min. -->

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

<!-- The worked example — slow down here. Decompose the payload token by token; this is exactly the SQLi Boss Fight round 1. Stress the space after `--` (MySQL needs it) — the #1 reason a student's payload "doesn't work". ~8 min. -->

---

## Real-world impact

- **Equifax (2017):** unvalidated HTTP header → Struts RCE (CVE-2017-5638); 147M people, ~$700M settlement
- **Heartland (2008):** SQLi into payment systems → 130M+ cards
- Bulgaria: data on *almost all adults* leaked via SQLi
- Impact: data leak/modification, full DB control, DoS, reputation

<!-- Make it real — these are careers ended and companies fined. Equifax = a single unpatched input parser. Tie back: every breach here started as "untrusted data interpreted as code". ~4 min. -->

---

## Validate: allow-list, not block-list

- **Allow-list (preferred):** accept only known-good (e.g. `0–9` for a phone)
- **Block-list:** ban known-bad → bypassed by new payloads
- Validate **type · length · range · format**
- Client-side for UX, **server-side for security**

<!-- Key principle that recurs all term. Block-lists always lose (attackers invent new payloads); allow-lists define what's acceptable. Emphasize: validation is defense-in-depth, NOT the primary SQLi fix (that's parameterization — next). ~4 min. -->

---

## Demo / attack surface

- Login forms, search boxes, URL params, JSON fields, headers
- Error messages leak schema → enumeration
- Tooling: Burp Suite, `sqlmap` (sandbox only)

<!-- Point out injection isn't just login boxes — any input reaching an interpreter. Note verbose DB errors are a gift to attackers (schema leakage). Reiterate ethics: sqlmap only on provided sandbox targets. ~3 min. -->

---

## Command injection

```php
system("ping -c 1 " . $_GET['host']);   // vulnerable
// host = 8.8.8.8; cat /etc/passwd
```

- Shell metacharacters: `; | & $() \` >`
- Leads to RCE — full server compromise

<!-- Same pattern, deadlier outcome (RCE = own the server, not just the DB). Walk the metacharacters: `;` chains a second command. Ask: "what does `8.8.8.8; cat /etc/passwd` run?" ~5 min. -->

---

## Upload → RCE (a classic chain)

Attacker uploads `shell.php`:

```php
<?php system($_GET['cmd']); ?>
```

- Then: `.../uploads/shell.php?cmd=ls%20-l` → runs `ls -l`
- One file + one line = arbitrary commands
- **Fix:** validate file type via `mime_content_type()`, allow-list extensions, store uploads outside web root, no execute

<!-- Connects to W1's /upload threat model — now it's a full exploit chain. The webshell is tiny and total. This reappears in the W6 log-reading slide. Stress the layered fix (type + extension + location + no-exec). ~5 min. -->

---

## CWE mapping

- **CWE-89** — SQL injection
- **CWE-78** — OS command injection
- **CWE-20** — improper input validation
- **CWE-77** — command injection (general)

<!-- They map every lab finding to a CWE id. Quick slide — these are the ids to cite in the worksheet. ~1 min. -->

---

## Defenses that actually work

- **Parameterized queries / prepared statements** (the fix for SQLi)
- ORM with bound parameters
- **Allow-list** input validation (type, length, format)
- Avoid shells: use exec APIs with arg arrays, not string concat
- Least-privilege DB accounts

<!-- The payoff. #1 message: parameterization makes data STAY data — the DB never parses it as SQL. For shells, pass an argv array, not a string. Least-privilege limits blast radius if they still get in. ~5 min. -->

---

## ⚔️ Game — SQLi Boss Fight

Tiered challenges in **DVWA / Juice Shop** — easy → "boss" (stacked filters).

1. Clear each level → unlock a flag
2. Boss = bypass a naive filter / WAF
3. **Round 2:** patch endpoints with prepared statements + validation

<!-- Explain before lab: levels escalate (raw → quoted → filtered → boss). Round 2 (patch it) is where the real learning is — and the deliverable. Leaderboard on capture time. Flags are per-student. ~3 min. -->

---

## Lab steps

> 📋 **Worksheet 4** — `labs/week04-injection/worksheet.md` (Part 3) · **kickoff:** `docker compose up` → http://localhost:5000

```bash
docker run --rm -p 80:80 vulnerables/web-dvwa   # optional extra target (or Juice Shop)
```

1. Find an injectable parameter
2. Extract data (UNION / blind)
3. Achieve command injection where present
4. Rewrite the endpoint safely & re-test

<!-- Logistics. Circulate with TAs. Remind: step 4 (rewrite + prove the payload now fails) is graded, not just the exploit. Also kick off the NoteVault project injection task (worksheet). -->

---

## Deliverable

- Findings: each injection point + payload + impact (CWE-mapped)
- The **fixed** code (prepared statements / validation)
- Proof the payload no longer works
- **+ Audit the AI / EiPE / Prompt Problem** (see worksheet)

<!-- Set expectations: before AND after code + proof. The AI-resilient tasks are part of the grade. Q6 of this week's quiz asks for their own payload + personal flag. -->

---

## Key takeaways

- Never build interpreter strings from untrusted input
- Parameterize first; validate as defense-in-depth
- Injection = data treated as code

<!-- Recap in 3 lines. Cold-call: "what's the ONE fix for SQLi?" (parameterized queries). ~2 min. -->

---

# Questions?
Next week: XSS & client-side risks

<!-- Cliffhanger: "Next week the same trick runs in the victim's browser — and skims credit cards." Remind DVWA/Juice Shop ready in their VM. -->
