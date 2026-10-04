"""Create / reuse Google Meet and Zoom rooms for a StoreSlotSession."""
from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import Optional
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from app_models.community_store.conference_crypto import decrypt_secret, encrypt_secret
from app_models.community_store.models import (
    CommunityConferenceConnection,
    ConferenceConnectionStatus,
    ConferenceProvider,
    ConferenceRoomSource,
    SlotConferenceStatus,
    StorePurchase,
    StoreSlotSession,
)

logger = logging.getLogger(__name__)


def meeting_join_grace():
    return timedelta(minutes=60)


def session_is_live(session: StoreSlotSession, *, now=None) -> bool:
    now = now or timezone.now()
    if session.cancelled_at:
        return False
    return now < (session.slot_end_utc + meeting_join_grace())


def occupying_purchases_qs(product_id, slot_start_utc, *, now=None):
    from django.db.models import Q

    now = now or timezone.now()
    return StorePurchase.objects.filter(
        product_id=product_id,
        booked_slot_start_utc=slot_start_utc,
    ).filter(
        Q(status=StorePurchase.STATUS_COMPLETED)
        | (
            Q(status=StorePurchase.STATUS_PENDING)
            & (Q(checkout_expires_at__isnull=True) | Q(checkout_expires_at__gt=now))
        )
    )


def expire_stale_pending_purchases(product_id=None, *, now=None) -> int:
    now = now or timezone.now()
    qs = StorePurchase.objects.filter(
        status=StorePurchase.STATUS_PENDING,
        checkout_expires_at__isnull=False,
        checkout_expires_at__lte=now,
    )
    if product_id is not None:
        qs = qs.filter(product_id=product_id)
    return qs.update(status=StorePurchase.STATUS_FAILED)


def seat_count_for_slot(product_id, slot_start_utc, *, now=None) -> int:
    expire_stale_pending_purchases(product_id, now=now)
    return occupying_purchases_qs(product_id, slot_start_utc, now=now).count()


def occupancy_counts_for_starts(product_id, slot_starts_utc, *, now=None) -> dict:
    """One grouped COUNT per start instead of a query per slot."""
    from datetime import timezone as dt_timezone

    from django.db.models import Count, Q

    now = now or timezone.now()
    starts = []
    for raw in slot_starts_utc or ():
        if raw is None:
            continue
        dt = raw
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, dt_timezone.utc)
        starts.append(dt.astimezone(dt_timezone.utc).replace(microsecond=0))
    if not starts:
        return {}
    expire_stale_pending_purchases(product_id, now=now)
    rows = (
        StorePurchase.objects.filter(
            product_id=product_id,
            booked_slot_start_utc__in=starts,
        )
        .filter(
            Q(status=StorePurchase.STATUS_COMPLETED)
            | (
                Q(status=StorePurchase.STATUS_PENDING)
                & (Q(checkout_expires_at__isnull=True) | Q(checkout_expires_at__gt=now))
            )
        )
        .values('booked_slot_start_utc')
        .annotate(n=Count('id'))
    )
    out = {}
    for row in rows:
        key = row['booked_slot_start_utc']
        if key is None:
            continue
        if timezone.is_naive(key):
            key = timezone.make_aware(key, dt_timezone.utc)
        key = key.astimezone(dt_timezone.utc).replace(microsecond=0)
        out[key] = int(row['n'] or 0)
    return out


def slot_is_full(settings, product_id, slot_start_utc, *, now=None) -> bool:
    max_att = int(getattr(settings, 'max_attendees', 1) or 0)
    if max_att == 0:
        return False
    return seat_count_for_slot(product_id, slot_start_utc, now=now) >= max_att


def get_or_create_slot_session(product, slot_start_utc, slot_end_utc, *, settings):
    source = (getattr(settings, 'room_source', None) or '') or ''
    provider = source if source in (ConferenceProvider.GOOGLE_MEET, ConferenceProvider.ZOOM) else ''
    max_att = int(getattr(settings, 'max_attendees', 1) or 1)
    session, created = StoreSlotSession.objects.get_or_create(
        store_product=product,
        slot_start_utc=slot_start_utc,
        defaults={
            'slot_end_utc': slot_end_utc,
            'conference_provider': provider,
            'max_attendees_snapshot': max_att,
            'conference_status': SlotConferenceStatus.NONE,
        },
    )
    if created and not session.ics_uid:
        session.ics_uid = f'store-slot-{session.id}@rockae.com'
        session.save(update_fields=['ics_uid', 'updated_at'])
    return session


