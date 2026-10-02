"""
Discrete bookable slots for store meeting products from weekly availability windows.

Used by Main API (list slots) and Payment (checkout validation). All slot instants
are UTC-aware :class:`datetime` objects.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from datetime import timezone as dt_timezone
from typing import Iterable, List, Optional, Sequence, Tuple

from django.utils import timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def normalize_utc_start(dt: datetime) -> datetime:
    """Normalize to aware UTC with microsecond cleared for stable comparisons."""
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, dt_timezone.utc)
    out = dt.astimezone(dt_timezone.utc).replace(microsecond=0)
    return out


def _windows_as_tuples(windows) -> List[Tuple[int, time, time]]:
    seq = windows.all() if hasattr(windows, 'all') else windows
    out: List[Tuple[int, time, time]] = []
    for w in seq:
        out.append((int(w.weekday), w.local_start, w.local_end))
    return out


def _daterange(d0: date, d1: date) -> Iterable[date]:
    d = d0
    while d <= d1:
        yield d
        d += timedelta(days=1)


def generate_meeting_slot_intervals(
    *,
    time_zone: str,
    duration_minutes: int,
    buffer_before_minutes: int,
    buffer_after_minutes: int,
    minimum_notice_minutes: int,
    windows: Sequence[Tuple[int, time, time]],
    range_start: date,
    range_end: date,
    now_utc: datetime,
    occupied_starts_utc: Optional[Iterable[datetime]] = None,
    max_slots: int = 4000,
    filter_by_occupied: bool = True,
) -> List[Tuple[datetime, datetime]]:
    """
    Return (start_utc, end_utc) for each slot in [range_start, range_end] on the owner's grid.

    Slot starts are aligned on a fixed grid from each window's local_start, stepping by
    ``duration + buffer_before + buffer_after`` minutes. Slots respect ``minimum_notice_minutes``
    from ``now_utc``.

    When ``filter_by_occupied`` is True (default), occupied starts are omitted. When False,
    all grid starts from ``earliest_utc`` onward are returned so callers can mark taken slots.
    """
    if not windows or range_end < range_start:
        return []
    try:
        tz = ZoneInfo((time_zone or 'UTC').strip() or 'UTC')
    except ZoneInfoNotFoundError:
        return []

    occ = {normalize_utc_start(x) for x in (occupied_starts_utc or ())}
    duration_td = timedelta(minutes=int(duration_minutes))
    step_minutes = int(duration_minutes) + int(buffer_before_minutes) + int(buffer_after_minutes)
    step_td = timedelta(minutes=max(step_minutes, int(duration_minutes)))
    notice_td = timedelta(minutes=int(minimum_notice_minutes))
    earliest_utc = normalize_utc_start(now_utc + notice_td)

    results: List[Tuple[datetime, datetime]] = []

    for d in _daterange(range_start, range_end):
        iso_dow = d.isoweekday()
        for wday, t_start, t_end in windows:
            if int(wday) != iso_dow:
                continue
            if t_start >= t_end:
                continue
            try:
                window_start = datetime.combine(d, t_start).replace(tzinfo=tz)
                window_end = datetime.combine(d, t_end).replace(tzinfo=tz)
            except (ValueError, OSError):
                continue

            cursor = window_start
            while cursor + duration_td <= window_end:
                start_utc = normalize_utc_start(cursor.astimezone(dt_timezone.utc))
                if start_utc < earliest_utc:
                    cursor += step_td
                    continue
                if filter_by_occupied and start_utc in occ:
                    cursor += step_td
                    continue
                end_utc = normalize_utc_start((cursor + duration_td).astimezone(dt_timezone.utc))
                results.append((start_utc, end_utc))
                if len(results) >= max_slots:
                    return sorted(results, key=lambda x: x[0])
                cursor += step_td

    results.sort(key=lambda x: x[0])
    return results


def list_meeting_slots_for_product_public(
    product,
    *,
    range_start: date,
    range_end: date,
    now_utc: Optional[datetime] = None,
    max_slots: int = 4000,
) -> List[dict]:
    """
    JSON-serializable slots for storefront: ``start``, ``end`` (ISO-8601 UTC), ``label``,
    and ``available`` (bool). Taken or held starts are included with ``available: false`` so
    UIs can grey them out like Calendly.
    """
    from app_models.community_store.models import StoreBookableMeetingSettings, StoreProductKind

    now_utc = now_utc or timezone.now()
    if getattr(product, 'product_kind', None) != StoreProductKind.MEETING:
        return []

    try:
        settings = product.bookable_meeting_settings
    except StoreBookableMeetingSettings.DoesNotExist:
        return []

    windows = _windows_as_tuples(settings.windows)
    if not windows:
        return []

    from app_models.community_store.conference import occupancy_counts_for_starts

    max_att = int(getattr(settings, 'max_attendees', 1) or 0)

    intervals = generate_meeting_slot_intervals(
        time_zone=settings.time_zone,
        duration_minutes=settings.duration_minutes,
        buffer_before_minutes=settings.buffer_before_minutes,
        buffer_after_minutes=settings.buffer_after_minutes,
        minimum_notice_minutes=settings.minimum_notice_minutes,
        windows=windows,
        range_start=range_start,
        range_end=range_end,
        now_utc=now_utc,
        occupied_starts_utc=None,
        max_slots=max_slots,
        filter_by_occupied=False,
    )

    tz_label = (settings.time_zone or 'UTC').strip() or 'UTC'
    try:
        disp_tz = ZoneInfo(tz_label)
    except ZoneInfoNotFoundError:
        disp_tz = ZoneInfo('UTC')

    counts = occupancy_counts_for_starts(
        product.id,
        [start for start, _end in intervals],
        now=now_utc,
    )

    out: List[dict] = []
    for start_utc, end_utc in intervals:
        local = start_utc.astimezone(disp_tz)
        label = local.strftime('%a %d %b %Y, %H:%M')
        su = normalize_utc_start(start_utc)
        taken = int(counts.get(su, 0) or 0)
        if max_att == 0:
            available = True
            remaining = None
        else:
            remaining = max(0, max_att - taken)
            available = remaining > 0
        out.append(
            {
                'start': start_utc.isoformat().replace('+00:00', 'Z'),
                'end': end_utc.isoformat().replace('+00:00', 'Z'),
                'label': label,
                'available': available,
                'seats_taken': taken,
                'seats_remaining': remaining,
            }
        )
    return out


def list_meeting_slots_from_next_available(
    product,
    *,
    window_days: int = 14,
    search_days: int = 400,
    now_utc: Optional[datetime] = None,
    max_slots: int = 4000,
) -> List[dict]:
    """Slots for a short window starting on the local date of the next bookable time."""
    from app_models.community_store.conference import occupancy_counts_for_starts
    from app_models.community_store.models import StoreBookableMeetingSettings, StoreProductKind

    now_utc = now_utc or timezone.now()
    window_days = max(1, min(int(window_days or 14), 31))
    search_days = max(1, min(int(search_days or 400), 400))
    if getattr(product, 'product_kind', None) != StoreProductKind.MEETING:
        return []

    try:
        settings = product.bookable_meeting_settings
    except StoreBookableMeetingSettings.DoesNotExist:
        return []

    windows = _windows_as_tuples(settings.windows)
    if not windows:
        return []

    max_att = int(getattr(settings, 'max_attendees', 1) or 0)
    tz_label = (settings.time_zone or 'UTC').strip() or 'UTC'
    try:
        disp_tz = ZoneInfo(tz_label)
    except ZoneInfoNotFoundError:
        disp_tz = ZoneInfo('UTC')

    today = now_utc.astimezone(disp_tz).date()
    next_day: Optional[date] = None
    for offset in range(search_days):
        day = today + timedelta(days=offset)
        day_intervals = generate_meeting_slot_intervals(
            time_zone=settings.time_zone,
            duration_minutes=settings.duration_minutes,
            buffer_before_minutes=settings.buffer_before_minutes,
            buffer_after_minutes=settings.buffer_after_minutes,
            minimum_notice_minutes=settings.minimum_notice_minutes,
            windows=windows,
            range_start=day,
            range_end=day,
            now_utc=now_utc,
            occupied_starts_utc=None,
            max_slots=80,
            filter_by_occupied=False,
        )
        if not day_intervals:
            continue
        if max_att == 0:
            next_day = day
            break
        counts = occupancy_counts_for_starts(
            product.id,
            [start for start, _end in day_intervals],
            now=now_utc,
        )
        for start_utc, _end in day_intervals:
            taken = int(counts.get(normalize_utc_start(start_utc), 0) or 0)
            if taken < max_att:
                next_day = day
                break
        if next_day is not None:
            break

    if next_day is None:
        return []
    return list_meeting_slots_for_product_public(
        product,
        range_start=next_day,
        range_end=next_day + timedelta(days=window_days - 1),
        now_utc=now_utc,
        max_slots=max_slots,
    )


def validate_booked_slot_start_for_checkout(product, slot_start_utc: datetime, *, now_utc: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    Return (ok, error_message). ``error_message`` is empty when ``ok``.

    Ensures the instant is on the owner's availability grid for that local day, respects
    minimum notice, and has remaining capacity.
    """
    from app_models.community_store.conference import expire_stale_pending_purchases, slot_is_full
    from app_models.community_store.models import (
        ConferenceConnectionStatus,
        ConferenceProvider,
        StoreBookableMeetingSettings,
        StoreProductKind,
    )

    now_utc = now_utc or timezone.now()
    if getattr(product, 'product_kind', None) != StoreProductKind.MEETING:
        return False, 'Product is not a bookable meeting.'

    try:
        settings = product.bookable_meeting_settings
    except StoreBookableMeetingSettings.DoesNotExist:
        return False, 'This meeting does not have availability configured yet.'

    source = (getattr(settings, 'room_source', None) or '').strip()
    if source == 'manual' or not source:
        if not (getattr(settings, 'manual_join_url', None) or '').strip():
            return False, 'This meeting needs a join URL before it can be booked.'
    elif source in (ConferenceProvider.GOOGLE_MEET, ConferenceProvider.ZOOM):
        community = product.store.community
        from app_models.community_store.models import CommunityConferenceConnection

        if not CommunityConferenceConnection.objects.filter(
            community=community,
            provider=source,
            status=ConferenceConnectionStatus.ACTIVE,
        ).exists():
            return False, 'The host needs to reconnect Google Meet or Zoom before this time can be booked.'
    else:
        return False, 'Choose a join URL or a connected Google Meet / Zoom account before selling times.'

    windows = _windows_as_tuples(settings.windows)
    if not windows:
        return False, 'No weekly availability windows are configured.'

    ss = normalize_utc_start(slot_start_utc)

    try:
        tz = ZoneInfo((settings.time_zone or 'UTC').strip() or 'UTC')
    except ZoneInfoNotFoundError:
        return False, 'Invalid time zone on this product.'

    local = ss.astimezone(tz)
    day = local.date()

    expire_stale_pending_purchases(product.id, now=now_utc)

    intervals = generate_meeting_slot_intervals(
        time_zone=settings.time_zone,
        duration_minutes=settings.duration_minutes,
        buffer_before_minutes=settings.buffer_before_minutes,
        buffer_after_minutes=settings.buffer_after_minutes,
        minimum_notice_minutes=settings.minimum_notice_minutes,
        windows=windows,
        range_start=day,
        range_end=day,
        now_utc=now_utc,
        occupied_starts_utc=None,
        max_slots=2000,
        filter_by_occupied=False,
    )
    matched_end = None
    for start_utc, end_utc in intervals:
        if normalize_utc_start(start_utc) == ss:
            matched_end = end_utc
            break
    if matched_end is None:
        return False, 'That time is not available. Choose another slot from the list.'
    if slot_is_full(settings, product.id, ss, now=now_utc):
        return False, 'That time is full. Choose another slot from the list.'
    return True, ''
