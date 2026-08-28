"""
Week 3 — Cryptography Used Correctly

Fixes:
- Password storage: Argon2id
- Legacy MD5 migration: rehash-on-login
- Encryption: AES-GCM
- Encryption key: environment variable
- Reset token: secrets CSPRNG

pip install argon2-cffi pycryptodome
"""

import os
import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.low_level import Type
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from Crypto.Cipher import AES


# Argon2id password hasher
ph = PasswordHasher(type=Type.ID)


def store_password(pw: str) -> str:
    """Store a new password using Argon2id."""
    return ph.hash(pw)


def verify_password(hash_: str, pw: str) -> bool:
    """Verify an Argon2id password."""
    try:
        return ph.verify(hash_, pw)
    except (VerifyMismatchError, InvalidHashError):
        return False


def verify_and_upgrade(hash_: str, pw: str):
    """
    Verify password and upgrade legacy MD5 to Argon2id.

    Returns:
        (True, new_hash)  -> login succeeds and hash should be replaced
        (True, None)      -> login succeeds, no upgrade needed
        (False, None)     -> wrong password
    """

    # Existing Argon2 hash
    if hash_.startswith("$argon2"):
        try:
            ph.verify(hash_, pw)

            if ph.check_needs_rehash(hash_):
                return True, ph.hash(pw)

            return True, None

        except (VerifyMismatchError, InvalidHashError):
            return False, None

    # Legacy MD5 hash
    md5_candidate = hashlib.md5(
        pw.encode("utf-8")
    ).hexdigest()

    if hmac.compare_digest(md5_candidate, hash_):
        new_hash = ph.hash(pw)
        return True, new_hash

    return False, None


def encrypt_gcm(
    data: bytes,
    key: bytes
) -> tuple[bytes, bytes, bytes]:
    """Encrypt data using AES-GCM."""

    if len(key) not in (16, 24, 32):
        raise ValueError(
            "AES key must be 16, 24, or 32 bytes"
        )

    nonce = os.urandom(12)

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    ciphertext, tag = cipher.encrypt_and_digest(data)

    return nonce, ciphertext, tag


def decrypt_gcm(
    nonce: bytes,
    ciphertext: bytes,
    tag: bytes,
    key: bytes
) -> bytes:
    """Decrypt AES-GCM ciphertext and verify authentication tag."""

    if len(key) not in (16, 24, 32):
        raise ValueError(
            "AES key must be 16, 24, or 32 bytes"
        )

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    return cipher.decrypt_and_verify(
        ciphertext,
        tag
    )


def reset_token() -> str:
    """Generate a cryptographically secure reset token."""
    return secrets.token_urlsafe(16)


def load_encryption_key() -> bytes:
    """Load AES key from ENC_KEY_HEX environment variable."""

    key_hex = os.environ.get("ENC_KEY_HEX")

    if not key_hex:
        raise RuntimeError(
            "ENC_KEY_HEX environment variable is required"
        )

    try:
        key = bytes.fromhex(key_hex)
    except ValueError as exc:
        raise RuntimeError(
            "ENC_KEY_HEX must contain valid hexadecimal"
        ) from exc

    if len(key) not in (16, 24, 32):
        raise RuntimeError(
            "ENC_KEY_HEX must represent a 16, 24, or 32-byte AES key"
        )

    return key


if __name__ == "__main__":

    print("=== Week 3 Secure Crypto Demo ===")
    print()

    # --------------------------------------------------
    # Password Storage
    # --------------------------------------------------

    password = "password123"

    password_hash = store_password(password)

    print("[Password Storage]")
    print("Hash:", password_hash)
    print(
        "Argon2 verify:",
        verify_password(password_hash, password)
    )
    print()

    # --------------------------------------------------
    # Legacy MD5 Migration
    # --------------------------------------------------

    legacy_password = "admin123"

    legacy_md5 = hashlib.md5(
        legacy_password.encode("utf-8")
    ).hexdigest()

    ok, upgraded_hash = verify_and_upgrade(
        legacy_md5,
        legacy_password
    )

    print("[MD5 Migration]")
    print("Legacy MD5:", legacy_md5)
    print("Legacy login OK:", ok)

    if upgraded_hash:
        print("New hash:", upgraded_hash)
        print(
            "Is Argon2id:",
            upgraded_hash.startswith("$argon2id$")
        )
        print(
            "New hash verifies:",
            verify_password(
                upgraded_hash,
                legacy_password
            )
        )

    print()

    # --------------------------------------------------
    # AES-GCM
    # --------------------------------------------------

    key = load_encryption_key()

    message = b"Week 3 secret message"

    nonce, ciphertext, tag = encrypt_gcm(
        message,
        key
    )

    plaintext = decrypt_gcm(
        nonce,
        ciphertext,
        tag,
        key
    )

    print("[AES-GCM]")
    print("Nonce length:", len(nonce))
    print("Nonce:", nonce.hex())
    print("Ciphertext:", ciphertext.hex())
    print("Tag:", tag.hex())
    print("Decrypted:", plaintext)
    print(
        "Round-trip OK:",
        plaintext == message
    )

    print()

    # --------------------------------------------------
    # Tampering Test
    # --------------------------------------------------

    tampered = bytearray(ciphertext)

    if tampered:
        tampered[0] ^= 1

    print("[Tampering Test]")

    try:
        decrypt_gcm(
            nonce,
            bytes(tampered),
            tag,
            key
        )

        print("Tampered ciphertext accepted: ERROR")

    except ValueError:
        print("Tampered ciphertext rejected: True")
        print(
            "Authentication tag check failed as expected"
        )

    print()

    # --------------------------------------------------
    # Secure Reset Token
    # --------------------------------------------------

    print("[Secure Reset Token]")
    print("Token:", reset_token())