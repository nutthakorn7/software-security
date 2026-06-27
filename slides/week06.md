---
marp: true
theme: default
paginate: true
header: "Software Security · Week 6"
---

# Week 6
## Authentication, Sessions & Access Control
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Authn vs authz
- Session management & JWT pitfalls
- OAuth2 / OIDC at a glance
- IDOR & broken access control
- 🎮 Game: **IDOR Treasure Hunt + JWT Forgery**

---

## Recap — Week 5

- XSS steals sessions → today we manage them
- Client-side trust is limited — enforce on the server

---

## Authn vs Authz

- **Authentication** — *who are you?* (login, MFA)
- **Authorization** — *what are you allowed to do?*
- Most breaches today are **authz** failures
- Maps to **A01 Broken Access Control**, **A07 Authentication Failures**

---

## Sessions

- Server issues a session token after login
- Stored in cookie (`HttpOnly`, `Secure`, `SameSite`)
- Risks: fixation, predictable IDs, no expiry, no logout invalidation

---

## JWT pitfalls

```text
header.payload.signature
```

- `alg: none` accepted → forge any token
- Weak/guessable HMAC secret → re-sign
- Not checking `exp` / `aud` / signature at all
- Sensitive data in payload (it's only base64!)

---

## OAuth2 / OIDC (high level)

- Delegated access via tokens — don't share passwords
- OIDC adds identity (ID token) on top of OAuth2
- Common bugs: open redirect, missing state, token leakage

---

## IDOR & broken access control

```text
GET /api/orders/1001   → your order
GET /api/orders/1002   → someone else's  😱
```

- Object reference with no ownership check
- Vertical (become admin) vs horizontal (other users)

---

## Access control models

- **MAC** — Mandatory: system-enforced labels (military)
- **DAC** — Discretionary: owner grants access (file perms)
- **RBAC** — Role-Based: permissions via roles
- **RuBAC** — Rule-Based: conditions (time of day, IP)

> Best practices: separation of duties · least privilege · implicit deny

---

## Exercise — RBAC

| Role | Permissions |
|---|---|
| Developer | Read/write Git, JIRA, run unit tests |
| QA Engineer | Read Git, write test reports, JIRA, **deploy to staging** |
| Project Manager | Read Git, JIRA, view dashboard |
| Intern | Read Git, run unit tests |

1. Who may deploy to staging?
2. An intern must create bug entries — which role's perms to add?
3. List all roles that can modify the codebase.

---

## Reading the attack in the logs

Reconstruct the kill chain from Apache logs:

```text
GET /login.php?username=' or 1=1 limit 1; -- a&...   302   ← SQLi admin
POST /upload.php                                     200   ← backdoor
GET /uploads/backdoor.php?cmd=ls%20-l                200   ← RCE
```

- `%20` = space (URL-decode!) · logs let you trace what happened

---

## CWE mapping

- **CWE-639 / CWE-284** — IDOR / improper access control
- **CWE-287** — improper authentication
- **CWE-345 / CWE-347** — insufficient verification / bad signature

---

## Defenses

- **Server-side authorization on every request** (deny by default)
- Check ownership, not just authentication
- Strong session tokens + proper expiry/rotation
- Verify JWT signature, `alg`, `exp`, `aud`; keep secrets strong
- RBAC / ABAC enforced centrally

---

## Tool — Burp Suite workflow

| Tool | Use |
|---|---|
| **Proxy** | intercept & modify requests |
| **Repeater** | replay/tweak one request |
| **Intruder** | automate brute-force/fuzz |
| **Decoder/Comparer** | encode payloads / diff responses |

- Set **scope**, intercept, change a value (e.g. `price=1`), forward
- Test auth, sessions, **IDOR**, privilege escalation

---

## 🗺️ Game — IDOR Treasure Hunt + JWT Forgery

1. Tamper object IDs to reach other users' data → each secret = a flag
2. Forge a weak JWT to become **admin**
3. **Round 2:** implement RBAC checks + fix token signing/verification

---

## Lab steps

1. Find IDOR endpoints; enumerate other users' objects
2. Crack/forge a weak JWT (e.g. `alg:none` or weak secret)
3. Add ownership checks + proper JWT verification
4. Re-test: access denied

---

## Deliverable

- IDOR + JWT findings with impact
- Fixed authorization + token handling
- Proof the forged token / cross-user access now fails

---

## Key takeaways

- Authenticate once, **authorize every request**
- Never trust client-supplied IDs or tokens blindly
- Deny by default

---

# Questions?
Next week: Reflection & review (midterm prep)
