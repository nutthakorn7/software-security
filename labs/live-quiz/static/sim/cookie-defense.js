/* cookie-defense.js — Week 5 simulation.
 *
 * WHAT THIS IS FOR
 * Students leave this week thinking "SameSite stops CSRF" and "HttpOnly stops
 * XSS." Each is half true, and the lab's own Task 4 vs Task 5 is built on the
 * gap. This models the two attacks against this week's real handlers so the
 * student can see which flag moves which outcome:
 *
 *   vulnerable_app.py:40  set_cookie("session","abc123")          # no flags
 *   fixed_app.py:42       set_cookie(..., httponly, samesite=Strict, secure)
 *   BOTH apps /comments:  COMMENTS.append(request.form["body"])   # no token, no cookie check
 *   vulnerable renders comments RAW (XSS runs); fixed escapes them (XSS inert)
 *
 * Two independent truths the real code forces:
 *  - Cookie theft via stored XSS needs the script to RUN (output not escaped)
 *    AND the cookie to be JS-readable (no HttpOnly). Two separate layers.
 *  - A forged cross-site POST: SameSite decides whether the cookie is ATTACHED,
 *    but /comments posts the comment regardless, because it checks no cookie and
 *    no token. So cookie hardening never closes CSRF here — a server-side token
 *    does. That is exactly why Task 5's PoC still works against fixed_app.py.
 *
 * Nothing runs or is sent anywhere; both outcomes are computed in the page.
 */
(function () {
  "use strict";

  var encEl = document.getElementById("enc");
  var httpOnlyEl = document.getElementById("httponly");
  var sameSiteEl = document.getElementById("samesite");
  var tokenEl = document.getElementById("csrftoken");
  var presetsEl = document.getElementById("presets");

  var xssStatus = document.getElementById("xss-status");
  var xssDetail = document.getElementById("xss-detail");
  var csrfStatus = document.getElementById("csrf-status");
  var csrfDetail = document.getElementById("csrf-detail");

  var PRESETS = [
    { label: "vulnerable_app.py", enc: "raw", httponly: false, samesite: "unset", token: false },
    { label: "fixed_app.py (cookie hardened + escaped)", enc: "escaped", httponly: true, samesite: "Strict", token: false },
    { label: "HttpOnly on, but output still raw", enc: "raw", httponly: true, samesite: "unset", token: false },
    { label: "the real CSRF fix: add a token", enc: "escaped", httponly: true, samesite: "Strict", token: true }
  ];

  function set(el, text, kind) {
    el.textContent = text;
    el.className = "cookie-line cookie-" + kind; // ok | bad | warn
  }

  function line(parent, label, value, good) {
    var row = document.createElement("div");
    row.className = "cookie-axis";
    var k = document.createElement("span");
    k.className = "cookie-axis-k";
    k.textContent = label + ": ";
    var v = document.createElement("span");
    v.className = "cookie-axis-v cookie-" + (good ? "ok" : "bad");
    v.textContent = value;
    row.appendChild(k); row.appendChild(v);
    parent.appendChild(row);
  }

  function update() {
    var raw = encEl.value === "raw";
    var httpOnly = httpOnlyEl.checked;
    var sameSite = sameSiteEl.value;      // unset | Lax | Strict
    var tokenReq = tokenEl.checked;

    // ---- Attack A: stored XSS -> cookie theft ----
    xssDetail.textContent = "";
    if (!raw) {
      set(xssStatus, "stored as text — never executes", "ok");
      line(xssDetail, "output encoding", "escaped — the injected script tag is printed as text", true);
      line(xssDetail, "result", "no code runs, nothing to steal", true);
    } else if (!httpOnly) {
      set(xssStatus, "cookie stolen — document.cookie leaks", "bad");
      line(xssDetail, "output encoding", "raw — your injected script tag executes in the origin", false);
      line(xssDetail, "HttpOnly", "off — document.cookie = \"session=abc123\"", false);
      line(xssDetail, "result", "the beacon exfiltrates the session", false);
    } else {
      set(xssStatus, "script runs, but the cookie is hidden", "warn");
      line(xssDetail, "output encoding", "raw — the injected script tag still executes (defacement/keylogging)", false);
      line(xssDetail, "HttpOnly", "on — document.cookie is empty for session", true);
      line(xssDetail, "result", "THIS theft fails — but encoding, not HttpOnly, was the missing layer", false);
    }

    // ---- Attack B: forged cross-site POST to /comments ----
    csrfDetail.textContent = "";
    var attached = sameSite === "unset";      // lab treats an unset cookie as sent cross-site
    var posted = !tokenReq;                    // /comments posts unless a token is demanded
    line(csrfDetail, "cookie attached to the cross-site POST",
      attached ? "yes — SameSite not set" : "no — SameSite=" + sameSite + " withholds it", attached ? false : true);
    line(csrfDetail, "comment actually posted",
      posted ? "yes — /comments checks no token" : "no — 403, CSRF token required", posted ? false : true);
    if (posted) {
      set(csrfStatus, attached ? "forged comment posted (cookie rode along)"
                               : "forged comment posted — even though the cookie was withheld", "bad");
      var row = document.createElement("div");
      row.className = "cookie-note";
      row.textContent = attached
        ? "SameSite is unset, so the browser attaches session cross-site — but that is not even needed: /comments never reads the cookie or a token, so the POST succeeds on its own."
        : "SameSite=" + sameSite + " stopped the cookie from being attached, yet the comment STILL posted. Hardening the cookie changed who carries it, not whether /comments accepts it. This is Task 5: the fix doesn't close CSRF.";
      csrfDetail.appendChild(row);
    } else {
      set(csrfStatus, "forged POST rejected — 403", "ok");
      var r2 = document.createElement("div");
      r2.className = "cookie-note";
      r2.textContent = "/comments now requires a per-session CSRF token the attacker's page cannot read "
        + "(same-origin policy). THIS — a server-side check tied to the session — is what actually stops the "
        + "forgery, not the cookie flag.";
      csrfDetail.appendChild(r2);
    }
  }

  PRESETS.forEach(function (p) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = p.label;
    b.addEventListener("click", function () {
      encEl.value = p.enc;
      httpOnlyEl.checked = p.httponly;
      sameSiteEl.value = p.samesite;
      tokenEl.checked = p.token;
      update();
    });
    presetsEl.appendChild(b);
  });

  encEl.addEventListener("change", update);
  httpOnlyEl.addEventListener("change", update);
  sameSiteEl.addEventListener("change", update);
  tokenEl.addEventListener("change", update);
  update();
})();
