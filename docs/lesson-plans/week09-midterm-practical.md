# Lesson Plan — Week 9: Midterm — Hands-on CTF Practical

| | |
|---|---|
| **Course** | Software Security (⬚ course code) |
| **Week / date** | 9 · ⬚ |
| **Contact time** | 150 min — a single practical-exam block. No lecture, no lab (`AGENDA.md`, *Week 9 — Midterm CTF practical (150 min)*) |
| **Lab folder** | `labs/week09-midterm-practical` — holds `README.md` and `ctf.md` (the student paper); it ships no target of its own |
| **Slides** | `slides/week09.md` — proctor deck, not a teaching deck |
| **Covers** | Weeks 1–6 (`labs/week09-midterm-practical/README.md`). The seven challenges themselves draw on Weeks 3–6; threat modelling and CWE/OWASP mapping (W1–W2 material) are examined in the Week 8 written paper |
| **Targets** | `labs/week03-cryptography` · `labs/week04-injection` · `labs/week05-xss-client-side` · `labs/week06-authn-authz` (`ctf.md`, *Targets*) |
| **Standards** | The ids the source weeks' READMEs attach: **A04** Cryptographic Failures · CWE-327, CWE-916, CWE-330 (W3) · **A05** Injection · CWE-89, CWE-78 (W4) · **A05** Injection · CWE-79, CWE-352 (W5) · **A01** Broken Access Control, **A07** Authentication Failures · CWE-639, CWE-287 (W6) |
| **CLOs addressed** | **CLO2** exploit · **CLO3** remediate · **CLO6** evidence & ethics (course specification §6, row 9) |

---

## 1. Session objectives

This is an assessment, not a teaching session. What the sitting is designed to evidence:

**Knowledge (K)**
- K1 — For each challenge solved, state in one line the control that would have prevented it (`ctf.md` requires a **mitigation** column per challenge).
- K2 — Recognise which vulnerability class a target's behaviour belongs to *without* task scaffolding: unlike the weekly worksheets, `ctf.md` states only the goal of each challenge.

**Skills (P)**
- P1 — Log in as `admin` without the password, and read a file via the `host` parameter, on the injection target (challenges 1–2, W4).
- P2 — Fire `alert(document.domain)` stored for another user (challenge 3, W5).
- P3 — Read another user's order object, and become admin with a forged JWT (challenges 4–5, W6).
- P4 — Recover a password from a weak hash, and recover the plaintext structure from the ECB oracle (challenges 6–7, W3).
- P5 — Record, per challenge, the **flag/proof**, the **payload or command**, and a **one-line mitigation** — the three columns of `ctf.md`'s submission table.

**Attitude (A)**
- A1 — Attack only the supplied sandbox targets, under [ETHICS.md](../../ETHICS.md) (`ctf.md`, *Rules*).
- A2 — Work individually — no collaboration (`ctf.md`, *Rules*).
- A3 — Submit evidence that is identifiably their own and that they can reproduce on request ([SUBMISSION.md](../../SUBMISSION.md), *Academic Integrity*).

## 2. What is assessed

Seven challenges, 100 points, 150 minutes, individual (`ctf.md`). They are **not** independently
hosted: only four targets carry the seven challenges (`ctf.md`, *Targets*) — `week04-injection`
carries challenges 1–2 (30 pts), `week06-authn-authz` carries 4–5 (30 pts), and
`week03-cryptography` carries 6–7 (25 pts); only `week05-xss-client-side` (challenge 3, 15 pts) is
single-challenge. A target that will not start therefore costs a student every challenge it hosts,
not one.

| # | Title (as printed in `ctf.md`) | Topic | Source week | Pts |
|---|---|---|---|---:|
| 1 | **Boolean Bypass** — log in as `admin` without the password | SQLi | W4 | 15 |
| 2 | **Shell Out** — read a file via the `host` parameter | Command injection | W4 | 15 |
| 3 | **Pop the Alert** — fire `alert(document.domain)` stored for another user | Stored XSS | W5 | 15 |
| 4 | **Not Your Order** — read another user's order object | IDOR | W6 | 15 |
| 5 | **Forge Ahead** — become admin with a forged JWT | Broken JWT | W6 | 15 |
| 6 | **Crack It** — recover a password from a weak hash | Crypto | W3 | 15 |
| 7 | **Penguin** — recover the plaintext structure from the ECB oracle | Crypto | W3 | 10 |

The READMEs attach OWASP/CWE ids at **week** level (header table above), not per challenge;
challenge-level attribution is left to the marking key.

