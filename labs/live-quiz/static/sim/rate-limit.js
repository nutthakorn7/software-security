/* rate-limit.js — Week 10 simulation.
 *
 * WHAT THIS IS FOR
 * API4 (Unrestricted Resource Consumption) is the third graded W10 bug and the
 * only one with no sim. "Add a rate limit" sounds obvious until you watch the
 * exact window logic decide who gets a 429 — including a legitimate user with
 * the right password. This re-implements this week's real limiter:
 *
 *   solution_api.py:78  def rate_limited(ip):
 *                          now = time.time()
 *                          _attempts[ip] = [t for t in _attempts[ip] if now - t < 60]
 *                          if len(_attempts[ip]) >= 5: return True      # 429, NOT appended
 *                          _attempts[ip].append(now); return False
 *   solution_api.py:89  login(): if rate_limited(...) -> 429  (BEFORE checking the password)
 *   vulnerable_api.py:73 login(): no limiter -> 401 forever, never 429
 *
 * A virtual clock lets you age timestamps out of the 60s window. Nothing runs or
 * is sent anywhere; the limiter is computed in the page.
 */
(function () {
  "use strict";

  var LIMIT = 5, WINDOW = 60;
  var now = 0;            // virtual clock, seconds
  var attempts = [];      // recorded timestamps, mirroring _attempts[ip]
  var total = 0;          // every send, for the "Nth attempt" narration

  var serverVuln = document.getElementById("server-vuln");
  var serverFixed = document.getElementById("server-fixed");
  var pwEl = document.getElementById("pw-correct");
  var clockEl = document.getElementById("clock");
  var respEl = document.getElementById("resp");
  var windowEl = document.getElementById("window");
  var verdictEl = document.getElementById("verdict");
  var explainEl = document.getElementById("explain");

  function setResp(code, text, kind) {
    respEl.textContent = code + " " + text;
    respEl.className = "ratelimit-resp ratelimit-" + kind; // ok | denied | locked
  }

  function renderWindow() {
    windowEl.textContent = "";
    if (serverVuln.checked) {
      var p = document.createElement("div");
      p.className = "ratelimit-wnone";
      p.textContent = "no limiter on this server — every attempt reaches the password check";
      windowEl.appendChild(p);
      return;
    }
    var head = document.createElement("div");
    head.className = "ratelimit-whead";
    head.textContent = attempts.length + " / " + LIMIT + " slots used in the last " + WINDOW + "s";
    windowEl.appendChild(head);
    attempts.forEach(function (t) {
      var row = document.createElement("div");
      row.className = "ratelimit-wrow";
      row.textContent = "attempt at t=" + t + "s  →  frees at t=" + (t + WINDOW) + "s";
      windowEl.appendChild(row);
    });
    if (!attempts.length) {
      var e = document.createElement("div");
      e.className = "ratelimit-wrow";
      e.textContent = "(window empty — " + LIMIT + " attempts available)";
      windowEl.appendChild(e);
    }
  }

  function send() {
    total += 1;
    var correct = pwEl.checked;

    if (serverVuln.checked) {
      if (correct) { setResp(200, "OK — logged in", "ok"); }
      else { setResp(401, "Unauthorized", "denied"); }
      verdictEl.className = "verdict bad";
      verdictEl.textContent = "Attempt #" + total + " — no throttle, guess forever.";
      explainEl.textContent = "vulnerable_api.py has no limiter, so every request runs the password check and "
        + "returns 401 (or 200). A script can try millions of passwords, and flood the endpoint — that is API4, "
        + "unrestricted resource consumption.";
      renderWindow();
      return;
    }

    // fixed: prune, then the >= check runs BEFORE appending.
    attempts = attempts.filter(function (t) { return now - t < WINDOW; });
    if (attempts.length >= LIMIT) {
      setResp(429, "Too Many Requests", "locked");
      // NOTE: not appended — a rejected attempt does not extend the lockout.
      verdictEl.className = "verdict ok";
      if (correct) {
        verdictEl.textContent = "Locked out — even with the correct password.";
        explainEl.textContent = "The limiter runs BEFORE the password check, so attempt #" + total
          + " gets 429 and the right password is never even looked at. That is the availability cost: a flood of "
          + "wrong guesses locks the real user out too. The 429 is not recorded, so hammering does not push the "
          + "window further out — it clears only as the first 5 timestamps age past " + WINDOW + "s.";
      } else {
        verdictEl.textContent = "429 — brute force stopped at " + LIMIT + " / " + WINDOW + "s.";
        explainEl.textContent = "Five attempts are already in the window, so this one is refused before the password "
          + "check. Note it is NOT added to the window (the >= check returns first), so holding down the button does "
          + "not extend the lockout — advance the clock past a recorded timestamp to free a slot.";
      }
      renderWindow();
      return;
    }
    // under the limit: record it, then check the password.
    attempts.push(now);
    if (correct) {
      setResp(200, "OK — logged in", "ok");
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Allowed — slot " + attempts.length + " of " + LIMIT + ".";
      explainEl.textContent = "Under the limit, so the request is recorded and the password is checked — correct, so "
        + "200. A genuine login costs one slot like any other attempt.";
    } else {
      setResp(401, "Unauthorized", "denied");
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "401 — wrong password, slot " + attempts.length + " of " + LIMIT + " used.";
      explainEl.textContent = "Wrong password returns 401, and this attempt is now counted in the window. After "
        + LIMIT + " in " + WINDOW + "s the next one is a 429 regardless of the password.";
    }
    renderWindow();
  }

  function advance(sec) {
    now += sec;
    clockEl.textContent = "t = " + now + "s";
    // Reflect expiry immediately in the window panel (fixed server only).
    if (serverFixed.checked) {
      attempts = attempts.filter(function (t) { return now - t < WINDOW; });
    }
    renderWindow();
  }

  function reset() {
    now = 0; attempts = []; total = 0;
    clockEl.textContent = "t = 0s";
    respEl.textContent = "— no request yet —";
    respEl.className = "ratelimit-resp";
    verdictEl.className = "verdict";
    verdictEl.textContent = "";
    explainEl.textContent = "";
    renderWindow();
  }

  document.getElementById("send").addEventListener("click", send);
  document.getElementById("adv10").addEventListener("click", function () { advance(10); });
  document.getElementById("adv60").addEventListener("click", function () { advance(60); });
  document.getElementById("reset").addEventListener("click", reset);
  serverVuln.addEventListener("change", renderWindow);
  serverFixed.addEventListener("change", renderWindow);

  reset();
})();
