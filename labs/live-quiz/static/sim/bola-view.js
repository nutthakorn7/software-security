/* bola-view.js — Week 10 simulation.
 *
 * WHAT THIS IS FOR
 * "The endpoint doesn't check ownership" is abstract until a student picks a
 * login, asks for a different user's id, and watches the orders come back with
 * a 200 anyway. This re-implements both get_orders() paths from this week's
 * real API code:
 *
 *   vulnerable_api.py:  return orders_for(id)          -- never reads the caller
 *   solution_api.py:     caller = request X-User-Id
 *                         if caller is None: 401
 *                         if caller != id and not is_admin(caller): 403
 *                         return orders_for(id)
 *
 * Nothing is sent anywhere; the two servers' logic is computed in the page.
 */
(function () {
  "use strict";

  // Seeded users + their orders, matching this week's vulnerable_api.py.
  var USERS = {
    "1": { name: "alice", admin: false, order: "AirPods" },
    "2": { name: "bob",   admin: false, order: "Laptop stand" },
    "3": { name: "carol", admin: true,  order: "Server rack · FLAG{bola_demo}" }
  };

  var PRESETS = [
    { label: "read a stranger's orders", identity: "1", reqid: "2", mode: "vuln" },
    { label: "same request, fixed server", identity: "1", reqid: "2", mode: "fixed" },
    { label: "no login at all", identity: "none", reqid: "1", mode: "fixed" },
    { label: "read your own", identity: "1", reqid: "1", mode: "fixed" }
  ];

  var identity = document.getElementById("identity");
  var reqid = document.getElementById("reqid");
  var modeVuln = document.getElementById("mode-vuln");
  var modeFixed = document.getElementById("mode-fixed");
  var presetsEl = document.getElementById("presets");
  var reqlineEl = document.getElementById("reqline");
  var statusEl = document.getElementById("status");
  var bodyEl = document.getElementById("bodyout");
  var verdictEl = document.getElementById("verdict");
  var explainEl = document.getElementById("explain");

  function setStatus(code, text, kind) {
    statusEl.textContent = code + " " + text;
    statusEl.className = "bola-status bola-" + kind; // ok | denied
  }

  function update() {
    var who = identity.value;              // "none" | "1" | "2"
    var want = reqid.value;                // "1" | "2" | "3"
    var fixed = modeFixed.checked;
    var target = USERS[want];

    var hdr = who === "none" ? "(none)" : "X-User-Id: " + who;
    reqlineEl.innerHTML = "";
    var r1 = document.createElement("code");
    r1.textContent = "GET /api/users/" + want + "/orders";
    var r2 = document.createElement("span");
    r2.className = "bola-hdr";
    r2.textContent = "  header " + hdr;
    reqlineEl.appendChild(r1);
    reqlineEl.appendChild(r2);

    bodyEl.textContent = "";

    if (!fixed) {
      // vulnerable_api.py: orders handed back for whatever id was asked, no check.
      setStatus(200, "OK", "ok");
      bodyEl.textContent = target.name + "'s orders: " + target.order;
      var mine = who === want;
      if (mine) {
        verdictEl.className = "verdict ok";
        verdictEl.textContent = "You read your own orders — but only by coincidence.";
        explainEl.textContent = "The code returned id " + want + "'s orders without checking who you are. "
          + "It happens to match your login this time; change the requested id and it still returns.";
      } else {
        verdictEl.className = "verdict bad";
        verdictEl.textContent = "BOLA — you just read " + target.name + "'s orders"
          + (who === "none" ? " with no login at all." : " while logged in as " + USERS[who].name + ".");
        explainEl.textContent = "get_orders() never reads the caller. There is no check to spoof and none runs — "
          + "the id in the URL is the only thing that decides what comes back.";
      }
      return;
    }

    // solution_api.py: 401 (no identity) -> 403 (not owner) -> 200 (owner/admin).
    if (who === "none") {
      setStatus(401, "Unauthorized", "denied");
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "No identity → the server won't even look at the object.";
      explainEl.textContent = "The fixed handler reads X-User-Id first. With no header it can't know who you are, "
        + "so it refuses before touching any orders.";
      return;
    }
    var caller = USERS[who];
    if (who !== want && !caller.admin) {
      setStatus(403, "Forbidden", "denied");
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Known caller, but the object isn't yours → blocked.";
      explainEl.textContent = caller.name + " (id " + who + ") asked for id " + want + "'s orders. "
        + "The one added check — caller owns the object, or is admin — fails, so the server returns 403 "
        + "instead of the data.";
      return;
    }
    setStatus(200, "OK", "ok");
    bodyEl.textContent = target.name + "'s orders: " + target.order;
    verdictEl.className = "verdict ok";
    if (caller.admin && who !== want) {
      verdictEl.textContent = "Allowed — carol is admin, so the ownership check passes.";
      explainEl.textContent = "The check is \"caller owns the object OR is admin.\" Admin is the one "
        + "legitimate way to read another user's object; a normal user gets 403.";
    } else {
      verdictEl.textContent = "Allowed — you own this object.";
      explainEl.textContent = "caller == id, so the ownership check passes and the same orders are returned — "
        + "this is the only case where 200 is correct.";
    }
  }

  PRESETS.forEach(function (p) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = p.label;
    b.addEventListener("click", function () {
      identity.value = p.identity;
      reqid.value = p.reqid;
      if (p.mode === "fixed") { modeFixed.checked = true; } else { modeVuln.checked = true; }
      update();
    });
    presetsEl.appendChild(b);
  });

  identity.addEventListener("change", update);
  reqid.addEventListener("change", update);
  modeVuln.addEventListener("change", update);
  modeFixed.addEventListener("change", update);
  update();
})();