**CLO coverage.** Challenges 1–7 evidence **CLO2**. The per-challenge mitigation line is the
**CLO3** evidence available in a 150-minute practical — there is no defend-and-re-test task here, as
there is in a teaching week. Per-student flags and identity-stamped evidence carry **CLO6**.

## 3. Preparation and infrastructure readiness

### 3.1 What this sitting runs on

- **Graded flags come from the hosted platform.** Each student spawns their **own** instance of
  challenges 1–5 and 7 in the course's hosted CTFd (`ctf.zcr.ai`, container-spawning plugin). The
  platform issues that student a flag per challenge — an HMAC of student ID + challenge key with the
  cohort salt (`airsec_flag_bridge`) — so a flag can be traced to the student it was issued to and no
  student can read it out of their own machine. Students reach their instances over the arena WireGuard
  VPN with their own arena account ([arena-vpn-guide](../arena-vpn-guide.md)); confirm every student has set
  it up **before** the day.
- **Local Docker is practice only.** The lab folders' compose files serve the public `…_demo` flags
  when no `.env` is present. Do **not** plan graded flags around giving each student a per-student
  `.env`: the student owns the machine and the file, so `cat .env` / `docker exec … env` reveals every
  flag before any exploitation. (At the first sitting, 19 Sep 2026, `ctf.md` listed local
  Docker targets; roughly two thirds of the cohort had no per-student flag, and 38 of the 40
  per-student flags claimed by the students who used the hosted instances matched the issued table —
  the other 2 came from outside the platform.)
- **All seven challenges now have a hosted, per-student instance** (as of 24 Sep 2026 — `airsec/w03-crack`
  is live, image `airsec/w03-crack:dev`, flag key `crack`; verified end-to-end: spawn, crack, submit,
  `seed_flags.py verify` all confirmed). §3.2 lists the images.
- **CTFd's scoreboard is engagement, not the grade.** Marks come from the answer key applied to the
  submission of record, not from the board. Freeze the board for the exam window
  (CTFd → Settings → Freeze time, `CTFd-SETUP.md` §4).
- **Submission of record.** Flags + payload + mitigation via the CTF Form / Classroom
  ([SUBMISSION.md](../../SUBMISSION.md), *Exams*). `ctf.md`'s own submission table is the paper form
  of the same three columns.

### 3.2 Per-student flags — hosted platform

The instructor-side tooling is still used for the **table and for attribution at marking** (the hosted
platform derives its flags from the same salt, so `verify` resolves them):

```bash
export FLAG_SALT='<this cohort's salt — never published>'   # instructor/anti-cheating.md §A
python3 instructor/seed_flags.py gen students.txt -o flags.csv     # authoritative table
python3 instructor/seed_flags.py verify 'FLAG{...}' students.txt   # who was this issued to?
```

Two dependencies that fail *before* anything is generated: `instructor/seed_flags.py` is a shim that
forwards `FLAG_SALT` to `SWSEC_FLAG_SALT` and requires the sibling `KOSEN69 - curriculum` monorepo —
without it, it exits with `ERROR: curriculum monorepo not found at …`.

**Which challenges have a hosted, per-student instance** (from the live CTFd catalog, checked 24 Sep 2026):

| Challenge | Hosted image | Per-student flag |
|---|---|---|
| 1 Boolean Bypass (SQLi) | `w04-sqli` | yes |
| 2 Shell Out (command injection) | `w04-cmdi` | yes |
| 3 Pop the Alert (stored XSS) | `w05-xss` | yes |
| 4 Not Your Order (IDOR) | `w06-idor` | yes |
| 5 Forge Ahead (JWT) | `w06-jwt` | yes |
| 6 Crack It (weak hash) | `w03-crack` | yes |
| 7 Penguin (ECB) | `w03-ecb` | yes |

The local lab folders (`labs/week04-injection`, `labs/week06-authn-authz`) still read `FLAG_*` from the
environment with a `…_demo` fallback; that is for practice and for the Week 4 / 6 teaching sessions.
`labs/week05-xss-client-side` and `labs/week03-cryptography` have no `environment:` block and never
served per-student flags locally.

**Pre-flight (the day before).** Spawn each of the seven hosted challenges once as a test student and
check that the flag it returns resolves with `seed_flags.py verify` **using the same salt**. Any `…_demo`
flag on a submission sheet means the student ran a local copy, not that they cheated: ask which
instance they used before anything else.

### 3.3 Room, network, machines

