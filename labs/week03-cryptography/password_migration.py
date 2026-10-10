"""
Week 3 Task 6 — password storage migration.

store_password / verify_password use argon2id (per-password salt, tunable cost).
login_and_migrate() is the rehash-on-login path: a user whose password is still
stored as legacy unsalted MD5 is transparently upgraded to argon2id on their next
successful login, so the weak hashes drain out of the database over time without a
mass reset or ever seeing anyone's plaintext at rest.
"""
import hashlib
import re
from argon2 import PasswordHasher

ph = PasswordHasher()

# A legacy record is a 32-char hex MD5 digest; an argon2id record starts with "$argon2id$".
_MD5_RE = re.compile(r"^[0-9a-f]{32}$")


def store_password(pw: str) -> str:
    """Hash a new password with argon2id (salt is generated and embedded automatically)."""
    return ph.hash(pw)


def verify_password(stored: str, pw: str) -> bool:
    """Verify a password against an argon2id record."""
    try:
        return ph.verify(stored, pw)
    except Exception:
        return False


def _is_legacy_md5(stored: str) -> bool:
    return bool(_MD5_RE.match(stored))


def login_and_migrate(stored: str, pw: str):
    """
    Attempt a login and, on success, return an upgraded hash if the stored record
    needs migrating.

    Returns (ok, new_hash):
      ok        — True if the password is correct.
      new_hash  — a fresh argon2id hash the caller should WRITE BACK to the DB,
                  or None if the stored record is already current.
    """
    # Case 1 — legacy unsalted MD5 record.
    if _is_legacy_md5(stored):
        if hashlib.md5(pw.encode()).hexdigest() == stored:
            # Correct password, weak storage: upgrade it now.
            return True, store_password(pw)
        return False, None

    # Case 2 — already argon2id.
    if verify_password(stored, pw):
        # Even a current hash may need re-hashing if the cost parameters have been
        # raised since it was created; argon2-cffi tells us.
        if ph.check_needs_rehash(stored):
            return True, store_password(pw)
        return True, None

    return False, None


if __name__ == "__main__":
    # Demo: NoteVault's real legacy record for alice (unsalted MD5 of "alicepw").
    legacy = hashlib.md5(b"alicepw").hexdigest()
    print("stored (legacy):", legacy)
    print("  is legacy MD5:", _is_legacy_md5(legacy))

    # Wrong password — login fails, no migration.
    ok, new = login_and_migrate(legacy, "wrongpw")
    print("login wrongpw   -> ok:", ok, "| migrated:", new is not None)

    # Correct password — login succeeds AND the record is upgraded to argon2id.
    ok, new = login_and_migrate(legacy, "alicepw")
    print("login alicepw   -> ok:", ok, "| migrated:", new is not None)
    print("upgraded record:", new[:40], "...")

    # Next login now verifies against argon2id, and needs no further migration.
    ok, again = login_and_migrate(new, "alicepw")
    print("re-login        -> ok:", ok, "| needs migrate again:", again is not None)