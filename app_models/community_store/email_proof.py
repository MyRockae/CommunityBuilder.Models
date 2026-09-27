"""Signed guest email proof for Payment checkout after 6-digit verify."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from typing import Optional, Tuple

from django.conf import settings


def _key() -> bytes:
    raw = (
        getattr(settings, 'CONFERENCE_TOKEN_ENCRYPTION_KEY', None)
        or getattr(settings, 'SECRET_KEY', '')
        or ''
    ).encode('utf-8')
    return hashlib.sha256(raw).digest()


def issue_email_proof(*, email: str, buyer_name: str, ttl_seconds: int = 1800) -> str:
    payload = {
        'email': (email or '').strip().lower(),
        'name': (buyer_name or '').strip(),
        'exp': int(time.time()) + int(ttl_seconds),
    }
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8')).decode('ascii')
    sig = hmac.new(_key(), body.encode('ascii'), hashlib.sha256).hexdigest()
    return f'{body}.{sig}'


def verify_email_proof(token: Optional[str]) -> Tuple[bool, str, str]:
    """Return (ok, email, name)."""
    raw = (token or '').strip()
    if '.' not in raw:
        return False, '', ''
    body, sig = raw.rsplit('.', 1)
    expected = hmac.new(_key(), body.encode('ascii'), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return False, '', ''
    try:
        payload = json.loads(base64.urlsafe_b64decode(body.encode('ascii')))
    except (ValueError, json.JSONDecodeError):
        return False, '', ''
    if int(payload.get('exp') or 0) < int(time.time()):
        return False, '', ''
    email = (payload.get('email') or '').strip().lower()
    name = (payload.get('name') or '').strip()
    if not email:
        return False, '', ''
    return True, email, name