- Room / seating / invigilator count: ⬚ (not recorded in this repository).
- Students work on their own machines; "phones away; one device" (`instructor/anti-cheating.md` §C).
- Network is needed for **every** graded challenge: the hosted instances are reached over the network,
  as is the submission Form. Have each student log in to CTFd and spawn a first instance **before the
  clock starts** (§4). Local Docker (image and `pip` fetches at start-up) is only for practice.
- The deck's own instruction: confirm in the first 5 min that everyone can log in to CTFd and reach a
  spawned instance (`slides/week09.md`, speaker note).

### 3.4 Test the day before

- [ ] **Hosted platform up for the cohort.** Every student has an arena account and VPN set up ([arena-vpn-guide](../arena-vpn-guide.md)) and can spawn and
      reach an instance; each of the seven hosted challenges spawns (§3.2
      pre-flight). A shared instance that issues one flag to everyone makes the per-student flags
      decorative.
- [ ] Practice only, if you still want the local targets up for the Week 7 warm-up:
      `docker pull python:3.12-slim`; the three web labs answer on `http://localhost:8080` one at a
      time; `labs/week03-cryptography` publishes no port and runs its compose command
      (`pycryptodome`, `argon2-cffi`, then `vulnerable_crypto.py`), with `hashes.txt` in the folder.
      These serve `…_demo` flags and are **not** graded targets.
- [ ] `python3 instructor/seed_flags.py verify '<one issued flag>' students.txt` resolves to the
      right student, **using the same salt** that `gen` ran with.
- [ ] Optional, if the CTFd catalog is in use: `python3 instructor/check_flag_keys.py` exits 0
      (flag-key vocabulary in sync — `instructor/platform-build/README.md`, *Guardrails*).
- [ ] CTFd scoreboard frozen for the window; submission Form open/close times set, with the Form
      settings from `instructor/anti-cheating.md` §C (restrict to the cohort's accounts, collect
      email, one response, auto-close).
- [ ] Challenge 6's hosted instance serves its own candidate list (`GET /wordlist.txt`, ~2,200
      entries — small enough to crack with a plain Python loop, no `hashcat`/`john` required). A
      cracker is still convenient: mention it's optional, not a blocker.
- [ ] The Week 7 mock CTF has been run — `labs/week07-review-midterm-prep/mock-ctf.md` states
      "Format: same as the Week 9 midterm practical", ungraded, hints included. `README.md` tells
      students to warm up on it.

## 4. Run of show — the 150-minute block

