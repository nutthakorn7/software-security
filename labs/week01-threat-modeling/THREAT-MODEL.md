# Threat Model — Flask Sample Application (Week 1)

## 1. Data-flow diagram
![Data Flow Diagram](task1-dfd.png)
*(Trust boundary crossed: Internet → Application process boundary)*

## 2. Elements & trust boundaries
| Element | Type (process/store/entity/flow) | Trust boundary crossed? |
|---|---|---|
| Web client | external entity | yes (Internet → Flask app boundary) |
| Flask app (`app.py`) | process | yes (receives untrusted external HTTP inputs) |
| SQLite DB (`notes.db`) | data store | no (internal process storage) |
| `uploads/` store | data store | yes (accessible via HTTP serving & path traversal) |
| `/notes` flow | data flow | yes (untrusted JSON input → DB insert & full read) |
| `/upload` flow | data flow | yes (untrusted file payload → raw disk write) |
| `/files/<name>` flow | data flow | yes (untrusted URL param → file read) |

## 3. STRIDE analysis

| Element | Spoofing (S) | Tampering (T) | Repudiation (R) | Information Disclosure (I) | Denial of Service (D) | Elevation of Privilege (E) |
|---|---|---|---|---|---|---|
| **/notes** | Client supplies arbitrary `owner` string (`request.json.get("owner")`) without authentication; anyone can impersonate any user. | Unauthenticated clients can insert arbitrary or corrupted note bodies into `notes.db`. | No request logging or audit trail; impossible to prove who created or modified a note. | `GET` / `POST` returns **all** records from `notes.db` (`SELECT id, owner, body FROM notes`) to any unauthenticated caller. | No payload size limits, rate limiting, or pagination; attacker can flood DB with huge bodies to exhaust disk/RAM. | Impersonating `owner="admin"` or reading confidential notes allows an attacker to gain unauthorized privileges. |
| **/upload** | Upload endpoint is unauthenticated; anonymous clients can upload files claiming to be system files or other users. | `f.save(os.path.join(UPLOAD_DIR, f.filename))` uses raw filename. Path traversal (`../../app.py`) allows arbitrary file write/overwrite. | No upload logging (no client IP, timestamp, or file hash logged); actions cannot be traced back to caller. | Echoes back internal save paths in response `{"saved": f.filename}`; error tracebacks expose filesystem structure. | No file size limits (`MAX_CONTENT_LENGTH`) or rate limits; large uploads can exhaust disk space (Disk Exhaustion DoS). | Overwriting application code (`app.py`) or system scripts via path traversal leads to Remote Code Execution (RCE) as Flask process. |
| **/files/<name>** | File retrieval is unauthenticated; anyone can request any filename without identity verification. | Low for direct path traversal on read (defended by Werkzeug `send_from_directory`), but reads tampered files uploaded via `/upload`. | No read/download access logging; cannot trace who retrieved sensitive uploaded files. | Unrestricted public access to `uploads/` directory; any user who knows/guesses a filename can download sensitive files. | No rate limiting or bandwidth throttling; mass repeated downloads consume network bandwidth and disk I/O. | Accessing sensitive uploaded files (e.g. system configs, DB backups, keys) grants elevated access to attackers. |
| **SQLite DB (`notes.db`)** | No DB-level authentication; Flask process opens file directly. | Database rows modified by unvalidated web input. | SQLite engine does not log row insertions or access attempts. | Database file stored unencrypted on disk; readable if server filesystem is compromised. | Concurrent write contention or storage exhaustion from unconstrained inserts. | Process running Flask owns DB file; compromise of process gives full DB access. |
| **`uploads/` store** | No file ownership or metadata enforced on disk. | Files can be overwritten directly if filenames collide or path traversal occurs. | No filesystem file modification auditing. | Web-accessible directory permits directory listing or direct download if names are known. | Unrestricted disk allocation can fill the partition. | Saved executable/script files could be executed if web server executes CGIs or scripts. |

## 4. Top 5 risks (likelihood × impact) + mitigation
1. **Arbitrary File Write / Path Traversal via `/upload` (Tampering / Elevation of Privilege)**
   - *Risk:* High Likelihood × Critical Impact.
   - *Mitigation:* Sanitize input filenames using `werkzeug.utils.secure_filename()`, validate file extensions against an allow-list, and store uploaded files outside the web root.
2. **Broken Access Control & Identity Spoofing on `/notes` (Spoofing / Information Disclosure)**
   - *Risk:* High Likelihood × High Impact.
   - *Mitigation:* Implement session-based authentication (e.g. JWT / Cookies) and enforce authorization checks so users can only view and create their own notes.
3. **Unrestricted File Upload / Disk Exhaustion DoS on `/upload` (Denial of Service)**
   - *Risk:* High Likelihood × High Impact.
   - *Mitigation:* Enforce `app.config['MAX_CONTENT_LENGTH']` limit (e.g., 2MB) and implement IP-based rate limiting.
4. **Information Disclosure of All Notes on `/notes` (Information Disclosure)**
   - *Risk:* High Likelihood × High Impact.
   - *Mitigation:* Scope `SELECT` queries to the authenticated user ID (`WHERE owner = ?`) instead of returning `SELECT *`.
5. **Absence of Audit Logging (Repudiation)**
   - *Risk:* Medium Likelihood × Medium Impact.
   - *Mitigation:* Implement centralized application logging capturing timestamp, client IP, user ID, endpoint, and action for all state-changing requests (`POST`).
