"""ICS REQUEST / CANCEL for a store slot session (one attendee per email)."""
from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Optional

from django.utils import timezone


def _ics_escape(text: str) -> str:
    return (
        (text or '')
        .replace('\\', '\\\\')
        .replace(';', '\\;')
        .replace(',', '\\,')
        .replace('\r\n', '\\n')
        .replace('\n', '\\n')
    )


def _fold_ics_line(line: str) -> str:
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    rest = line[75:]
    while rest:
        parts.append(' ' + rest[:74])
        rest = rest[74:]
    return '\r\n'.join(parts)


def _ics_dt_utc(dt) -> str:
    if dt is None:
        dt = timezone.now()
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, dt_timezone.utc)
    return dt.astimezone(dt_timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def build_slot_invite_ics(
    *,
    uid: str,
    summary: str,
    start,
    end,
    join_url: str = '',
    description: str = '',
    organizer_email: str = '',
    organizer_name: str = '',
    attendee_email: str = '',
    attendee_name: str = '',
    sequence: int = 0,
    method: str = 'REQUEST',
    cancelled: bool = False,
) -> str:
    status = 'CANCELLED' if cancelled or method == 'CANCEL' else 'CONFIRMED'
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Rockae//Store Meeting//EN',
        'CALSCALE:GREGORIAN',
        f'METHOD:{method}',
        'BEGIN:VEVENT',
        f'UID:{uid}',
        f'DTSTAMP:{_ics_dt_utc(timezone.now())}',
        f'DTSTART:{_ics_dt_utc(start)}',
        f'DTEND:{_ics_dt_utc(end)}',
        _fold_ics_line(f'SUMMARY:{_ics_escape(summary)}'),
        f'SEQUENCE:{int(sequence)}',
        f'STATUS:{status}',
        'TRANSP:OPAQUE' if not cancelled else 'TRANSP:TRANSPARENT',
    ]
    loc = (join_url or '').strip()
    if loc:
        lines.append(_fold_ics_line(f'LOCATION:{_ics_escape(loc)}'))
    desc = (description or '').strip()
    if loc and loc not in desc:
        desc = f'{desc}\nJoin: {loc}'.strip() if desc else f'Join: {loc}'
    if desc:
        lines.append(_fold_ics_line(f'DESCRIPTION:{_ics_escape(desc)}'))
    if organizer_email:
        cn = _ics_escape(organizer_name or organizer_email)
        lines.append(_fold_ics_line(f'ORGANIZER;CN={cn}:mailto:{organizer_email.strip()}'))
    if attendee_email:
        cn = _ics_escape(attendee_name or attendee_email)
        lines.append(
            _fold_ics_line(
                f'ATTENDEE;CN={cn};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{attendee_email.strip()}'
            )
        )
    lines.extend(['END:VEVENT', 'END:VCALENDAR'])
    return '\r\n'.join(lines) + '\r\n'
