---
marp: true
theme: default
paginate: true
header: "Software Security · Week 3"
---

# Week 3
## Cryptography Used Correctly (and Misused)
Software Security · Nutthakorn Chalaemwongwan

---

## Today

- Hashing vs encryption vs encoding
- Password storage done right
- Symmetric / asymmetric basics
- Common crypto failures (A04:2025)
- 🎮 Game: **Capture the Hash**

---

## Recap — Week 2

- Tools find bugs; today we study a bug *class*
- Crypto misuse is subtle — code "works" but isn't safe

---

## Three things people confuse

- **Hashing** — one-way, fixed-size digest (integrity, passwords)
- **Encryption** — reversible *with a key* (confidentiality)
- **Encoding** — reversible *without a key* (Base64 ≠ security!)

---

## Symmetric vs asymmetric

- **Symmetric** (AES, ChaCha20) — one shared key, fast
- **Asymmetric** (RSA, ECC) — public/private key pair
- TLS uses asymmetric to exchange a symmetric session key

---

## Password storage

- Never store plaintext or plain hashes
- Use a **slow, salted KDF**: argon2id (preferred), bcrypt, scrypt
- Salt is per-user and random

```python
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash("correct horse battery staple")
```

---

## Common crypto failures (A04:2025)

- **ECB mode** → identical plaintext blocks leak patterns
- Hardcoded keys / keys in source
- Weak RNG (`random` instead of `secrets`/CSPRNG)
- **MD5 / SHA-1** for security
- Unauthenticated encryption (no integrity)

---

## Why ECB is broken (the penguin)

- ECB encrypts each block independently
- Same plaintext block → same ciphertext block
- Structure/patterns survive encryption → leakage

---

## Do this instead

- Authenticated encryption: **AES-GCM** or **ChaCha20-Poly1305**
- Keys from a secrets manager / KMS — never in code
- CSPRNG: `secrets` (Python), `crypto.randomBytes` (Node)
- SHA-256+ for integrity; argon2id/bcrypt for passwords

---

## CWE mapping

- **CWE-327** — broken/risky crypto algorithm
- **CWE-916** — weak password hash (no/weak KDF)
- **CWE-330** — insufficiently random values
- **CWE-321** — hardcoded key

---

## 🔓 Game — Capture the Hash

- **Round 1 (speedrun):** crack unsalted/MD5 hashes (`hashcat`/`john` + wordlist); fastest team wins
- **Round 2:** exploit an **ECB oracle** (identical blocks)
- **Round 3 (defend):** argon2id + AES-GCM + keys from env

---

## Lab 3 — deliverable

1. Cracked hashes + method
2. ECB oracle exploitation notes
3. **Before/after** code + which CWE each fix closes

---

## Key takeaways

- Encoding is not encryption; hashing is not reversible
- Use vetted KDFs + authenticated encryption — never roll your own
- Randomness and key handling matter as much as the algorithm

---

# Questions?
Next week: Injection & input handling
