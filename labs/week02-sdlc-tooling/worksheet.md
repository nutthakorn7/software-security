# Worksheet 2 — Secure SDLC & Tooling (3 hrs)

> **Course:** Software Security (KOSEN69) · **Week 2**
> **Aligned to:** OWASP 2025 (A05 Injection [CWE-89, CWE-78], A04 Cryptographic Failures [CWE-327], A02 Security Misconfiguration [CWE-798, CWE-489]) · CWE-798, CWE-89, CWE-78, CWE-327, CWE-489
> **Signature game:** "Bug Triage Race" (scan → triage; score = true positives − misclassified)

> **Ethics note:** The scanners run only against the provided `vulnerable-repo/` on your own machine. Do not point SAST/secret scanners at third-party repos or production systems without authorization. Treat any secret you find here as fake lab data.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|Hathaichanok Yimjan|6631503045|16/8/2569|---|

## Part 2 — Lecture Questions
Answer in your own words (2–4 sentences each).
1. Distinguish SAST, DAST, and SCA — what does each see, and when in the SDLC does each run?
Answer = SAST checks source code for security problems without running the application, while DAST tests a running application from the outside. SCA checks third-party libraries and dependencies for known vulnerabilities, with SAST and SCA commonly used earlier in development and DAST used when a runnable application is available.
2. What is secret scanning, and why do hardcoded secrets keep ending up in repos?
Answer = Secret scanning searches code and repositories for sensitive information such as API keys, passwords, and tokens. Hardcoded secrets often appear because developers put credentials directly in code for convenience, forget to remove test secrets, or accidentally commit configuration files.
3. What does "shift-left / DevSecOps" mean in practice for a CI pipeline?
Answer = Shift-left means moving security checks earlier in the software development process instead of waiting until release. In a CI pipeline, tools such as SAST, SCA, and secret scanning can automatically check code when developers commit changes or create pull requests.
4. Why is coverage-guided fuzzing considered the dominant modern bug-finding technique?
Answer = Coverage-guided fuzzing generates many inputs and uses code-coverage feedback to find inputs that reach new parts of the program. This makes it effective for discovering crashes and unexpected behavior that normal testing may miss.
5. Define true positive vs. false positive in scanner triage, and why misclassifying both directions is costly.
Answer = A true positive is a scanner finding that represents a real security problem, while a false positive is a finding that is not actually a vulnerability. Missing a true positive can leave a real vulnerability unfixed, while treating too many false positives as real problems wastes time and causes alert fatigue.

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

![Task 0 Verification](img/wk02-task%200.png)

**Task 1 — SAST sweep with Semgrep (25 min)** · *Goal:* find code flaws. *Steps:* read the Semgrep output; locate the SQL injection in `/user` (CWE-89, string-formatted query), the OS command injection in `/ping` (CWE-78, `shell=True`), the weak `md5` password hash (CWE-327), and `debug=True` (CWE-489). *Deliverable:* one screenshot per finding with the file:line.

![Task 1 Semgrep Findings](img/wk02-task%201.png)

**Task 2 — Secret scan with Gitleaks (15 min)** · *Goal:* find leaked credentials. *Steps:* read the Gitleaks output; identify `AWS_SECRET_ACCESS_KEY` and `DB_PASSWORD` (CWE-798). *Deliverable:* screenshot + the rule that fired for each.
Ans = ### Finding 1 — AWS_SECRET_ACCESS_KEY
| Field | Value |
|---|---|
| File:Line | `app.py:11` |
| Rule ที่ทำงาน (RuleID) | `generic-api-key` |
| Entropy | 5.080274 |
| CWE | CWE-798 (Use of Hard-coded Credentials) |

### Finding 2 — DB_PASSWORD
| Field | Value |
|---|---|
| File:Line | `app.py:12` |
| Rule ที่ทำงาน (RuleID) | `generic-api-key` |
| Entropy | 4.000000 |
| CWE | CWE-798 (Use of Hard-coded Credentials) |

**Task 3 — Bug Triage Race (30 min)** · *Goal:* triage accurately. *Steps:* build a table with columns *Tool | File:Line | CWE | Severity | TP/FP | Fix idea*; mark at least 3 true positives and 1 likely false positive and justify each. (Score = TP − misclassified.) *Deliverable:* the completed triage table.
Ans = ## Task 3 — Bug Triage Race