Timings are `AGENDA.md`'s (*Week 9 — Midterm CTF practical*): `0:00–0:10 rules + target check ·
0:10–2:30 solve challenges · submit flags`.

| Time | Block | Instructor does | Students do |
|---|---|---|---|
| 0:00–0:10 | **Briefing + target check** | Run `slides/week09.md`: format (timed, sandbox, each solved challenge = a flag = points), the 150 minutes, that **flags are per-student, come only from your own hosted instance, and copying is traceable**, the four challenge areas, and the rules (sandbox targets only, no collaboration, submit flag + method + mitigation). Confirm everyone can log in to CTFd and reach a spawned instance | Log in, spawn the first instance; report anything that will not connect **now**, not at 1:00 |
| 0:10–2:30 | **Competition window** | Invigilate; answer only environment questions, not challenge questions; watch for the `_demo` tell (a student working on a local copy, §3.2) | Solve challenges 1–7 in any order; fill the three columns per challenge as they go |
| 2:30 | **Submission cutoff** | Close the Form / collect the paper tables; the deck's closing slide is "Submit your flags" | Submit flags + payload/command + one-line mitigation |

**Port note (local practice only).** The three local web labs all publish host port **8080** — they
cannot run at the same time; bring one down before the next, or override the published port (§9).
This is about the local copies; how hosted instances are addressed and whether they collide: ⬚.

The 150-minute block contains **no debrief slot** — see §7.

## 5. Scoring — how points become marks

| Step | Rule | Source |
|---|---|---|
| Per challenge | Flag/proof + payload/command + one-line mitigation = full points | Points: `ctf.md` (challenge table, 6 × 15 + 1 × 10 = 100); scoring rule: `instructor/exams/week09-midterm-practical-ctf-answers.md` (*Scoring*) |
| No flag | Partial credit for documented progress | `ctf.md`; `labs/week09-midterm-practical/README.md` |
| Paper total | 100 pts | `ctf.md` |
| Into the gradebook | **Midterm % = average** of the W8 written and the W9 CTF | `instructor/GRADEBOOK.md` |
| Into the final mark | Midterm block = **20%**, individual — so this sitting carries half of it | `syllabus.md` §6; course specification §4 |

**Individual vs team.** Week 9 is individual end to end (`ctf.md`: *Individual*, "no
collaboration"). There is **no** team component: the Houses / CTFd leaderboard is explicitly
non-graded engagement (`syllabus.md`, *Teams & Houses*; course specification §7), and the team CTF
is Week 19. Nothing on the scoreboard should be transcribed into the gradebook.

**Make-up sittings.** The instructor exam set holds a parallel **Form B for the written papers only**
(`instructor/exams/` — W8 and W18); there is no Form B for the practical. What the deck points at
for rotation is the CTF pool in `instructor/exams/item-bank.md` ("W9 — Midterm CTF extras", covers
W1–6). Absence / make-up / late policy for an exam sitting: ⬚ (institutional).

## 6. Academic-integrity controls actually used

| Control | How it is operated | What it catches |
|---|---|---|
| **Per-student flags (hosted instances)** | Issued by the hosted platform; `seed_flags.py gen` before the day, `verify '<flag>' students.txt` at marking (CTFd's `container_audit_logs` / `container_flag_attempts` add an audit trail) | A flag submitted by one student but *issued* to another — a violation for **both** parties ([SUBMISSION.md](../../SUBMISSION.md)) |
| **Identity-stamped evidence** | Screenshots must carry the student's terminal `whoami` / login email / student ID **and** a timestamp | Borrowed or generic screenshots (`instructor/anti-cheating.md` §B) |
| **Method note per challenge** | The payload/command + mitigation columns of `ctf.md` | A flag held without the mechanism; also the basis for partial credit |
| **Viva / re-demo spot-check** | Pick 2–3 students to reproduce or explain their own submission | Work the student cannot account for (`anti-cheating.md` §D; course specification §7) |
| **Scoreboard freeze** | CTFd → Settings → Freeze time for the window | Progress leaking between students mid-sitting (`CTFd-SETUP.md` §4) |
| **Dynamic scoring + first blood** | Already configured per challenge on CTFd | Reduces the incentive to pool answers (`anti-cheating.md` §C) |
| **Rotation each cohort** | New `FLAG_SALT`, new data seeds, at least one target changed per topic | Last year's flag dump (`anti-cheating.md` §E) |

**Known limits, so they are covered deliberately rather than assumed away:**

- A `…_demo` flag means the student worked on a local copy, **not** that they cheated (§3.2). It proves
  nothing either way; ask which instance they used before accusing anyone.
- A flag `verify` attributes to another student does not by itself say *how* it got there — the 19 Sep
  2026 sitting had two such flags that no platform log explained. Ask both students and check the
  instance/audit logs before deciding.
- `verify` only resolves flags generated with the **same salt**; a salt mismatch looks like an
  unattributable flag.
- Red flags to carry into marking (`anti-cheating.md` §F): identical screenshots across students,
  a flag `verify` attributes elsewhere, prose that does not match the student's own data seed.
- If copying is found: `ETHICS.md` + the conduct process; keep the `verify` output as evidence
  (`anti-cheating.md` §G).

## 7. After the sitting — debrief and how results feed the final mark

- **Debrief.** `AGENDA.md` allocates no debrief inside the 150 minutes. The only adjacent slot the
  timetable offers is the Week 10 lecture's opening block, `0:00–0:10 weekly quiz + recap`
  (`AGENDA.md`, standard teaching-week template); date ⬚. The deck's own close is: collect
  submissions, grade with the answer key + `seed_flags.py verify` for copied flags, preview Week 10
  (APIs) (`slides/week09.md`).
- **Marking.** Key: `instructor/exams/week09-midterm-practical-ctf-answers.md` (git-ignored — never
  copy any of it into this repository's public files).
- **Into the mark.** Enter the score under *Midterm*; the sheet recomputes **Midterm % = average**
  of W8 and W9 (`instructor/GRADEBOOK.md`), and the Classroom import maps
  `grade ÷ maxPoints × 100`. Midterm is 20% of the final mark (`syllabus.md` §6).
- **Into next time.** A challenge nobody solved, or everybody solved, is an item-bank note for the
  W19 pool (`instructor/exams/item-bank.md`).

## 8. Materials

- Paper + brief: `labs/week09-midterm-practical/ctf.md`, `labs/week09-midterm-practical/README.md`
- Proctor deck: `slides/week09.md`
- Targets: the hosted CTFd challenges (SQLi, command injection, stored XSS, IDOR, JWT, weak-hash
  crack, ECB); local practice copies in `labs/week03-cryptography/`, `labs/week04-injection/`,
  `labs/week05-xss-client-side/`, `labs/week06-authn-authz/` (`docker compose up` in each — demo flags)
- Dry run students should have done: `labs/week07-review-midterm-prep/mock-ctf.md`
- Instructor-only (git-ignored): `instructor/seed_flags.py`, `instructor/anti-cheating.md`,
  `instructor/CTFd-SETUP.md`, `instructor/GRADEBOOK.md`,
  `instructor/exams/week09-midterm-practical-ctf-answers.md`, `instructor/exams/item-bank.md`
- Submission channels: [SUBMISSION.md](../../SUBMISSION.md) · Rules of engagement:
  [ETHICS.md](../../ETHICS.md)

## 9. Risks and contingencies

| Risk | Mitigation |
|---|---|
| **Port 8080 collision between targets.** `labs/week04-injection`, `labs/week05-xss-client-side` and `labs/week06-authn-authz` all publish `8080:5000`; the second `docker compose up` fails to bind | Brief it at 0:00–0:10: `docker compose down` one before starting the next, or override the **left** side of the ports mapping. The app listens on 5000 *inside* the container, so do not republish 5000 — macOS AirPlay squats 5000, not 8080 |
| **Student works on a local copy → demo flag.** Compose renders `FLAG_SQLI: null` and the app falls back to the `…_demo` placeholder committed in `vulnerable_app.py` | Brief it: graded flags come only from your own hosted instance (`ctf.md`, *Targets*). Treat a `_demo` flag on a sheet as "worked locally", not as cheating; give it no credit and ask which instance was used |
| **`seed_flags.py` cannot find the curriculum monorepo** — the shim `sys.exit`s with `ERROR: curriculum monorepo not found` and generates nothing | Run `gen` the **day before**, not on the morning; the sibling `KOSEN69 - curriculum` directory must be present |
| **Salt mismatch** between `gen` and `verify` (flags are an HMAC of student ID + challenge keyed by the salt) — attribution silently returns nothing | Record the cohort's `FLAG_SALT` with the `flags.csv` it produced; export the same value before `verify` |
| **PyPI reachability at start-up.** Every target `pip install`s at container start (`flask`; `flask pyjwt`; `pycryptodome argon2-cffi`) — a whole room starting at once needs the network | Pre-pull `python:3.12-slim`; keep a USB `docker save`/`docker load` copy; use the 0:00–0:10 target check to surface failures before the clock matters |
| **Burp on its default listener.** The Week 6 worksheet's optional Burp step points the browser proxy at `127.0.0.1:8080` — the same port the targets publish | Burp is optional for this sitting; move either Burp's listener or the target's published port |
| **Hosted platform unavailable during the sitting** | Local Docker gives only demo flags, so per-student attribution is lost for that window — decide the fallback before the day (extend, reschedule, or accept identity-stamped evidence only) and record it: ⬚. The submission of record is still the CTF Form / Classroom ([SUBMISSION.md](../../SUBMISSION.md)), and `ctf.md`'s submission table works on paper |
| **A shared instance issues one flag to everyone** | Each student must spawn their own instance; check in the pre-flight that two test students get different flags (§3.2) |
| **A student cannot reach the hosted instances** (VPN/network) | Sort it in the 0:00–0:10 target check; no spare-machine provision is recorded in this repository — decide and record it: ⬚ |

**If it fails mid-session — decision order**

1. **Network drops.** Solving is local and the targets are already up; keep going. Hold submissions
   and collect `ctf.md`'s table on paper at 2:30, transcribe afterwards.
2. **One target dies for one student.** They lose every challenge that target hosts (§2) — up to 30
   pts (week04 or week06) or 25 pts (week03), 15 pts if it's week05 — not the whole paper. Note it
   against their sheet for partial credit.
3. **The Form / CTFd dies.** The paper table becomes the record; nothing else changes.
4. **Widespread failure to start targets inside the first 10 minutes.** That is exactly what the
   `0:00–0:10` target check exists to expose. The repository defines no fallback adjustment to the
   150-minute window — the decision and its justification are the instructor's, and must be
   recorded: ⬚.

## 10. Post-teaching reflection

*Complete after the session — this also feeds the course's engagement data.*

- Attendance / completion: ⬚
- Time actually taken per task (vs. plan): ⬚
- Where the class got stuck, and what unblocked them: ⬚
- Challenge with the lowest solve rate, and what that says about the week it came from: ⬚
- Integrity flags raised by `seed_flags.py verify`, and how each resolved: ⬚
- Anything to change before this week runs again: ⬚
