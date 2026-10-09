/* cmd-inject.js — Week 4 simulation.
 *
 * WHAT THIS IS FOR
 * "shell=True is dangerous" is a slogan until a student types 127.0.0.1;id and
 * watches /bin/sh split one string into two commands. This re-implements this
 * week's real /ping handler in both forms, plus the allow-list the fix adds:
 *
 *   vulnerable_app.py:81  subprocess.run("ping -c 1 " + host, shell=True)
 *   solution_app.py:75    if not re.fullmatch(r"[A-Za-z0-9_.-]+", host): 400
 *   solution_app.py:77    subprocess.run(["ping","-c","1",host], shell=False)
 *
 * It is a STRING TOKENIZER, not a shell: nothing runs, nothing is sent anywhere.
 * The point is to see where the boundary between command and data is — and that
 * an argv list moves that boundary so the shell never re-parses the input.
 *
 * Honest extra beat the fix does NOT close: the allow-list [A-Za-z0-9_.-]+
 * accepts a LEADING '-', so "-h" passes both the regex and argv and reaches
 * ping as an OPTION (CWE-88 argument injection). The real fix is "--" before the
 * host, or rejecting a leading '-'. The sim says so rather than pretending the
 * allow-list is airtight.
 */
(function () {
  "use strict";

  var FLAG = "FLAG{cmdi_demo}"; // the public demo default from vulnerable_app.py:11

  var PRESETS = [
    "127.0.0.1",
    "127.0.0.1;id",
    "127.0.0.1;cat /flag.txt",
    "$(whoami)",
    "8.8.8.8|whoami",
    "-h"
  ];

  var hostEl = document.getElementById("host");
  var presetsEl = document.getElementById("presets");
  var modeVuln = document.getElementById("mode-vuln");
  var modeArgv = document.getElementById("mode-argv");
  var modeAllow = document.getElementById("mode-allow");
  var callEl = document.getElementById("call");
  var statusEl = document.getElementById("status");
  var parseEl = document.getElementById("parseout");
  var verdictEl = document.getElementById("verdict");
  var explainEl = document.getElementById("explain");

  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = "cmdinj-status cmdinj-" + kind; // ran | safe | warn
  }

  // Classify the host string the way /bin/sh would read it (illustrative).
  function classify(host) {
    var sub = host.match(/\$\(([^)]*)\)/) || host.match(/`([^`]*)`/);
    if (sub) return { kind: "subst", cmd: sub[1].trim() };
    var sepIdx = host.search(/;|\|\||\||&&|&/);
    if (sepIdx !== -1) {
      var injected = host.slice(sepIdx).replace(/^\s*(?:;|\|\||\||&&|&)\s*/, "").trim();
      return { kind: "chain", prefix: host.slice(0, sepIdx).trim(), injected: injected };
    }
    return { kind: "plain", host: host };
  }

  function note(cmd) {
    // What the injected/substituted command would reveal — for the verdict text.
    if (/cat\s+\/flag\.txt/.test(cmd)) return "prints the server's flag file → " + FLAG;
    if (/^id\b/.test(cmd)) return "prints the service account's uid/gid";
    if (/^whoami\b/.test(cmd)) return "prints the user the server runs as";
    return "runs as the server user";
  }

  function render(parts) {
    parseEl.textContent = "";
    parts.forEach(function (p) {
      var row = document.createElement("div");
      row.className = "cmdinj-tok cmdinj-" + p.cls; // cmd | data | inj
      row.textContent = p.text;
      parseEl.appendChild(row);
    });
  }

  function update() {
    var host = hostEl.value;
    var c = classify(host);
    var leadingDash = /^-/.test(host);

    if (modeVuln.checked) {
      callEl.textContent = 'subprocess.run("ping -c 1 " + host, shell=True)';
      if (c.kind === "subst") {
        setStatus("injected command ran", "ran");
        render([
          { cls: "cmd", text: "$(" + c.cmd + ")  ← runs FIRST (command substitution)" },
          { cls: "cmd", text: "ping -c 1 " + "<output of " + c.cmd + ">" }
        ]);
        verdictEl.className = "verdict bad";
        verdictEl.textContent = "Command injection — the shell ran your command.";
        explainEl.textContent = "Inside shell=True, $(…) and backticks are command substitution: "
          + c.cmd + " executes before ping and its output is spliced in. It " + note(c.cmd) + ".";
        return;
      }
      if (c.kind === "chain") {
        setStatus("injected command ran", "ran");
        render([
          { cls: "cmd", text: "ping -c 1 " + c.prefix },
          { cls: "inj", text: c.injected + "   ← your injected command" }
        ]);
        verdictEl.className = "verdict bad";
        verdictEl.textContent = "Command injection — a second command ran.";
        explainEl.textContent = "The shell reads ; | & as syntax, so \"ping -c 1 " + c.prefix
          + "\" finishes and then " + c.injected + " runs as a separate command. It " + note(c.injected)
          + ". You never had to break ping — the shell did the splitting.";
        return;
      }
      // plain
      if (leadingDash) {
        setStatus("reached ping as an option", "warn");
        render([{ cls: "cmd", text: "ping -c 1 " + host } , { cls: "data", text: host + "  ← parsed by ping as an OPTION, not a host" }]);
        verdictEl.className = "verdict bad";
        verdictEl.textContent = "Argument injection — ping read it as a flag.";
        explainEl.textContent = "No shell metacharacter, so nothing chains; but the value starts with '-', "
          + "so ping treats it as an option (CWE-88) instead of a host. A different bug class from the ; | $() above.";
        return;
      }
      setStatus("ran: a plain ping", "safe");
      render([{ cls: "cmd", text: "ping -c 1 " + host }, { cls: "data", text: host + "  ← one host argument" }]);
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Just pings — but only because you didn't inject.";
      explainEl.textContent = "No shell metacharacter here, so the string is a single ping target. "
        + "Nothing validated it, though: add ; or $() and shell=True will run whatever follows.";
      return;
    }

    if (modeArgv.checked) {
      callEl.textContent = 'subprocess.run(["ping","-c","1",host], shell=False)';
      if (leadingDash) {
        setStatus("reached ping as an option", "warn");
        render([{ cls: "cmd", text: 'argv = ["ping","-c","1","' + host + '"]' },
                { cls: "data", text: host + "  ← one argument, but ping reads a leading '-' as an option" }]);
        verdictEl.className = "verdict bad";
        verdictEl.textContent = "Shell injection gone — argument injection is not.";
        explainEl.textContent = "No shell runs, so ; | $() can't chain a command. But argv still passes '" + host
          + "' straight to ping, and a leading '-' is an option (CWE-88). Dropping the shell is necessary, not sufficient.";
        return;
      }
      setStatus("one literal argument", "safe");
      render([{ cls: "cmd", text: 'argv = ["ping","-c","1","' + host + '"]' },
              { cls: "data", text: host + "  ← the WHOLE value is one argument; no shell to re-parse it" }]);
      var hostile = c.kind !== "plain";
      verdictEl.className = "verdict ok";
      verdictEl.textContent = hostile ? "Inert — the shell never sees it." : "Pings normally.";
      explainEl.textContent = hostile
        ? "Because there is no shell, ; | & $() are just characters in the hostname. ping tries to resolve the "
          + "literal host \"" + host + "\", fails (unknown host), and nothing else runs. This is the real fix: "
          + "the argv list fixes the boundary between command and data."
        : "A normal hostname resolves and pings. The argv form has no shell for metacharacters to escape into.";
      return;
    }

    // allow-list + argv (solution_app.py)
    callEl.textContent = 'if not re.fullmatch(r"[A-Za-z0-9_.-]+", host): return 400\n'
      + 'subprocess.run(["ping","-c","1",host], shell=False)';
    var passes = /^[A-Za-z0-9_.-]+$/.test(host);
    if (!passes) {
      setStatus("rejected — 400 invalid host", "safe");
      render([{ cls: "data", text: host },
              { cls: "inj", text: "✗ contains a character outside [A-Za-z0-9_.-] → 400 before argv is built" }]);
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Blocked at the allow-list — never reaches ping.";
      explainEl.textContent = "re.fullmatch rejects the space and ; | $ ( ) in this value, so the request is "
        + "refused with 400 before any command is built. The allow-list stops the obvious payloads early.";
      return;
    }
    if (leadingDash) {
      setStatus("passes the allow-list → option", "warn");
      render([{ cls: "data", text: host + "  ✓ every character is in [A-Za-z0-9_.-]" },
              { cls: "inj", text: 'argv = ["ping","-c","1","' + host + '"]  → ping reads it as an OPTION' }]);
      verdictEl.className = "verdict bad";
      verdictEl.textContent = "The allow-list is not airtight — '-' slips through.";
      explainEl.textContent = "[A-Za-z0-9_.-]+ accepts a leading '-', so \"" + host + "\" passes the regex AND argv, "
        + "and ping takes it as an option (CWE-88 argument injection). The real fix is to put '--' before the host, "
        + "or reject a leading '-'. Don't sell the allow-list as belt-and-braces against this.";
      return;
    }
    setStatus("accepted → pings", "safe");
    render([{ cls: "data", text: host + "  ✓ passes [A-Za-z0-9_.-]+" },
            { cls: "cmd", text: 'argv = ["ping","-c","1","' + host + '"]' }]);
    verdictEl.className = "verdict ok";
    verdictEl.textContent = "Allowed — a plain host, no shell, no option.";
    explainEl.textContent = "Both layers agree: the value is a normal hostname, so it passes the allow-list and "
      + "is handed to ping as one literal argument with no shell in the path.";
  }

  PRESETS.forEach(function (p) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = p;
    b.addEventListener("click", function () { hostEl.value = p; update(); });
    presetsEl.appendChild(b);
  });

  hostEl.addEventListener("input", update);
  modeVuln.addEventListener("change", update);
  modeArgv.addEventListener("change", update);
  modeAllow.addEventListener("change", update);
  update();
})();