| Tool | File:Line | CWE | Severity | TP/FP | Fix idea |
|---|---|---|---|---|---|
| Semgrep | app.py:19 | CWE-89 (SQL Injection) | High | **TP** | Use a parameterized query instead of string formatting: `con.execute("SELECT * FROM users WHERE name = ?", (name,))` |
| Semgrep | app.py:26 | CWE-78 (OS Command Injection) | Critical | **TP** | Remove `shell=True` and pass arguments as a list instead: `subprocess.check_output(["ping", "-c", "1", host])`, plus validate/allowlist the `host` value |
| Semgrep | app.py:30 | CWE-327 (Weak Hash — MD5) | Medium | **TP** | Replace md5 with bcrypt or argon2, which are purpose-built for password hashing (include salting + a work factor) |
| Semgrep | app.py:33 | CWE-489 (Active Debug Code) | Low–Medium | **TP** | Set `debug=False` before deploying, or pull the value from an environment variable so debug mode is never accidentally left on in production |
| Gitleaks | app.py:11 | CWE-798 (Hard-coded Credentials) | Critical | **TP** | Move `AWS_SECRET_ACCESS_KEY` into an environment variable or a secrets manager, and rotate the leaked key immediately |
| Gitleaks | app.py:12 | CWE-798 (Hard-coded Credentials) | Critical | **TP** | Move `DB_PASSWORD` into an environment variable or a secrets manager, and change the leaked database password |

**Note on False Positives:**
No false positive appeared in this scan of `vulnerable-repo/app.py`, since this is a controlled lab where the planted vulnerabilities align exactly with each tool's detection signatures. In real-world use, though, a common source of false positives is generic secret detection flagging high-entropy strings that aren't actually secrets (e.g. test fixtures, UUIDs, or hashes unrelated to credentials) — these require checking the surrounding context rather than trusting the regex/entropy score alone.

**Triage Race score:** TP = 6, misclassified = 0 → Score = 6 − 0 = **6**

![Task 3 Bug Triage Result](img/wk02-task%203.png)

**Task 4 — Fuzzing intro (10 min)** · *Goal:* see coverage-guided fuzzing find a bug SAST won't. *Steps:* in the `labs/toolbox` container (Apple clang has no libFuzzer runtime), build `clang -g -fsanitize=address,fuzzer harness.c -o fuzz`, then **seed the corpus** and run it:
`mkdir -p corpus && printf 'FUZ' > corpus/seed && ./fuzz corpus`. It crashes almost immediately with an AddressSanitizer heap-buffer-overflow at `harness.c:23` (the `data[3]` read with no `size > 3` check). Seeding matters: an unseeded `./fuzz` has to rediscover the magic bytes by chance and often finds nothing for minutes — that unpredictability is itself worth a sentence in your write-up. (The deep fuzzing+exploit lab is Week 11.) *Deliverable:* the ASan crash output (or a screenshot) + a 2-sentence note on why fuzzing finds this bug when a linter/SAST pass over the same 4-line check would not.
Ans = ### Task 4 — Fuzzing intro

**ASan Crash Output:**
```text
=================================================================
==18420==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6020000000b3 at pc 0x0000004c21a1 bp 0x7ffd5e2a39b0 sp 0x7ffd5e2a39a8
READ of size 1 at 0x6020000000b3 thread T0
    #0 0x4c21a0 in LLVMFuzzerTestOneInput /labs/week02-sdlc-tooling/harness.c:23
    #1 0x4311b9 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long)
    #2 0x41b873 in fuzzer::RunOneTest(fuzzer::Fuzzer*, char const*, unsigned long)

0x6020000000b3 is located 0 bytes to the right of 3-byte region [0x6020000000b0,0x6020000000b3)
allocated by thread T0 here:
    #0 0x4972fd in malloc
    #1 0x431120 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long)

SUMMARY: AddressSanitizer: heap-buffer-overflow harness.c:23 in LLVMFuzzerTestOneInput
=================================================================
(SAST vs. Fuzzing):
Static analysis tools (SAST) rely on pattern matching and code structure without executing the binary, making them blind to dynamic memory states and implicit array boundary assumptions. Coverage-guided fuzzing actually executes the code with mutating inputs, leveraging runtime feedback to trigger the out-of-bounds read at line 23 when size <= 3.

Note on Seeding: Providing a initial corpus seed (FUZ) gives the fuzzer the required magic bytes upfront, allowing it to instantly breach the conditional check rather than wasting minutes randomly guessing byte combinations.
```
**Task 5 — Scan the project target (40 min)** · *Goal:* apply the tools to your term project. *Steps:* run Semgrep + Gitleaks against **NoteVault** (`../../project/starter-app`); also run an SCA scan: `docker run --rm -v "$PWD/../../project/starter-app:/src" aquasec/trivy fs /src`. *Deliverable:* a findings list (tool, file:line/CVE, CWE) — reuse it in your project vuln report.

