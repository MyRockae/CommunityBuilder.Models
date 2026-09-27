"""Encrypt OAuth tokens and hash guest OTP codes. Same key must be set on Main API and Payment."""
from __future__ import annotations

import hashlib
import hmac
import os
from typing import Optional

from django.conf import settings


def _raw_key() -> bytes:
    raw = (
        getattr(settings, 'CONFERENCE_TOKEN_ENCRYPTION_KEY', None)
        or os.environ.get('CONFERENCE_TOKEN_ENCRYPTION_KEY')
        or ''
    ).strip()
    if not raw:
        raw = (getattr(settings, 'SECRET_KEY', None) or '')[:64]
    if not raw:
        raise RuntimeError('CONFERENCE_TOKEN_ENCRYPTION_KEY is not configured.')
    return hashlib.sha256(raw.encode('utf-8')).digest()


def _xor_keystream(key: bytes, iv: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hashlib.sha256(key + iv + counter.to_bytes(4, 'big')).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def encrypt_secret(plaintext: Optional[str]) -> str:
    if not plaintext:
        return ''
    key = _raw_key()
    data = plaintext.encode('utf-8')
    iv = os.urandom(16)
    cipher = bytes(a ^ b for a, b in zip(data, _xor_keystream(key, iv, len(data))))
    mac = hmac.new(key, iv + cipher, hashlib.sha256).digest()
    return (iv + mac + cipher).hex()


def decrypt_secret(ciphertext: Optional[str]) -> str:
    if not ciphertext:
        return ''
    key = _raw_key()
    raw = bytes.fromhex(ciphertext.strip())
    if len(raw) < 48:
        raise ValueError('Invalid encrypted secret.')
    iv, mac, cipher = raw[:16], raw[16:48], raw[48:]
    expected = hmac.new(key, iv + cipher, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError('Invalid encrypted secret.')
    data = bytes(a ^ b for a, b in zip(cipher, _xor_keystream(key, iv, len(cipher))))
    return data.decode('utf-8')


def hash_otp_code(code: str) -> str:
    key = _raw_key()
    return hmac.new(key, (code or '').strip().encode('utf-8'), hashlib.sha256).hexdigest()


def otp_codes_match(code: str, code_hash: str) -> bool:
    return hmac.compare_digest(hash_otp_code(code), (code_hash or '').strip())
