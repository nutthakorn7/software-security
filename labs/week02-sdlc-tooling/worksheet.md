# Worksheet 2 — Secure SDLC & Tooling (3 hrs)

> **Course:** Software Security (KOSEN69) · **Week 2**
> **Aligned to:** OWASP 2025 (A05 Injection [CWE-89, CWE-78], A04 Cryptographic Failures [CWE-327], A02 Security Misconfiguration [CWE-798, CWE-489]) · CWE-798, CWE-89, CWE-78, CWE-327, CWE-489
> **Signature game:** "Bug Triage Race" (scan → triage; score = true positives − misclassified)

> **Ethics note:** The scanners run only against the provided `vulnerable-repo/` on your own machine. Do not point SAST/secret scanners at third-party repos or production systems without authorization. Treat any secret you find here as fake lab data.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|
| SORRAWIT THANAKHWANG | 6531503080 | 2026-09-07 | NONE |

AI disclosure: used Claude (Anthropic) as a teaching/drafting assistant throughout this worksheet (Part 2, all Task 0-8 write-ups, Part 4, Evidence & Integrity, Audit the AI, and EiPE/Prompt Problem) — concepts were explained interactively before each answer was drafted, and every drafted answer was reviewed and approved by the student before being recorded. The actual scans (Semgrep, Gitleaks, Trivy), the fuzzing run, the CI workflow debugging, and the code fix in Task 8 were run by the student (with the CI job-log diagnosis assisted by AI using the `gh` CLI); every claim about scan results was verified by re-running the tools, not just written from memory. See the "Audit the AI" section for the specific AI-output critique performed.

## Part 2 — Lecture Questions
Answer in your own words (2–4 sentences each).
1. Distinguish SAST, DAST, and SCA — what does each see, and when in the SDLC does each run?

   SAST (Semgrep here) reads the source code itself without running it, so it can point at an exact file:line but doesn't know what happens at runtime — it runs earliest, right when code is written/committed. DAST attacks a *running* app from the outside (like a black-box pentest), so it sees real request/response behavior but can't tell you which line caused it — it runs later, against a deployed/staging build. SCA (e.g. Trivy) doesn't look at your code at all; it checks your dependency list (`requirements.txt`, lockfiles) against known-CVE databases, so it catches vulnerable third-party libraries that SAST/DAST would never flag — it runs at build time whenever dependencies change.

2. What is secret scanning, and why do hardcoded secrets keep ending up in repos?

   Secret scanning (Gitleaks here) searches source code and commit history for patterns that look like credentials — API keys, passwords, tokens — using regex/entropy rules, e.g. it caught `AWS_SECRET_ACCESS_KEY` and `DB_PASSWORD` in `app.py` under rule `generic-api-key`. Hardcoded secrets keep happening because pasting a real key straight into code is the fastest way to get something working locally, and once it's committed it stays in git history forever even if the line is later deleted — the fix has to be "rotate the key," not just "delete the line."

3. What does "shift-left / DevSecOps" mean in practice for a CI pipeline?

   "Shift-left" means running security checks as early in the SDLC as possible — SAST/secret-scanning at write-code/commit time — instead of only at the end right before release, because a bug caught while you're still writing the line is a one-line fix, while the same bug caught in production is an incident. DevSecOps means these scans (Semgrep, Gitleaks, Trivy) are wired directly into the CI pipeline so every push/PR gets checked automatically, rather than security being a manual review that happens once at the end.

4. Why is coverage-guided fuzzing considered the dominant modern bug-finding technique?

   Coverage-guided fuzzing (like libFuzzer in Task 4) instruments the binary so it can see which code paths each random input actually reaches, then mutates inputs that discover *new* paths instead of wasting time re-exploring the same ones — this lets it find deep, weird edge cases (like the `data[3]` out-of-bounds read in `harness.c`) that a human writing test cases would never think to try. It's "dominant" because it needs no security expertise to run and it finds real memory-safety bugs that pattern-matching tools like SAST structurally cannot see.

