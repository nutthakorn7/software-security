"""
Week 3 Task 7 — AES-GCM authenticated encryption round-trip.

encrypt_gcm / decrypt_gcm use a random 12-byte nonce and a key taken from the
ENC_KEY_HEX environment variable (never hardcoded). The GCM auth tag means any
tampering with the ciphertext is detected on decrypt and the operation fails,
rather than silently returning corrupted plaintext.
"""
import os
from Crypto.Cipher import AES


def encrypt_gcm(data: bytes, key: bytes):
    nonce = os.urandom(12)                      # fresh random nonce per message
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(data)   # ciphertext + authentication tag
    return nonce, ct, tag


def decrypt_gcm(nonce: bytes, ct: bytes, tag: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    # decrypt_and_verify raises ValueError if the tag does not match the ciphertext.
    return cipher.decrypt_and_verify(ct, tag)


if __name__ == "__main__":
    # Key from the environment; fall back to a random one for the demo (never hardcode).
    key = bytes.fromhex(os.environ.get("ENC_KEY_HEX", os.urandom(32).hex()))
    msg = b"prod db password is hunter2"

    nonce, ct, tag = encrypt_gcm(msg, key)
    print("plaintext :", msg)
    print("nonce     :", nonce.hex())
    print("ciphertext:", ct.hex())
    print("tag       :", tag.hex())

    # 1. Honest round-trip — decrypts back to the original.
    recovered = decrypt_gcm(nonce, ct, tag, key)
    print("round-trip decrypt:", recovered, "| matches:", recovered == msg)

    # 2. Tamper: flip one bit in the first ciphertext byte, then try to decrypt.
    tampered = bytearray(ct)
    tampered[0] ^= 0x01
    try:
        decrypt_gcm(nonce, bytes(tampered), tag, key)
        print("tampered decrypt : SUCCEEDED  <-- BAD, integrity not enforced")
    except ValueError:
        print("tampered decrypt : ValueError (tag check failed) <-- tampering detected")