# Week 10 — API Security

**OWASP API Security Top 10:** API1 BOLA · API3 broken object property level auth (mass assignment) · API4 unrestricted resource consumption

## Objectives
- Map the REST/GraphQL attack surface.
- Exploit BOLA and mass assignment.
- Add authorization, schema validation, and rate limiting.

## 🥷 Signature game — "crAPI Raid"
Take over accounts/vehicles in the crAPI target; each flag = points on the leaderboard.
```bash
git clone https://github.com/OWASP/crAPI.git
cd crAPI/deploy/docker && docker compose -f docker-compose.yml up -d
```
1. **BOLA:** access another user's vehicle/order by id.
2. **Mass assignment:** set a field you shouldn't (e.g. role/credit) via JSON body.
3. **Resource consumption:** trigger an unthrottled endpoint.
4. **Fix (round 2):** object-level auth checks, explicit allow-listed request schemas, and rate limiting.

## Run the local target
```bash
docker compose up        # vulnerable_api.py on http://localhost:5000 ; solution_api.py on :5001
```
**macOS:** port 5000 is used by AirPlay Receiver — if you see `address already in use`, disable
*System Settings → General → AirDrop & Handoff → AirPlay Receiver*, or (recommended) run the labs
inside the course VM, where there is no conflict.

## Deliverable
Findings report (API Top 10 mapping) + fixes.

## References
- https://owasp.org/API-Security/  ·  https://github.com/OWASP/crAPI
