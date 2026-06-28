# Week 3 — Cryptography Used Correctly (and Misused)

**OWASP 2025:** A04 Cryptographic Failures · **CWE:** CWE-327, CWE-916, CWE-330

## Objectives
- Distinguish hashing vs encryption vs encoding.
- Store passwords with a vetted KDF (bcrypt/argon2).
- Recognize crypto misuse: ECB, hardcoded keys, weak RNG, MD5/SHA-1.

## 🔓 Signature game — "Capture the Hash"
1. **Crack weak hashes:** given unsalted MD5 hashes, recover passwords (e.g. `hashcat`/`john` with a wordlist).
2. **ECB oracle:** observe identical plaintext blocks → identical ciphertext; exploit to leak structure.
3. **Remediate:** rewrite the sample service to use argon2id for passwords and AES-GCM (authenticated) for data, with keys from a secrets manager / env (never hardcoded).

## Deliverable
Before/after code + a short note on which CWE each change closes.

## References
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