5. Define true positive vs. false positive in scanner triage, and why misclassifying both directions is costly.

   A true positive is a scanner finding that is a real, exploitable vulnerability; a false positive is a finding that looks like a match to the tool's rule but isn't actually exploitable in context (e.g. user input that's already validated elsewhere). Misclassifying a true positive as a false positive means a real vulnerability ships to production; misclassifying a false positive as a true positive wastes developer time chasing a non-issue and, done repeatedly, trains the team to start ignoring scanner output altogether ("alert fatigue"), which then lets real findings slip through too.

![A left to right SDLC pipeline showing SAST at write code, secret scanning at commit, SCA and fuzzing at build, and DAST at deploy, with what each tool cannot see written underneath it.](img/sdlc-gates.svg)

## Part 3 — Hands-on Lab (180 min)
**Learning goals:** run a SAST tool and a secret scanner, triage findings by CWE/severity, and remediate real flaws.
**Prerequisites:** Docker installed; internet to pull the Semgrep/Gitleaks images.

**Environment setup**
```bash
cd labs/week02-sdlc-tooling
cat scan.sh                 # see exactly what it runs
bash scan.sh                # Semgrep (p/default + p/owasp-top-ten) then Gitleaks on ./vulnerable-repo
```
Target under scan: `vulnerable-repo/app.py` (plus `requirements.txt`). It contains five planted flaws.

**What to submit per task:** the command/payload run + a screenshot of the finding + a 2–3 sentence mitigation.

**Task 0 — Onboarding (5 min)** · *Goal:* confirm tooling. *Steps:* run `bash scan.sh`; confirm both Semgrep and Gitleaks sections produce output. *Deliverable:* screenshot showing both tools ran.

> Command run: `bash scan.sh` from `labs/week02-sdlc-tooling`. Output confirms both tools ran: Semgrep reported "Ran 322 rules on 2 files: 10 findings", then Gitleaks reported "leaks found: 2". Screenshot: `Screenshots/task0-scan-summary.png`.

**Task 1 — SAST sweep with Semgrep (25 min)** · *Goal:* find code flaws. *Steps:* read the Semgrep output; locate the SQL injection in `/user` (CWE-89, string-formatted query), the OS command injection in `/ping` (CWE-78, `shell=True`), the weak `md5` password hash (CWE-327), and `debug=True` (CWE-489). *Deliverable:* one screenshot per finding with the file:line.

> Semgrep flagged all four planted flaws in `vulnerable-repo/app.py`:
> - **CWE-89 SQL injection**, `/user`, lines 19-20 — `q = "SELECT * FROM users WHERE name = '%s'" % name` then `con.execute(q)`. User input from `request.args.get("name")` is string-formatted straight into the query. *Mitigation:* use a parameterized query, e.g. `con.execute("SELECT * FROM users WHERE name = ?", (name,))`.
> - **CWE-78 OS command injection**, `/ping`, line 26 — `subprocess.check_output("ping -c 1 " + host, shell=True)`. User-controlled `host` is concatenated into a shell string with `shell=True`. *Mitigation:* drop `shell=True` and pass an argument list, e.g. `subprocess.check_output(["ping", "-c", "1", host])`.
> - **CWE-327 weak hash**, `store_password`, line 30 — `hashlib.md5(pw.encode()).hexdigest()`. MD5 is fast and not collision-resistant, so it's unsuitable for password storage. *Mitigation:* use a slow, salted password hash like bcrypt or argon2, not a general-purpose hash.
> - **CWE-489 debug mode in production**, line 33 — `app.run(debug=True)`. Flask's debugger, if reachable, allows remote code execution via its interactive console. *Mitigation:* set `debug=False` and read debug mode from an environment variable that's off by default.
>
> Screenshots: `Screenshots/task1-code-finding-19,20.png` (SQL injection), `Screenshots/task1-code-finding-26,30,33.png` (command injection, weak hash, debug mode).

**Task 2 — Secret scan with Gitleaks (15 min)** · *Goal:* find leaked credentials. *Steps:* read the Gitleaks output; identify `AWS_SECRET_ACCESS_KEY` and `DB_PASSWORD` (CWE-798). *Deliverable:* screenshot + the rule that fired for each.

> Gitleaks found both planted secrets in `app.py`, both under rule **`generic-api-key`**:
> - `AWS_SECRET_ACCESS_KEY = "hK8pQ2mN5vX9wZ3rT6yU1sA4bC7dE0fG2hJ5kL8"` — line 11, entropy 5.08.
> - `DB_PASSWORD = "xQ7mK2pL9wR4tY6u"` — line 12, entropy 4.00.
>
> *Mitigation:* move both values out of source code into environment variables (or a secrets manager) loaded at runtime, then rotate both keys since they're already exposed in git history. Screenshot: `Screenshots/task0-scan-summary.png` (Gitleaks section).

**Task 3 — Bug Triage Race (30 min)** · *Goal:* triage accurately. *Steps:* build a table with columns *Tool | File:Line | CWE | Severity | TP/FP | Fix idea*; mark at least 3 true positives and 1 likely false positive and justify each. (Score = TP − misclassified.) *Deliverable:* the completed triage table.

| Tool | File:Line | CWE | Severity | TP/FP | Fix idea |
|---|---|---|---|---|---|
| Semgrep `sql-injection-using-db-cursor-execute` | app.py:19-20 | CWE-89 | High | **TP** | Parameterize the query: `con.execute("SELECT * FROM users WHERE name = ?", (name,))` |
| Semgrep `sqlalchemy-execute-raw-query` | app.py:20 | CWE-89 | High | **FP** — justification: this rule's fix advice is "use SQLAlchemy ORM," but `app.py` doesn't import or use SQLAlchemy at all (it uses plain `sqlite3`). The rule fired purely on the string-formatting pattern, not on actual SQLAlchemy usage. The real SQLi bug at this same line is already correctly caught by the `sql-injection-using-db-cursor-execute` rule above — this is a duplicate/wrong-framework match on top of a true finding, not a distinct real issue. | N/A — no action beyond the fix already applied for the row above |
| Semgrep `dangerous-subprocess-use` / `subprocess-shell-true` | app.py:26 | CWE-78 | High | **TP** | Drop `shell=True`, pass an argument list: `subprocess.check_output(["ping", "-c", "1", host])` |
| Semgrep `insecure-hash-algorithm-md5` | app.py:30 | CWE-327 | Medium | **TP** | Replace `hashlib.md5` with a slow, salted hash: `bcrypt` or `argon2` |
| Semgrep `debug-enabled` | app.py:33 | CWE-489 | Medium | **TP** | `app.run(debug=False)`, control via an environment variable that defaults to off |
| Gitleaks `generic-api-key` | app.py:11 | CWE-798 | High | **TP** | Move `AWS_SECRET_ACCESS_KEY` to an environment variable / secrets manager, then rotate the key (it's already exposed in git history) |
| Gitleaks `generic-api-key` | app.py:12 | CWE-798 | High | **TP** | Move `DB_PASSWORD` to an environment variable / secrets manager, then rotate it |

*Note: the two Django-specific `tainted-sql-string` rule hits (also on lines 16-20) are the same duplicate-framework-match issue as the SQLAlchemy row above and are omitted from the table for that reason — they'd be marked FP with identical justification if listed individually.*

**Task 4 — Fuzzing intro (10 min)** · *Goal:* see coverage-guided fuzzing find a bug SAST won't. *Steps:* in the `labs/toolbox` container (Apple clang has no libFuzzer runtime), build `clang -g -fsanitize=address,fuzzer harness.c -o fuzz`, then **seed the corpus** and run it:
`mkdir -p corpus && printf 'FUZ' > corpus/seed && ./fuzz corpus`. It crashes almost immediately with an AddressSanitizer heap-buffer-overflow at `harness.c:23` (the `data[3]` read with no `size > 3` check). Seeding matters: an unseeded `./fuzz` has to rediscover the magic bytes by chance and often finds nothing for minutes — that unpredictability is itself worth a sentence in your write-up. (The deep fuzzing+exploit lab is Week 11.) *Deliverable:* the ASan crash output (or a screenshot) + a 2-sentence note on why fuzzing finds this bug when a linter/SAST pass over the same 4-line check would not.

> Built and ran in the `labs/toolbox` container: `clang -g -fsanitize=address,fuzzer harness.c -o fuzz`, seeded the corpus with `FUZ`, then `./fuzz corpus`. It crashed on the very first input (the seed itself) with `AddressSanitizer: heap-buffer-overflow ... harness.c:23:21`, and wrote a reproducer file `crash-0eb8e4ed029b774d80f2b66408203801cb982a60`. Screenshot: `Screenshots/task4-fuzz-crash.png`.
>
> **Why fuzzing found it and SAST didn't:** SAST works by matching code text against known dangerous patterns without ever executing the program — and the missing `size > 3` check on line 23 of harness.c looks like completely ordinary code, so there's no recognizable "dangerous pattern" for a rule to match against. Fuzzing actually runs the program with crafted input, so it caught the out-of-bounds read the moment real execution tried to read `data[3]` from a 3-byte buffer — a bug that only reveals itself when the code actually runs, not by reading the source.

**Task 5 — Scan the project target (40 min)** · *Goal:* apply the tools to your term project. *Steps:* run Semgrep + Gitleaks against **NoteVault** (`../../project/starter-app`); also run an SCA scan: `docker run --rm -v "$PWD/../../project/starter-app:/src" aquasec/trivy fs /src`. *Deliverable:* a findings list (tool, file:line/CVE, CWE) — reuse it in your project vuln report.

> Ran Semgrep (27 raw findings, several are duplicate rule-hits on the same bug from different framework-specific rulesets, the same false-positive-by-wrong-framework pattern as Task 3), Gitleaks (no leaks found), and Trivy SCA (32 dependency vulnerabilities) against `project/starter-app`:
>
> | Tool | File:Line / Library | CWE / CVE | Severity |
> |---|---|---|---|
> | Semgrep | Dockerfile:12 | CWE-269 | Medium — container runs as root (no `USER` set) |
> | Semgrep | app.py:83 | CWE-347 | High — JWT decode accepts the `none` algorithm (unsigned, forgeable tokens) |
> | Semgrep | app.py:106-107, 181-182, 204 | CWE-79 / CWE-1336 | High — reflected XSS/SSTI via string-built HTML instead of a template |
> | Semgrep | app.py:117 | CWE-327 | Medium — md5 used as password hash |
> | Semgrep | app.py:128-130 | CWE-89 | High — SQL injection in the login query |
> | Semgrep | app.py:134 | CWE-798 | High — hardcoded JWT signing secret |
> | Semgrep | app.py:136 | CWE-614 | Medium — session cookie missing `secure`/`httponly`/`samesite` |
> | Semgrep | app.py:176-179 | CWE-89 | High — SQL injection in the notes search |
> | Semgrep | app.py:202-204 | CWE-78 | High — OS command injection in the export feature (`shell=True` with user input) |
> | Semgrep | app.py:209 | CWE-489 | Medium — `debug=True` bound to `host="0.0.0.0"` (exposed publicly) |
> | Gitleaks | requirements.txt + app.py | — | "no leaks found" — missed the hardcoded JWT secret at app.py:23 because `SECRET = "notevault-dev-secret"` is a low-entropy, dictionary-like phrase, not a random-looking string Gitleaks' rules match on |
> | Trivy (SCA) | Flask 2.0.1 | CVE-2023-30861 | High — session cookie disclosure |
> | Trivy (SCA) | PyJWT 1.7.1 | CVE-2022-29217 | High — JWT key-confusion |
> | Trivy (SCA) | urllib3 1.26.4 | CVE-2021-33503 | High — ReDoS |
> | Trivy (SCA) | Werkzeug 2.0.1 | CVE-2024-34069 | High — code execution on a developer's machine |
> | Trivy (SCA) | requests 2.25.1 | CVE-2023-32681 | Medium — Proxy-Authorization header leak |
> | Trivy (SCA) | Jinja2 3.0.1 | CVE-2024-22195 | Medium — HTML attribute injection |
>
> *Trivy found 32 vulnerabilities total across these 6 libraries (12 High, 18 Medium, 2 Low) — the table lists the highest-severity CVE per library as representative; full output available in scan logs.*

**Task 6 — Build a security CI gate (25 min)** · *Goal:* automate the scan (previews Week 15). *Steps:* adapt `../week15-devsecops-pipeline/security-ci.yml` into a workflow that runs Semgrep + Trivy + Gitleaks and **fails on HIGH/CRITICAL**; run it locally (`act`) or commit to your fork and read the Actions log. *Deliverable:* the workflow file + a screenshot of a failing run.

> Adapted `week15-devsecops-pipeline/security-ci.yml` into a new workflow at `.github/workflows/week02-security-gate.yml`, scoped to this week's `vulnerable-repo` target — deliberately a **separate file** from the repo's real `.github/workflows/security-ci.yml`, which intentionally does not gate `labs/week*/` (that repo-wide `.semgrepignore` exclusion exists on purpose so the real course CI doesn't stay red forever on teaching material). Committed to `wk02` and pushed; GitHub Actions ran it automatically on push.
>
> **Debugging note (part of the learning, not just the deliverable):** the first run showed SAST (Semgrep) passing despite known bugs — the job log showed `Scanning 0 files ... Files matching .semgrepignore patterns: 2`, because that same repo-wide `.semgrepignore` silently excluded `labs/week*/` from *any* Semgrep run, not just the production workflow. Fixed by copying the scan target to `/tmp/scan-target` before scanning, outside the checked-out repo tree, so the ignore rule no longer applied (the same reason `scan.sh` works locally — it mounts only the `vulnerable-repo/` subfolder into a fresh container, with no `.semgrepignore` present).
>
> Final run: **SAST (Semgrep) ❌ fail**, **Gitleaks ❌ fail**, **SCA (Trivy) ✅ pass** — overall run status: **failure**, as required. The Trivy pass is legitimate, not a bug: `vulnerable-repo/requirements.txt` specifies `flask>=3.1.3` (an unpinned range), and Trivy needs an exact installed version to check against the CVE database, so it correctly found nothing to flag here — unlike `project/starter-app` in Task 5, whose `requirements.txt` pins exact vulnerable versions and produced 32 real findings.
>
> Screenshot: `Screenshots/task6-ci-gate-failing.png`.

**Task 7 — SAST blind spots (20 min)** · *Goal:* see what scanners miss. *Steps:* find one real bug in `vulnerable-repo/app.py` (or NoteVault) that Semgrep did **not** flag, and explain why a pattern-based tool missed it. *Deliverable:* the bug + a 2-sentence explanation.

> **The bug:** the `/user` route (lines 14-20) has no authentication or authorization check at all — anyone who knows the URL (`/user?name=admin`) can read every matching row straight from the database with no login required. This is a Broken Access Control / Missing Authorization flaw (CWE-862), and Semgrep never flagged it.
>
> **Why a pattern-based tool missed it:** Semgrep works by matching code text against known dangerous *syntax patterns* — it has no concept of which routes are supposed to require login, because that's business intent that lives outside the code's syntax entirely. There is no "missing `if not logged_in: return 403`" pattern to match against, since the absence of a check looks identical to any other route that legitimately doesn't need one — spotting it requires a human who understands what the app *should* do, not just what the code *says*.

**Task 8 — Defend / fix it (10 min)** · *Goal:* remediate the planted flaws in `vulnerable-repo/app.py`. *Steps:* rewrite `/user` to use a parameterized query (`?` placeholder); remove `shell=True` and pass an argument list in `/ping`; move both secrets to environment variables; replace `md5` with bcrypt/argon2; set `debug=False`. *Deliverable:* a before/after diff for each fix mapped to its CWE.

> All five planted flaws fixed in `vulnerable-repo/app.py`:
>
> | CWE | Before | After |
> |---|---|---|
> | CWE-798 (hardcoded secrets) | `AWS_SECRET_ACCESS_KEY = "hK8pQ2..."` / `DB_PASSWORD = "xQ7mK2..."` | `AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]` / `DB_PASSWORD = os.environ["DB_PASSWORD"]` |
> | CWE-89 (SQL injection) | `q = "SELECT * FROM users WHERE name = '%s'" % name` then `con.execute(q)` | `q = "SELECT * FROM users WHERE name = ?"` then `con.execute(q, (name,))` — parameterized, `name` is never interpreted as SQL |
> | CWE-78 (OS command injection) | `subprocess.check_output("ping -c 1 " + host, shell=True)` | `subprocess.check_output(["ping", "-c", "1", host])` — no shell, argument list |
> | CWE-327 (weak hash) | `hashlib.md5(pw.encode()).hexdigest()` | `hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)` with a random per-password salt (`os.urandom(16)`), stored alongside the hash |
> | CWE-489 (debug in production) | `app.run(debug=True)` | `app.run(debug=False)` |
>
> **Verified by re-running the scanners** (not just by reading the diff): `bash scan.sh` against the fixed `vulnerable-repo/` now reports **Semgrep: 0 findings** (down from 10) and **Gitleaks: no leaks found** (down from 2) — confirms all five flaws are actually resolved, not just visually changed.

## Part 4 — Reflection
1. Map two of your findings to their CWE and to the matching OWASP 2025 category.

   The SQL injection at `app.py:19-20` (Task 1) is **CWE-89**, mapping to **OWASP 2025 A05 Injection**. The hardcoded `AWS_SECRET_ACCESS_KEY` at `app.py:11` (Task 2) is **CWE-798**, mapping to **OWASP 2025 A02 Security Misconfiguration**.

2. Name a real-world breach caused by a hardcoded/leaked secret or an injection flaw, and what control would have caught it pre-release.

   The **2016 Uber data breach**: attackers found AWS credentials hardcoded in a private GitHub repository used by Uber engineers, then used those credentials to access an AWS S3 bucket containing the personal data of 57 million users and drivers — the same class of mistake as the `AWS_SECRET_ACCESS_KEY` planted in this week's `app.py`. Secret scanning (like Gitleaks) wired into CI would have flagged the credential the moment it was committed, long before it could be exploited.

3. Which single tool (SAST vs. secret scanning) gave the highest-value findings on this repo, and why?

   It depends on what "highest-value" means. By **count**, SAST (Semgrep) won clearly — 10 findings vs. Gitleaks' 2. But by **severity-per-finding**, secret scanning arguably wins: a single leaked AWS key is an immediate, complete compromise of whatever that key can access (as the Uber example above shows), while most individual SAST findings need a specific attacker action against a specific endpoint to matter. In practice neither replaces the other — they catch different failure modes, which is why the pipeline runs both.

## Grading rubric (100)
| Criterion | Points |
|---|---|
| Lecture questions (Part 2) | 20 |
| Exploitation + evidence (scan output + triage table + screenshots) | 40 |
| Defense (remediated `app.py` with before/after diffs) | 25 |
| Reflection (CWE/OWASP mapping + breach + tool value) | 15 |

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/diagram must show a terminal running `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'` **in the
  same image as the evidence**. When the evidence is a browser page, a DevTools panel or a
  rendered response, put that terminal **beside the browser and capture the whole screen** — a
  cropped window carries nothing that identifies you, and the lab's own output is
  byte-identical for the whole cohort *by design*, so the stamp is the only thing that makes
  the shot yours. Generic or borrowed evidence is not accepted.
- **Personalized flag (if this lab issues one):** N/A — this lab does not issue a `ctf.zcr.ai` flag.
  *Flags are unique per student — submitting another student's flag is a violation. How to submit: **learn.zcr.ai/submit** (full guide: `SUBMISSION.md` in the repo root).*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the vulnerability work**?

     The `/user` endpoint built its SQL query by directly formatting user input into the query string (`"...WHERE name = '%s'" % name`). Because the database receives the whole thing as one string with no distinction between "original command" and "user-supplied data," an attacker could submit input like `x' OR '1'='1` to turn the query into `WHERE name = 'x' OR '1'='1'` — a condition that's always true — and dump every row in the table instead of just one user's data.

  2. **Why does your fix actually stop it** — and what could still break it?

     The parameterized query (`WHERE name = ?` with `name` passed separately) sends the query structure and the user's value to the database through two separate channels. The database compiles the structure first, so whatever value lands in the `?` slot is always treated as a single literal string to compare against — never as SQL syntax — no matter what characters it contains. This fix only protects this one query, though: any other place in the codebase that still concatenates strings into SQL remains vulnerable, and nothing stops a future edit from reintroducing string formatting by mistake — which is exactly why an automated gate (Task 6) matters more than a one-time manual fix.

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

1. Ask an AI assistant to exploit **or** fix this week's vulnerability. Paste its full answer.
2. **Find what's wrong or risky** in it — insecure code, a subtly incomplete fix, a hallucinated API/function/CVE, a missed edge case, or wrong reasoning. Quote the exact line(s).
3. Produce the **correct, verified** version yourself and explain in 2–3 sentences why the AI's output was insufficient.

> **1. AI's answer** (asked to fix the SQL injection at `/user`):
> ```python
> @app.route("/user")
> def user():
>     name = request.args.get("name", "")
>     safe_name = sqlite3.escape_string(name)   # "escape it before using it"
>     con = sqlite3.connect("app.db")
>     q = "SELECT * FROM users WHERE name = '%s'" % safe_name
>     return str(con.execute(q).fetchall())
> ```
>
> **2. What's wrong:**
> - **Hallucinated API:** `sqlite3.escape_string(...)` — Python's built-in `sqlite3` module has **no such function** (verified: `hasattr(sqlite3, 'escape_string')` returns `False`). That name belongs to a different library (MySQL's client), not `sqlite3`. This code crashes with `AttributeError` on the very first request, before security even enters the picture.
> - **Wrong approach even if the function existed:** "escape the input, then still string-format it into the query" still concatenates user input into the SQL command string — it only shrinks the attack surface, it doesn't eliminate it, because it depends on the escaping logic covering every dangerous character correctly in every context. That's fragile; parameterization removes the need to get escaping right at all.
>
> **3. Correct, verified version:** the actual fix applied in Task 8 — `q = "SELECT * FROM users WHERE name = ?"` then `con.execute(q, (name,))`. Verified by re-running `bash scan.sh`: Semgrep findings dropped from 10 to 0. The AI's answer was insufficient because it invented a function that doesn't exist in the library actually being used, and even its underlying strategy (escape-then-concatenate) is a weaker defense than parameterized queries.

> Disclose your AI use in the Part 1 table. This task counts toward your **Defense + Reflection** score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** In 2–3 sentences, in your own words, describe what this week's vulnerable code/endpoint actually *does* and *why it is exploitable* — explain the mechanism, don't dump jargon.

> The `/user` endpoint takes a `name` value straight from the URL and pastes it directly into a SQL query as text, without separating "the command" from "the data." Because the database can't tell the difference between the original query and text an attacker controls, typing something like `x' OR '1'='1` turns the query into one that's always true, dumping every row in the table instead of just one match.

**B. Prompt Problem.** Write a **single prompt** that makes an AI produce a *correct, secure* fix for one finding. Run it: does the exploit now fail? If not, refine the prompt and try again. Submit the **final prompt + the verified result**.
*Graded on the prompt's precision and your verification — this trains problem decomposition and AI literacy (Denny et al. 2024).*

> **Final prompt:** "Fix the SQL injection in this Flask + Python `sqlite3` endpoint. Requirements: (1) use only functions that actually exist in Python's built-in `sqlite3` module — do not invent any function names, (2) rewrite the query to use a `?` parameterized placeholder instead of string formatting, and pass the user input as a separate tuple argument to `.execute()`, (3) show only the corrected function." (followed by the vulnerable `/user` function). The requirements were written specifically to rule out the failure mode found in "Audit the AI" above (a hallucinated `sqlite3.escape_string` and an escape-based non-fix).
>
> **Verified result:**
> ```python
> @app.route("/user")
> def user():
>     name = request.args.get("name", "")
>     con = sqlite3.connect("app.db")
>     q = "SELECT * FROM users WHERE name = ?"
>     return str(con.execute(q, (name,)).fetchall())
> ```
> This is the actual fix applied in Task 8. Verified by re-running `bash scan.sh`: Semgrep findings dropped from 10 to 0, and the original exploit payload `x' OR '1'='1` no longer alters the query — it's now treated as a single literal string to compare against, not SQL syntax.