def active_connection(community, provider: str) -> Optional[CommunityConferenceConnection]:
    if not community or not provider:
        return None
    return CommunityConferenceConnection.objects.filter(
        community=community,
        provider=provider,
        status=ConferenceConnectionStatus.ACTIVE,
    ).first()


def _google_token_url():
    return 'https://oauth2.googleapis.com/token'


def _zoom_token_url():
    return 'https://zoom.us/oauth/token'


def refresh_connection_access_token(conn: CommunityConferenceConnection) -> str:
    refresh = decrypt_secret(conn.refresh_token_encrypted)
    if not refresh:
        raise RuntimeError('Conference connection has no refresh token.')
    if conn.provider == ConferenceProvider.GOOGLE_MEET:
        data = {
            'client_id': getattr(settings, 'GOOGLE_CALENDAR_CLIENT_ID', None)
            or getattr(settings, 'GOOGLE_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'GOOGLE_CALENDAR_CLIENT_SECRET', None)
            or getattr(settings, 'GOOGLE_CLIENT_SECRET', ''),
            'refresh_token': refresh,
            'grant_type': 'refresh_token',
        }
        resp = requests.post(_google_token_url(), data=data, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
        access = payload.get('access_token') or ''
        expires_in = int(payload.get('expires_in') or 3600)
        conn.access_token_encrypted = encrypt_secret(access)
        conn.access_token_expires_at = timezone.now() + timedelta(seconds=max(60, expires_in - 60))
        conn.save(update_fields=['access_token_encrypted', 'access_token_expires_at', 'updated_at'])
        return access
    if conn.provider == ConferenceProvider.ZOOM:
        cid = getattr(settings, 'ZOOM_CLIENT_ID', '') or ''
        secret = getattr(settings, 'ZOOM_CLIENT_SECRET', '') or ''
        resp = requests.post(
            _zoom_token_url(),
            params={'grant_type': 'refresh_token', 'refresh_token': refresh},
            auth=(cid, secret),
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        access = payload.get('access_token') or ''
        new_refresh = payload.get('refresh_token') or refresh
        expires_in = int(payload.get('expires_in') or 3600)
        conn.access_token_encrypted = encrypt_secret(access)
        conn.refresh_token_encrypted = encrypt_secret(new_refresh)
        conn.access_token_expires_at = timezone.now() + timedelta(seconds=max(60, expires_in - 60))
        conn.save(
            update_fields=[
                'access_token_encrypted',
                'refresh_token_encrypted',
                'access_token_expires_at',
                'updated_at',
            ]
        )
        return access
    raise RuntimeError(f'Unsupported provider {conn.provider}')


def _access_token(conn: CommunityConferenceConnection) -> str:
    now = timezone.now()
    if (
        conn.access_token_encrypted
        and conn.access_token_expires_at
        and conn.access_token_expires_at > now + timedelta(seconds=30)
    ):
        try:
            return decrypt_secret(conn.access_token_encrypted)
        except Exception:
            pass
    return refresh_connection_access_token(conn)


def _iso_z(dt) -> str:
    return dt.isoformat().replace('+00:00', 'Z')


def provision_community_conference(
    community,
    provider: str,
    *,
    start,
    end,
    title: str,
    description: str = '',
    attendee_email: str = '',
):
    """Create a Meet or Zoom room on the community owner connection. No attendee list for groups."""
    conn = active_connection(community, provider)
    if not conn:
        raise RuntimeError('No active Google or Zoom connection for this community.')
    if provider == ConferenceProvider.GOOGLE_MEET:
        return _create_google_calendar_meet(
            conn,
            start=start,
            end=end,
            title=title,
            description=description,
            attendee_email=attendee_email,
        )
    if provider == ConferenceProvider.ZOOM:
        return _create_zoom_scheduled_meeting(conn, start=start, end=end, title=title)
    raise RuntimeError('Unsupported conference provider.')


CONNECTED_ROOM_SOURCES = (ConferenceRoomSource.GOOGLE_MEET, ConferenceRoomSource.ZOOM)


def normalize_room_source(value) -> str:
    source = (value or ConferenceRoomSource.MANUAL).strip() or ConferenceRoomSource.MANUAL
    if source not in (
        ConferenceRoomSource.MANUAL,
        ConferenceRoomSource.GOOGLE_MEET,
        ConferenceRoomSource.ZOOM,
    ):
        raise ValueError('Room source must be manual, google_meet, or zoom.')
    return source


def connected_provider_ids(community) -> set:
    if not community:
        return set()
    return set(
        CommunityConferenceConnection.objects.filter(
            community=community,
            status=ConferenceConnectionStatus.ACTIVE,
        ).values_list('provider', flat=True)
    )


def assert_room_source_allowed(community, room_source: str) -> str:
    source = normalize_room_source(room_source)
    if source in CONNECTED_ROOM_SOURCES and source not in connected_provider_ids(community):
        raise ValueError('Connect that Google or Zoom account first.')
    return source


def maybe_provision_community_room(
    community,
    room_source: str,
    *,
    start,
    end,
    title: str,
    description: str = '',
    existing_source: str = '',
    existing_url: str = '',
    existing_provider_id: str = '',
    remint: bool = False,
):
    """Mint a Meet/Zoom room, or reuse an existing vendor meeting, or return a pasted URL."""
    source = normalize_room_source(room_source)
    if source == ConferenceRoomSource.MANUAL:
        return {
            'join_url': (existing_url or '').strip(),
            'provider_meeting_id': '',
            'host_start_url': '',
        }
    if not start or not end:
        raise RuntimeError('Start and end times are required to create a meeting room.')
    if (
        not remint
        and source == (existing_source or '').strip()
        and (existing_url or '').strip()
        and (existing_provider_id or '').strip()
    ):
        return {
            'join_url': (existing_url or '').strip(),
            'provider_meeting_id': existing_provider_id,
            'host_start_url': '',
        }
    return provision_community_conference(
        community,
        source,
        start=start,
        end=end,
        title=title,
        description=description or '',
    )


def _create_google_calendar_meet(
    conn: CommunityConferenceConnection,
    *,
    start,
    end,
    title: str,
    description: str = '',
    attendee_email: str = '',
):
    token = _access_token(conn)
    request_id = uuid.uuid4().hex
    body = {
        'summary': title,
        'description': (description or '')[:8000],
        'start': {'dateTime': _iso_z(start), 'timeZone': 'UTC'},
        'end': {'dateTime': _iso_z(end), 'timeZone': 'UTC'},
        'conferenceData': {
            'createRequest': {
                'requestId': request_id,
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
    }
    params = {'conferenceDataVersion': 1, 'sendUpdates': 'none'}
    if attendee_email:
        body['attendees'] = [{'email': attendee_email}]
        params['sendUpdates'] = 'all'
    resp = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        params=params,
        json=body,
        headers={'Authorization': f'Bearer {token}'},
        timeout=25,
    )
    resp.raise_for_status()
    data = resp.json()
    hangout = (data.get('hangoutLink') or '').strip()
    entry = ''
    for ep in (data.get('conferenceData') or {}).get('entryPoints') or []:
        if ep.get('entryPointType') == 'video' and ep.get('uri'):
            entry = ep['uri']
            break
    return {
        'join_url': hangout or entry,
        'provider_meeting_id': str(data.get('id') or ''),
        'host_start_url': '',
    }


def _create_google_meet(session: StoreSlotSession, conn: CommunityConferenceConnection, *, attendee_email: str = ''):
    product = session.store_product
    exclusive = int(session.max_attendees_snapshot or 1) == 1
    return _create_google_calendar_meet(
        conn,
        start=session.slot_start_utc,
        end=session.slot_end_utc,
        title=product.name,
        description=(product.notes or product.description or ''),
        attendee_email=attendee_email if exclusive else '',
    )


def _add_google_attendee(session: StoreSlotSession, conn: CommunityConferenceConnection, email: str):
    if not session.provider_meeting_id or not email:
        return
    token = _access_token(conn)
    get = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{session.provider_meeting_id}',
        headers={'Authorization': f'Bearer {token}'},
        timeout=20,
    )
    get.raise_for_status()
    event = get.json()
    attendees = list(event.get('attendees') or [])
    existing = {(a.get('email') or '').lower() for a in attendees}
    if email.lower() in existing:
        return
    attendees.append({'email': email})
    requests.patch(
        f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{session.provider_meeting_id}',
        params={'sendUpdates': 'all', 'conferenceDataVersion': 1},
        json={'attendees': attendees},
        headers={'Authorization': f'Bearer {token}'},
        timeout=20,
    ).raise_for_status()


def _create_zoom_scheduled_meeting(conn: CommunityConferenceConnection, *, start, end, title: str):
    token = _access_token(conn)
    duration = max(1, int((end - start).total_seconds() // 60) or 30)
    body = {
        'topic': title,
        'type': 2,
        'start_time': start.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'duration': duration,
        'timezone': 'UTC',
        'settings': {
            'join_before_host': True,
            'waiting_room': False,
        },
    }
    resp = requests.post(
        'https://api.zoom.us/v2/users/me/meetings',
        json=body,
        headers={'Authorization': f'Bearer {token}'},
        timeout=25,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        'join_url': (data.get('join_url') or '').strip(),
        'host_start_url': (data.get('start_url') or '').strip(),
        'provider_meeting_id': str(data.get('id') or ''),
    }


def _create_zoom_meeting(session: StoreSlotSession, conn: CommunityConferenceConnection):
    return _create_zoom_scheduled_meeting(
        conn,
        start=session.slot_start_utc,
        end=session.slot_end_utc,
        title=session.store_product.name,
    )


def cancel_vendor_meeting(session: StoreSlotSession) -> None:
    product = session.store_product
    community = product.store.community
    provider = session.conference_provider or ''
    conn = active_connection(community, provider)
    if not conn or not session.provider_meeting_id:
        return
    try:
        token = _access_token(conn)
        if provider == ConferenceProvider.GOOGLE_MEET:
            requests.delete(
                f'https://www.googleapis.com/calendar/v3/calendars/primary/events/{session.provider_meeting_id}',
                params={'sendUpdates': 'all'},
                headers={'Authorization': f'Bearer {token}'},
                timeout=20,
            )
        elif provider == ConferenceProvider.ZOOM:
            requests.delete(
                f'https://api.zoom.us/v2/meetings/{session.provider_meeting_id}',
                headers={'Authorization': f'Bearer {token}'},
                timeout=20,
            )
    except Exception:
        logger.exception('Failed to cancel vendor meeting session_id=%s', session.id)


def _session_with_product(pk) -> StoreSlotSession:
    return StoreSlotSession.objects.select_related(
        'store_product',
        'store_product__store',
        'store_product__store__community',
        'store_product__bookable_meeting_settings',
    ).get(pk=pk)


def _persist_conference_failure(session_id, error: str) -> StoreSlotSession:
    StoreSlotSession.objects.filter(pk=session_id).update(
        conference_status=SlotConferenceStatus.FAILED,
        conference_error=(error or '')[:2000],
        updated_at=timezone.now(),
    )
    return _session_with_product(session_id)


def ensure_slot_conference(session: StoreSlotSession, *, attendee_email: str = '') -> StoreSlotSession:
    """Idempotent: create Meet/Zoom once; reuse join_url. Does not send email."""
    provider = ''
    conn = None
    with transaction.atomic():
        # Lock the session row only. select_related(bookable_meeting_settings) is a
        # nullable reverse OneToOne (LEFT JOIN); Postgres rejects FOR UPDATE on that.
        locked = StoreSlotSession.objects.select_for_update().get(pk=session.pk)
        locked = _session_with_product(locked.pk)
        if locked.cancelled_at:
            return locked
        settings = getattr(locked.store_product, 'bookable_meeting_settings', None)
        source = (getattr(settings, 'room_source', None) or '') or ''
        if source == 'manual' or not source:
            manual = (getattr(settings, 'manual_join_url', None) or '').strip()
            if manual:
                locked.join_url = manual
                locked.conference_status = SlotConferenceStatus.READY
                locked.conference_error = ''
                locked.conference_provider = ''
                locked.save(
                    update_fields=[
                        'join_url',
                        'conference_status',
                        'conference_error',
                        'conference_provider',
                        'updated_at',
                    ]
                )
            return locked
        if (locked.join_url or '').strip() and locked.conference_status == SlotConferenceStatus.READY:
            if (
                attendee_email
                and locked.conference_provider == ConferenceProvider.GOOGLE_MEET
                and int(locked.max_attendees_snapshot or 1) == 1
            ):
                community = locked.store_product.store.community
                meet_conn = active_connection(community, locked.conference_provider)
                if meet_conn:
                    try:
                        _add_google_attendee(locked, meet_conn, attendee_email)
                    except Exception:
                        logger.exception('Failed to add Google attendee session_id=%s', locked.id)
            return locked

        community = locked.store_product.store.community
        settings = getattr(locked.store_product, 'bookable_meeting_settings', None)
        provider = locked.conference_provider or (getattr(settings, 'room_source', None) or '')
        conn = active_connection(community, provider)
        if not conn:
            locked.conference_status = SlotConferenceStatus.FAILED
            locked.conference_error = 'No active Google or Zoom connection for this community.'
            locked.save(update_fields=['conference_status', 'conference_error', 'updated_at'])
            return locked

    try:
        if provider == ConferenceProvider.GOOGLE_MEET:
            result = _create_google_meet(locked, conn, attendee_email=attendee_email)
        elif provider == ConferenceProvider.ZOOM:
            result = _create_zoom_meeting(locked, conn)
        else:
            raise RuntimeError('Meeting product has no conference provider.')
    except Exception as exc:
        logger.exception('ensure_slot_conference failed session_id=%s', locked.id)
        return _persist_conference_failure(locked.pk, str(exc))

    try:
        with transaction.atomic():
            locked = StoreSlotSession.objects.select_for_update().get(pk=locked.pk)
            if (locked.join_url or '').strip() and locked.conference_status == SlotConferenceStatus.READY:
                return _session_with_product(locked.pk)
            locked.join_url = result.get('join_url') or ''
            locked.host_start_url = result.get('host_start_url') or ''
            locked.provider_meeting_id = result.get('provider_meeting_id') or ''
            locked.conference_provider = provider
            if not locked.ics_uid:
                locked.ics_uid = f'store-slot-{locked.id}@rockae.com'
            if locked.join_url:
                locked.conference_status = SlotConferenceStatus.READY
                locked.conference_error = ''
            else:
                locked.conference_status = SlotConferenceStatus.FAILED
                locked.conference_error = 'Provider did not return a join URL.'
            locked.save(
                update_fields=[
                    'join_url',
                    'host_start_url',
                    'provider_meeting_id',
                    'conference_provider',
                    'ics_uid',
                    'conference_status',
                    'conference_error',
                    'updated_at',
                ]
            )
    except Exception as exc:
        logger.exception('ensure_slot_conference save failed session_id=%s', locked.id)
        return _persist_conference_failure(locked.pk, str(exc))
    return _session_with_product(locked.pk)


def google_oauth_authorize_url(*, redirect_uri: str, state: str) -> str:
    client_id = getattr(settings, 'GOOGLE_CALENDAR_CLIENT_ID', None) or getattr(settings, 'GOOGLE_CLIENT_ID', '')
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/userinfo.email',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }
    return 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)


def zoom_oauth_authorize_url(*, redirect_uri: str, state: str) -> str:
    client_id = getattr(settings, 'ZOOM_CLIENT_ID', '') or ''
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
    }
    return 'https://zoom.us/oauth/authorize?' + urlencode(params)