![Task 5.1 Semgrep Scan](img/wk02-task%205.1.png)
![Task 5.2 Gitleaks Scan](img/wk02-task%205.2.png)
![Task 5.3 Trivy SCA Scan](img/wk02-task%205.3.png)

**Task 6 — Build a security CI gate (25 min)** · *Goal:* automate the scan (previews Week 15). *Steps:* adapt `../week15-devsecops-pipeline/security-ci.yml` into a workflow that runs Semgrep + Trivy + Gitleaks and **fails on HIGH/CRITICAL**; run it locally (`act`) or commit to your fork and read the Actions log. *Deliverable:* the workflow file + a screenshot of a failing run.

![Task 6 CI Pipeline Failure](img/wk02-task%206.png)

**Task 7 — SAST blind spots (20 min)** · *Goal:* see what scanners miss. *Steps:* find one real bug in `vulnerable-repo/app.py` (or NoteVault) that Semgrep did **not** flag, and explain why a pattern-based tool missed it. *Deliverable:* the bug + a 2-sentence explanation.
Ans = Vulnerability: Broken Access Control / Insecure Direct Object Reference (IDOR — $CWE-284$) in vulnerable-repo/app.py at the /user endpoint.Explanation:The /user endpoint fetches and returns profile data for any requested name without enforcing authentication or access control checks.Pattern-based SAST tools like Semgrep analyze syntactic patterns and taint sinks, making them incapable of understanding business logic intent or detecting when security authorization guards are entirely absent.



**Task 8 — Defend / fix it (10 min)** · *Goal:* remediate the planted flaws in `vulnerable-repo/app.py`. *Steps:* rewrite `/user` to use a parameterized query (`?` placeholder); remove `shell=True` and pass an argument list in `/ping`; move both secrets to environment variables; replace `md5` with bcrypt/argon2; set `debug=False`. *Deliverable:* a before/after diff for each fix mapped to its CWE.

![Task 8 Clean Scan Verification](img/wk02-task%208.png)

## Part 4 — Reflection
1. Map two of your findings to their CWE and to the matching OWASP 2025 category.
2. Name a real-world breach caused by a hardcoded/leaked secret or an injection flaw, and what control would have caught it pre-release.
3. Which single tool (SAST vs. secret scanning) gave the highest-value findings on this repo, and why?

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
- **Personalized flag (if this lab issues one):** ____________________
  *Flags are unique per student — submitting another student's flag is a violation. How to submit: **learn.zcr.ai/submit** (full guide: `SUBMISSION.md` in the repo root).*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the vulnerability work**?
  2. **Why does your fix actually stop it** — and what could still break it?

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

1. Ask an AI assistant to exploit **or** fix this week's vulnerability. Paste its full answer.
2. **Find what's wrong or risky** in it — insecure code, a subtly incomplete fix, a hallucinated API/function/CVE, a missed edge case, or wrong reasoning. Quote the exact line(s).
3. Produce the **correct, verified** version yourself and explain in 2–3 sentences why the AI's output was insufficient.

> Disclose your AI use in the Part 1 table. This task counts toward your **Defense + Reflection** score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** In 2–3 sentences, in your own words, describe what this week's vulnerable code/endpoint actually *does* and *why it is exploitable* — explain the mechanism, don't dump jargon.

**B. Prompt Problem.** Write a **single prompt** that makes an AI produce a *correct, secure* fix for one finding. Run it: does the exploit now fail? If not, refine the prompt and try again. Submit the **final prompt + the verified result**.
*Graded on the prompt's precision and your verification — this trains problem decomposition and AI literacy (Denny et al. 2024).*
