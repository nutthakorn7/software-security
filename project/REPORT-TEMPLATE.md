# Term Project Report — Secure Build

> Fill in every section. Keep the headings. Total **100 pts** (see rubric at the end).
> This is **team work** (2–3). Do not share your report with other teams.

## Cover

| Field | Value |
|---|---|
| Team name | |
| Members (name + ID) | |
| Target application | |
| Repository URL | |
| Date | |

## AI-tool usage disclosure
*Academic integrity: state how you used any AI tools (ChatGPT, Copilot, etc.) — e.g. searching, coding, translating, drafting. "None" is a valid answer.*

| Tool | How it was used |
|---|---|
| | |

---

## 1. Executive Summary
*(½ page) What the app is, how many findings by severity, and the overall risk before vs. after your fixes.*

---

## 2. System Scope & Function
- What the application does; in-scope components and endpoints.
- **Data-Flow Diagram (DFD):** processes, data stores, external entities, **trust boundaries** (insert image).

---

## 3. Threat Model — STRIDE  *(20 pts)*

| Element / data flow | S | T | R | I | D | E | Top threat & mitigation |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

*Then rank the top 5 risks by likelihood × impact.*

---

## 4. Vulnerability Findings  *(25 pts)*

One block per finding (copy as needed):

### Finding F-01 — Unsalted MD5 Password Hashing
| Field | Value |
|---|---|
| CWE | CWE-916 / CWE-327 |
| OWASP 2025 | A04 Cryptographic Failures |
| Severity | High |
| Location | `project/starter-app/app.py:67-69`, `116-117`, and `128-130` |
| Reproduction | Obtain the two unsalted MD5 values from NoteVault's `seed()` data and run Hashcat in raw-MD5 mode (`hashcat -m 0`). The Week 3 exercise recovered both seeded passwords through offline guessing. |
| Impact | Anyone who obtains the user table can test password guesses quickly without contacting the application. Recovered passwords can compromise NoteVault accounts and may create additional risk if a user reused the same password elsewhere. |
| Evidence | Week 3 Hashcat result shown below |

**Recommended mitigation:** Replace MD5 with Argon2id for new passwords and use rehash-on-login to migrate a correctly verified legacy MD5 record. Argon2id applies a unique salt and deliberately expensive time and memory costs, making offline guessing substantially harder.

![NoteVault seeded password hashes recovered in the authorized Week 3 lab](../labs/week03-cryptography/image-task5-notevault-hashes.png)

---

### Finding F-02 — SQL Injection in Login and Note Search
| Field | Value |
|---|---|
| CWE | CWE-89 |
| OWASP 2025 | A05 Injection |
| Severity | High |
| Location | Original vulnerable queries: `project/starter-app/app.py:128-130` and `178-179`. Fixed queries: `128-131` and `179-182`. |
| Reproduction | The original source formatted request values directly into the `/login` and `/search` SQL statements. The fixed local build was tested with username `alice'--` on `/login` and search term `' UNION SELECT id,title,body FROM notes--` on `/search`. |
| Impact | An attacker may bypass authentication or read note data outside the intended search. Successful exploitation could expose user data and weaken the application's access controls. |
| Evidence | Direct before/after code evidence at the locations above. Manual verification against the actual NoteVault container returned HTTP 401 and `login failed` for the login payload; the UNION search returned an empty list and exposed no other users' notes. No Week 4 lab screenshot is presented as NoteVault evidence. |

**Recommended mitigation:** Replace both formatted SQL strings with SQLite parameterized queries. Bind the login values as `(username, password_hash)` and bind the search pattern as `(user, "%" + term + "%")` so request data cannot change the SQL structure.

---

## 5. Remediation  *(25 pts)*

Per finding: the fix, **before/after** code, and the commit that implements it.

### Fix for F-01
```diff
- vulnerable line
+ fixed line
```
- **Why this fixes it:** …
- **Commit:** `<hash>`
- **Proof the exploit now fails:** (screenshot)

### Fix for F-02
```diff
- q = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (
-     username, hashlib.md5((password or "").encode()).hexdigest())
- row = con.execute(q).fetchone()
+ row = con.execute(
+     "SELECT * FROM users WHERE username = ? AND password = ?",
+     (username, hashlib.md5((password or "").encode()).hexdigest()),
+ ).fetchone()

- q = "SELECT id,title,body FROM notes WHERE owner='%s' AND body LIKE '%%%s%%'" % (user, term)
- rows = con.execute(q).fetchall()
+ rows = con.execute(
+     "SELECT id,title,body FROM notes WHERE owner = ? AND body LIKE ?",
+     (user, "%" + term + "%"),
+ ).fetchall()
```
- **Why this fixes it:** SQLite receives a fixed query structure and binds each value as data, so quotes, comments, and UNION text cannot become SQL syntax.
- **Commit:** `<ADD AFTER THE NoteVault F-02 FIX IS IMPLEMENTED AND COMMITTED>`
- **Proof the exploit now fails:** The actual NoteVault container preserved normal behavior: `alice` login returned HTTP 302 and the authenticated search for `milk` returned `groceries: milk, eggs`. The login SQLi returned HTTP 401 with `login failed`, while the authenticated UNION search returned HTTP 200 with no rows and did not expose the admin notes.

---

## 6. Supply-Chain Hardening  *(15 pts)*
- **SBOM** (CycloneDX) generated — attach `sbom.json`, note component count.
- **Artifact signed & verified** with Cosign — paste the `cosign verify` output.
- One-paragraph **SLSA** self-assessment (which level, why).

---

## 7. Security CI Pipeline  *(10 pts)*
- Link to the GitHub Actions workflow (SAST + SCA + secret scanning).
- Screenshot of a build **failing** on a HIGH/CRITICAL finding.
- How the gate is configured (what fails the build).

---

## 8. Conclusion & Reflection  *(5 pts — clarity)*
- Residual risks and what you'd harden next.
- Lessons learned.

---

## Appendix
- Tools used, references (OWASP/CWE links), and the team's task split.

---

## Grading rubric (100)

| Criterion | Pts |
|---|---|
| Threat model quality & completeness (§3) | 20 |
| Vulnerability findings — correctness, CWE/OWASP mapping, depth (§4) | 25 |
| Remediation quality — correct, minimal, well-explained (§5) | 25 |
| Supply-chain hardening — SBOM + signing + provenance (§6) | 15 |
| CI pipeline — works, fails build appropriately (§7) | 10 |
| Presentation & report clarity (§1, §8) | 5 |

*All work stays within the [ethics policy](../ETHICS.md).*
