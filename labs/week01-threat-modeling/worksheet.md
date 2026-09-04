# Worksheet 1 — Security Mindset & Threat Modeling (3 hrs)

> **Course:** Software Security (KOSEN69) · **Week 1**
> **Aligned to:** OWASP 2025 A06 Insecure Design · CWE-501 (Trust Boundary Violation)
> **Signature game:** "Elevation of Privilege" (Microsoft STRIDE card deck)

> **Ethics note:** This week is *modeling only* — you analyze design, you do **not** attack the app. Run the sample app only on your own VM/localhost. Never apply these techniques to systems you do not own or lack written permission to test.

## Part 1 — Student Information
| Name | Student ID | Date | Group |
|---|---|---|---|
| SORRAWIT THANAKHWANG | 6531503080 | 2026-09-04 | NONE |

AI disclosure: used Claude (Anthropic) as a drafting/critique assistant for Part 2/4, the Evidence & Integrity write-up, and the Audit the AI section below; all DFDs, STRIDE analysis, EoP scoring, and the Task 8 code fix were done by the student and then reviewed with AI help. See the "Audit the AI" section for the specific critique performed.

## Part 2 — Lecture Questions
Answer in your own words (2–4 sentences each).
1. Define the CIA triad and give one concrete failure example for each of the three properties.

   The CIA triad is Confidentiality (only authorized people can read data), Integrity (data can't be changed without authorization or detection), and Availability (authorized people can access the system/data when they need it). Failure examples: **Confidentiality** — `GET /notes` in this week's sample-app returns every user's notes to anyone, no auth check, so a stranger reads private data. **Integrity** — `/upload` lets a filename like `../notes.db` overwrite the real database, so data changes with no authorization and no detection. **Availability** — `/upload` has no size or rate limit, so repeated large uploads can fill the disk and crash the app for everyone.

2. What is a *trust boundary*, and why does data crossing one deserve extra scrutiny?

   A trust boundary is a line where data moves from one zone of trust to another — e.g. from an anonymous internet client into the server process, or from the server into a database. Anything past the boundary controls what it sends but not what happens to it, so the receiving side must not assume the data is safe; that's exactly the gap `/upload` fails to check (the client fully controls `filename`, and the server trusts it enough to build a file path from it).

3. Explain "attack surface." Name two things that increase it in a web app.

   The attack surface is every point where an outside input can reach the application — every endpoint, parameter, file upload, header, or dependency an attacker could touch. In this app it grows with: (1) every unauthenticated endpoint (`/notes`, `/upload`, `/files/<name>` all accept requests from anyone), and (2) every place client-supplied data is used to build something on the server side without validation, like a filename becoming a file path.

4. What does each STRIDE letter map to, and which security property does each threat violate?

   Spoofing (pretending to be someone else) violates **Authentication**; Tampering (changing data/code without permission) violates **Integrity**; Repudiation (denying you did an action, with no way to prove otherwise) violates **Non-repudiation**; Information disclosure (exposing data to those not authorized to see it) violates **Confidentiality**; Denial of Service (making the system unavailable) violates **Availability**; Elevation of Privilege (gaining more access than granted) violates **Authorization**.

5. What does "Secure by Design" (CISA) mean, and how does it differ from bolting security on after release?

   Secure by Design means security decisions (input validation, least privilege, safe defaults) are built into the architecture from the start, so insecure states are structurally hard to reach — like Task 8's fix, which removes the user-controlled string from the path entirely rather than trying to filter bad input after the fact. Bolting security on after release means shipping first and patching specific exploits as they're found (e.g. blacklisting `../` in a filename) — it only closes the instance that was discovered, not the whole class, so a new bypass technique can reopen the same hole.

## Part 3 — Hands-on Lab (180 min)
**Learning goals:** build a data-flow diagram (DFD), apply STRIDE to a real Flask app, rank risks, and propose mitigations.
**Prerequisites:** Docker + Docker Compose in your VM; a drawing tool (draw.io / paper + photo); the Elevation of Privilege deck (print or virtual) — free print-and-play PDF at [github.com/adamshostack/eop](https://github.com/adamshostack/eop).

**Environment setup**
```bash
cd labs/week01-threat-modeling
docker compose up --build           # starts sample-app on http://localhost:8080
curl -s -X POST localhost:8080/notes -H 'Content-Type: application/json' \
     -d '{"owner":"alice","body":"hello"}'   # observe behavior, do not attack
curl -s localhost:8080/notes

echo "demo file" > demo.txt
curl -s -X POST localhost:8080/upload -F "file=@demo.txt"   # observe behavior, do not attack
curl -s localhost:8080/files/demo.txt
```

Source to model lives in `sample-app/app.py`. Template to fill: `THREAT-MODEL-TEMPLATE.md` (copy it, do not edit the original).

**What to submit per task:** the threat/element identified + a screenshot (DFD, table, or running app) + a 2–3 sentence mitigation.

**Task 0 — Onboarding (5 min)** · *Goal:* prove the environment works. *Steps:* `docker compose up`, hit `/notes` and `/files/<name>`, read `sample-app/app.py`. *Deliverable:* screenshot of the running app + the JSON response.

**Task 1 — Draw the DFD (25 min)** · *Goal:* map the system. *Steps:* identify the external entity (web client), the process (Flask app), the data store (`notes.db` SQLite), the `uploads/` store, and the flows for `/notes`, `/upload`, `/files/<name>`; mark the Internet→app trust boundary with a dashed line. *Deliverable:* DFD image embedded in your copy of the template.

**Task 2 — STRIDE the elements (30 min)** · *Goal:* enumerate threats per element. *Steps:* for each element fill the S/T/R/I/D/E grid. Ground it in real code: `/notes` accepts a client-supplied `owner` with no auth (Spoofing); `/upload` saves raw `f.filename` — arbitrary-file-write (Tampering) — and echoes the resolved save path back in its response (Information disclosure); `/files/<name>` reads it back but is comparatively defended (see Task 5); no logging anywhere (Repudiation). *Deliverable:* completed STRIDE table.

**Task 3 — Elevation of Privilege game (20 min)** · *Goal:* find threats you missed. *Steps:* play the EoP deck against your DFD; each card you can tie to a real element/flow scores a point; record every valid threat. No printer or scissors? Draw from the digital deck below instead — same 78 cards, same rule. *Deliverable:* list of carded threats + score.

```sim
eop-deck
```

**Task 3b — Systems-level pass (25 min) 🔭** · *Goal:* find what the per-element grid cannot see. Tasks 2 and 3 enumerate threats **one element at a time**, and that is exactly where threat models are known to stop short — students taught STRIDE alone reliably identify component threats and *discount system-level ones* ([Joshi et al., ASEE 2024](https://arxiv.org/abs/2404.16632)). So do a second pass over the **whole** diagram:
![Three trust zones — public internet, application tier, data tier — with the two boundaries a request crosses between them](img/trust-boundaries.svg)

- **Trust boundaries end-to-end.** Follow one request from the client to `notes.db` and back. List every boundary it crosses. Which crossing has no check on it?
- **Assume one element is fully owned.** Pick the Flask process, then the `uploads/` store. For each: what does the attacker now *reach* — not what is it, but where does it get them?
- **Chain two "low" findings.** Find two threats you or the EoP deck rated minor that combine into something you would not accept. Write the chain as `A → B → consequence`.
- **One-line system claim.** Finish: "Even if every element-level mitigation in Task 8 is implemented, this system still fails if ___."

Use the simulation below before you start — toggle a component to attacker-controlled and watch what it reaches:

```sim
trust-boundary
```

*Deliverable:* the boundary list, two owned-element reachability notes, one written chain, and the system claim.

**Task 4 — Abuse cases & attacker personas (20 min)** · *Goal:* think like specific adversaries. *Steps:* define 2 personas (e.g. a curious logged-in user; an anonymous internet attacker) and write 2 abuse cases each against the sample app, tied to DFD elements. *Deliverable:* 4 abuse cases.

**Task 5 — Path-traversal deep-dive (25 min)** · *Goal:* analyze the riskiest flow. *Steps:* trace `/upload` → `/files/<name>`; explain how `../` in a filename escapes `uploads/`; sketch the secure design (`secure_filename`, store outside web root, allow-list extensions). *Deliverable:* the data flow + secure-design note.

**Task 6 — Threat-model the project target (30 min)** · *Goal:* kick off your term project. *Steps:* stop the sample-app first (`docker compose down` — both apps bind host port 8080), then run **NoteVault** (`cd ../../project/starter-app && docker compose up`), draw a quick DFD, and list the top 3 STRIDE threats you'd investigate. *Deliverable:* NoteVault DFD + top-3 threats (reuse these in your project report — `project/REPORT-TEMPLATE.md` in the repo root).

**Task 7 — Security requirements (15 min)** · *Goal:* turn threats into testable requirements. *Steps:* write 3 security requirements as acceptance criteria ("the system must … so that …"), each mapped to a threat from Task 2 or Task 6. *Deliverable:* 3 testable security requirements.

**Task 8 — Defend / fix it: rank & mitigate (25 min) 🛡️** · *Goal:* turn threats into action you can prove. *Steps:* rank the top 5 threats by likelihood × impact; propose one concrete mitigation each (e.g., auth on `/notes`, `secure_filename()` + allowlist for `/upload`, request logging for Repudiation, size/rate limits for DoS). Then **pick one and actually implement it** in your fork.

*Deliverable — the top-5 table, plus for the one you implemented:*
1. the **diff** (commit hash on your `wk01` branch),
2. **evidence it works**: the request that succeeded before your change and is refused after — both outputs,
3. **why it closes the class, not the instance** (2–3 sentences). `secure_filename()` on one endpoint is an instance fix; *"no user-supplied string ever becomes a path component"* is a class fix. Say which yours is, and if it's an instance fix, say what the class fix would be.

> **Why this is weighted.** Fewer than half of working developers can spot a security hole in code, and being shown vulnerabilities does not by itself teach you to find or close them. Exploiting is the half that feels like progress; defending is the half that transfers to your job.

## Part 4 — Reflection
1. Map your top finding to a CWE and to OWASP A06 (Insecure Design); explain the mapping in one sentence.

   My top finding — unauthenticated arbitrary file write via `/upload` accepting `../` in the client-supplied filename — maps to **CWE-22 (Path Traversal)** and to **OWASP A06:2025 Insecure Design**, because the vulnerability isn't a coding typo but a design choice (trusting a client-controlled string as a path component) that no amount of "adding a check later" fully fixes without redesigning where the filename comes from.

2. Name one real-world breach caused by a design flaw (not a missing patch) and what design control would have prevented it.

   The 2017 Equifax breach is usually remembered as "missed patch" (Apache Struts CVE), but the design flaw underneath it was that a single internet-facing web server had unrestricted read access to the entire consumer database with no network segmentation or least-privilege boundary — so one compromised process leaked ~147 million records instead of a limited slice. A design control of network segmentation + least-privilege data access per service would have limited the blast radius even after the same code-level bug occurred — the same principle as this week's class fix: don't let one compromised component reach everything.

3. Of your five mitigations, which gives the most risk reduction per unit of effort, and why?

   Mitigation #1 (server-generated UUID filenames for `/upload`, from the top-5 table in `threat-model-6531503080.md`) gives the most risk reduction per unit of effort: it's a ~10-line change confined to one function, it's already implemented and verified (before/after evidence, commit `a767efc`), and it closes an entire *class* of path/filename attacks (traversal, absolute paths, null bytes, future bypass tricks) rather than one instance — compared to, say, adding auth to `/notes` (#3), which needs a whole session/auth layer to be added first.

## Grading rubric (100)
| Criterion | Points |
|---|---|
| Lecture questions (Part 2) | 20 |
| Exploitation + evidence (DFD + STRIDE table + EoP findings + screenshots) | 40 |
| Defense (top-5 ranking + mitigations) | 25 |
| Reflection (CWE/OWASP mapping + breach + best mitigation) | 15 |

**Assessed within the rows above** (they are not extra points — they are what those points are for):
- **Systems-level reasoning** (inside *Exploitation + evidence*, Task 3b): does the model reach past single elements to boundaries, reachability and chains? Scored with the STRIDE + systems-thinking rubrics of [Joshi et al. 2024](https://arxiv.org/abs/2404.16632).
- **Defensive proof** (inside *Defense*, Task 8): a claimed mitigation with no before/after evidence scores at most half. A mitigation you can show closing a *class* scores full.
- **Adversarial thinking** (across the whole sheet): do the abuse cases, personas and chains show you reasoning as an attacker with goals and constraints — or just listing categories? This is the course's central disposition and it is assessed, not assumed.

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/diagram must show a terminal running `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'` **in the
  same image as the evidence**. When the evidence is a browser page, a DevTools panel or a
  rendered response, put that terminal **beside the browser and capture the whole screen** — a
  cropped window carries nothing that identifies you, and the lab's own output is
  byte-identical for the whole cohort *by design*, so the stamp is the only thing that makes
  the shot yours. Generic or borrowed evidence is not accepted.
- **Personalized flag (if this lab issues one):** N/A — Week 1 (threat modeling) does not issue a ctf.zcr.ai flag; this lab is modeling-only (see the Ethics note at the top of this worksheet).
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the vulnerability work**?

     I traced `/upload` in `sample-app/app.py`: it took the client-supplied `f.filename` as-is and built the save path with `os.path.join(UPLOAD_DIR, f.filename)`. `os.path.join` does not confine the result inside `UPLOAD_DIR` — if `f.filename` contains `../`, the joined path walks back out of `uploads/` before Python ever writes the file. So sending a file with `filename=../evil-6531503080.txt` made the server write to `/app/evil-6531503080.txt`, right next to `app.py` and `notes.db`, instead of inside `uploads/`. It worked because the server trusted a value it never should have trusted for that purpose — the client fully controls `filename`, and nothing checked it before using it to build a path (Trust Boundary Violation, CWE-501 / CWE-22).

  2. **Why does your fix actually stop it** — and what could still break it?

     The fix (commit `a767efc`) stops using the client-supplied filename to build the path at all: the server generates the on-disk name itself with `uuid.uuid4().hex` plus an extension checked against an allow-list regex (`^\.[A-Za-z0-9]{1,10}$`), and only stores the client's original filename as a display label (`original_filename`) that is never passed to a filesystem call. Because no attacker-controlled string ever becomes part of the path, `../`, absolute paths, null bytes, and unicode tricks all stop mattering — there's nothing left to sanitize. What could still break it: if a future change reintroduces the client filename into any filesystem call (e.g. a "download by original name" feature built carelessly), or if the extension allow-list regex itself is loosened to accept something dangerous (e.g. `.php` on a server that also executes uploaded files) — the mitigation only holds as long as `original_filename` stays purely cosmetic.

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

1. Ask an AI assistant to exploit **or** fix this week's vulnerability. Paste its full answer.
2. **Find what's wrong or risky** in it — insecure code, a subtly incomplete fix, a hallucinated API/function/CVE, a missed edge case, or wrong reasoning. Quote the exact line(s).
3. Produce the **correct, verified** version yourself and explain in 2–3 sentences why the AI's output was insufficient.

> Disclose your AI use in the Part 1 table. This task counts toward your **Defense + Reflection** score.

**1. Prompt given:** "Fix the path traversal vulnerability in this Flask `/upload` route: `f.save(os.path.join(UPLOAD_DIR, f.filename))`."

**AI's full answer:**
> You can fix this by sanitizing the filename with Werkzeug's `secure_filename()` before saving:
> ```python
> from werkzeug.utils import secure_filename
>
> @app.route("/upload", methods=["POST"])
> def upload():
>     f = request.files["file"]
>     filename = secure_filename(f.filename)
>     f.save(os.path.join(UPLOAD_DIR, filename))
>     return {"saved": filename}
> ```
> `secure_filename()` strips path separators and normalizes the filename, so `../../etc/passwd` becomes a safe string like `etc_passwd`, and the traversal is neutralized.

**2. What's wrong / risky, quoted:**
- `return {"saved": filename}` — the AI kept echoing the (now-sanitized) filename back in the response. This still leaks internal naming to the client and, more importantly, the AI never mentioned an **extension allow-list**, so a file like `shell.php` or `payload.sh` sanitizes to itself unchanged and still gets saved with an executable extension.
- `secure_filename()` strips *known* dangerous patterns (path separators, `..`) but the client-supplied string is still what ends up in the path — it's an **instance fix**, not a class fix. The AI's answer never says this or discusses the tradeoff; it presents `secure_filename()` as a complete solution ("the traversal is neutralized"), which overstates it. Werkzeug's own docs note edge cases (e.g. filenames that are pure dots/unicode after stripping can collapse to an empty string, which `secure_filename()` itself warns can still collide or fail silently).
- No collision handling: two uploads named the same sanitized filename overwrite each other silently — a minor availability/integrity issue the AI's answer doesn't address.

**3. Correct, verified version (what I actually implemented — commit `a767efc`):** generate the on-disk filename server-side with `uuid.uuid4().hex`, validate the extension against an allow-list regex (`^\.[A-Za-z0-9]{1,10}$`), and keep the client's original filename only as a cosmetic `original_filename` field that never touches the filesystem path — see Task 8 in `threat-model-6531503080.md` for the full before/after evidence. This is insufficient-vs-sufficient because the AI's fix still lets attacker input reach the path (just filtered), so it depends on the filter staying correct forever; my fix removes attacker input from the path entirely, so there's no filter left to bypass, and it also closes the file-type/extension gap the AI's answer missed.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** In 2–3 sentences, in your own words, describe what this week's vulnerable code/endpoint actually *does* and *why it is exploitable* — explain the mechanism, don't dump jargon.

`/upload` takes whatever file a visitor sends and saves it using the name the visitor typed for it, glued onto a fixed "uploads" folder path. Because the server never checks that name, a visitor can type a name like `../evil.txt` — the `../` means "go up one folder" — so instead of landing inside the uploads folder, the file gets written one level up, wherever the server can reach, which is not supposed to be reachable from the internet at all.

**B. Prompt Problem.** Write a **single prompt** that makes an AI produce a *correct, secure* fix for one finding. Run it: does the exploit now fail? If not, refine the prompt and try again. Submit the **final prompt + the verified result**.
*Graded on the prompt's precision and your verification — this trains problem decomposition and AI literacy (Denny et al. 2024).*

**Final prompt used:**
> "Fix this Flask upload route so that no part of the client-supplied filename is ever used to construct the on-disk file path — not even after sanitizing it. Generate the save filename entirely server-side (e.g. a UUID), validate the file extension against an allow-list, and keep the client's original filename only as metadata for display, never as part of a path. Here is the vulnerable code: `f.save(os.path.join(UPLOAD_DIR, f.filename))`."

**Verified result:** the AI produced the same design implemented in `sample-app/app.py` — `uuid.uuid4().hex` for the on-disk name, extension checked against `^\.[A-Za-z0-9]{1,10}$`, original filename returned only as `original_filename` in the JSON response, never passed to `os.path.join`. Tested before/after (see Task 8, `threat-model-6531503080.md` and screenshots `task8-before-fix-6531503080.png` / `task8-after-fix-6531503080.png`): sending `filename=../evil2-6531503080.txt` before the fix wrote outside `uploads/`; the identical request after the fix produced `{"original_filename":"../evil2-6531503080.txt","saved":"1cbacbf3f9944356a974354b424b2c65.txt"}` and the file landed only inside `uploads/` — exploit fails on the first try with this prompt, no refinement needed.
