/* cosign-verify.js — Week 12 simulation.
 *
 * WHAT THIS IS FOR
 * The deploy gate on the sigstore-keyless slide is abstract until a student
 * picks an image, runs `cosign verify`, and watches it either let the deploy
 * through or block it. This re-implements the VERIFY side of keyless signing:
 *
 *   - unsigned image            -> "no signatures found"            -> BLOCKED
 *   - signed, then tampered     -> signature != current digest      -> BLOCKED
 *   - signed by OUR CI identity -> identity matches the policy       -> deploy
 *   - signed by ANOTHER identity (a valid Fulcio cert, logged in Rekor, just
 *     not ours):
 *        policy pins our identity (--certificate-identity-regexp ciX) -> BLOCKED
 *        policy left wide open  (--certificate-identity-regexp '.*')   -> deploy  <-- the trap
 *
 * The one idea: keyless verify anchors trust to an IDENTITY, not a key. A valid
 * signature is not enough; it has to be a signature by the signer you expected.
 * The lab's demo command uses `.*` so verify runs at all; this sim shows why
 * `.*` in production would wave an attacker's own signed image straight through.
 *
 * Nothing is sent anywhere; cosign's verify logic is computed in the page.
 */
(function () {
  "use strict";

  // The identity our deploy policy expects to have signed a releasable image.
  var OURS = "https://github.com/acme/ci/.github/workflows/release.yml@refs/heads/main";
  var ATTACKER = "https://github.com/evil-fork/pwn/.github/workflows/build.yml@refs/heads/main";

  var IMAGES = {
    "signed-ci":      { label: "signed by our CI",          signed: true,  identity: OURS,     digestMatches: true  },
    "unsigned":       { label: "never signed",              signed: false, identity: null,     digestMatches: false },
    "tampered":       { label: "signed, then re-pushed",    signed: true,  identity: OURS,     digestMatches: false },
    "wrong-identity": { label: "signed by someone else",    signed: true,  identity: ATTACKER, digestMatches: true  }
  };

  var PRESETS = [
    { label: "our signed image → deploys", image: "signed-ci", pin: true },
    { label: "unsigned → blocked",          image: "unsigned", pin: true },
    { label: "tampered after signing → blocked", image: "tampered", pin: true },
    { label: "attacker's image, policy pinned → blocked", image: "wrong-identity", pin: true },
    { label: "attacker's image, policy '.*' → the dangerous pass", image: "wrong-identity", pin: false }
  ];

  var imageEl = document.getElementById("image");
  var pinEl = document.getElementById("pin");
  var presetsEl = document.getElementById("presets");
  var cmdEl = document.getElementById("cmd");
  var statusEl = document.getElementById("status");
  var bodyEl = document.getElementById("bodyout");
  var verdictEl = document.getElementById("verdict");
  var explainEl = document.getElementById("explain");

  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = "cosign-status cosign-" + kind; // ok | blocked
  }

  function shortId(id) {
    // Show the human-readable tail of the OIDC identity, not the whole URL.
    if (!id) return "(none)";
    var m = id.match(/github\.com\/([^/]+\/[^/]+)/);
    return m ? m[1] : id;
  }

  function update() {
    var img = IMAGES[imageEl.value];
    var pinned = pinEl.checked;

    var idFlag = pinned
      ? "--certificate-identity-regexp 'acme/ci'"
      : "--certificate-identity-regexp '.*'";
    cmdEl.textContent = "cosign verify " + idFlag
      + " --certificate-oidc-issuer-regexp 'https://token.actions.githubusercontent.com' \\\n"
      + "  registry.acme.io/web:latest";

    bodyEl.textContent = "";

    // 1. No signature at all -> nothing for the gate to check.
    if (!img.signed) {
      setStatus("BLOCKED — deploy refused", "blocked");
      bodyEl.textContent = "Error: no signatures found for the image";
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Gate did its job — an unsigned artifact never ships.";
      explainEl.textContent = "cosign found no signature in the registry or Rekor, so there is "
        + "nothing to trust. The deploy admission step fails closed. This is the common case the "
        + "gate exists for: someone built and pushed without the signing step.";
      return;
    }

    // 2. Signed, but the image was changed after signing -> digest no longer matches.
    if (!img.digestMatches) {
      setStatus("BLOCKED — deploy refused", "blocked");
      bodyEl.textContent = "Error: signature does not match the image digest\n"
        + "(the signature covers sha256:a1b2… but the image is now sha256:9f3c…)";
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Tamper caught — the signature is bound to the exact bytes.";
      explainEl.textContent = "The signature was made over the original image digest. Re-pushing a "
        + "modified layer changes the digest, so the old signature no longer matches. You cannot edit "
        + "a signed image and keep its signature valid — that is the integrity guarantee (A08).";
      return;
    }

    // 3. Valid signature. Does the SIGNER match what our policy expects?
    var identityOk = pinned ? /acme\/ci/.test(img.identity) : true;

    if (!identityOk) {
      setStatus("BLOCKED — deploy refused", "blocked");
      bodyEl.textContent = "Error: certificate identity \"" + shortId(img.identity) + "\"\n"
        + "does not match the expected identity \"acme/ci\"";
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Valid signature, wrong signer — still blocked.";
      explainEl.textContent = "The image is genuinely signed and logged in Rekor, but by "
        + shortId(img.identity) + ", not our CI. Keyless verify anchors trust to the OIDC identity, "
        + "so pinning --certificate-identity-regexp to our own workflow is what rejects a valid "
        + "signature from the wrong account.";
      return;
    }

    // Verified. If this is the attacker's image passing, say so loudly.
    setStatus("deploy ✓ — verified", "ok");
    bodyEl.textContent = "Verified OK — 1 signature, logged in Rekor\n"
      + "certificate identity: " + shortId(img.identity) + "\n"
      + "issuer: token.actions.githubusercontent.com";

    if (/evil-fork/.test(img.identity)) {
      verdictEl.className = "verdict bad";
      verdictEl.textContent = "Deployed the attacker's image — because the policy trusted '.*'.";
      explainEl.textContent = "The signature is valid and Rekor-logged, so with "
        + "--certificate-identity-regexp '.*' cosign is happy with ANY signer, including "
        + shortId(img.identity) + ". A valid signature is not the same as a signature you should "
        + "trust. The lab command uses '.*' only so verify runs; in production you pin it to your CI.";
    } else {
      verdictEl.className = "verdict ok";
      verdictEl.textContent = "Deploys — signed by our CI, unchanged since signing.";
      explainEl.textContent = "A signature that is present, matches the current digest, and comes from "
        + "the expected identity. All three must hold. There is no long-lived private key anywhere in "
        + "this — trust is the OIDC identity plus the Rekor record (so no key to leak, CWE-321).";
    }
  }

  PRESETS.forEach(function (p) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = p.label;
    b.addEventListener("click", function () {
      imageEl.value = p.image;
      pinEl.checked = p.pin;
      update();
    });
    presetsEl.appendChild(b);
  });

  imageEl.addEventListener("change", update);
  pinEl.addEventListener("change", update);
  update();
})();
