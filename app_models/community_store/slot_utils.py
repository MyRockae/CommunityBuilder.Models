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
    max_slots: int = 500,
) -> List[Tuple[datetime, datetime]]:
    """
    Return (start_utc, end_utc) for each bookable slot in [range_start, range_end].

    Slot starts are aligned on a fixed grid from each window's local_start, stepping by
    ``duration + buffer_before + buffer_after`` minutes. Slots respect ``minimum_notice_minutes``
    from ``now_utc``. Occupied starts (exact UTC slot starts) are excluded.
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
                if start_utc >= earliest_utc and start_utc not in occ:
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
    max_slots: int = 500,
) -> List[dict]:
    """
    JSON-serializable slots for storefront: ``start``, ``end`` (ISO-8601 UTC), ``label``.

    ``product`` must be a meeting :class:`~app_models.community_store.models.StoreProduct`
    with ``bookable_meeting_settings`` and ``windows`` prefetched when possible.
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

    from app_models.community_store.models import StoreProductSlotHold, StoreProductSlotHoldStatus, StorePurchase

    occupied: List[datetime] = []
    occupied.extend(
        StorePurchase.objects.filter(
            product_id=product.id,
            status__in=[StorePurchase.STATUS_COMPLETED, StorePurchase.STATUS_PENDING],
            booked_slot_start_utc__isnull=False,
        ).values_list('booked_slot_start_utc', flat=True)
    )
    occupied.extend(
        StoreProductSlotHold.objects.filter(
            store_product_id=product.id,
            status=StoreProductSlotHoldStatus.PENDING,
            hold_until__gt=now_utc,
        ).values_list('slot_start_utc', flat=True)
    )

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
        occupied_starts_utc=occupied,
        max_slots=max_slots,
    )

    tz_label = (settings.time_zone or 'UTC').strip() or 'UTC'
    try:
        disp_tz = ZoneInfo(tz_label)
    except ZoneInfoNotFoundError:
        disp_tz = ZoneInfo('UTC')

    out: List[dict] = []
    for start_utc, end_utc in intervals:
        local = start_utc.astimezone(disp_tz)
        label = local.strftime('%a %d %b %Y, %H:%M')
        out.append(
            {
                'start': start_utc.isoformat().replace('+00:00', 'Z'),
                'end': end_utc.isoformat().replace('+00:00', 'Z'),
                'label': label,
            }
        )
    return out


def validate_booked_slot_start_for_checkout(product, slot_start_utc: datetime, *, now_utc: Optional[datetime] = None) -> Tuple[bool, str]:
    """
    Return (ok, error_message). ``error_message`` is empty when ``ok``.

    Ensures the instant is on the owner's availability grid for that local day, respects
    minimum notice, and does not collide with completed/pending purchases or active holds.
    """
    from app_models.community_store.models import (
        StoreBookableMeetingSettings,
        StoreProductKind,
        StoreProductSlotHold,
        StoreProductSlotHoldStatus,
        StorePurchase,
    )

    now_utc = now_utc or timezone.now()
    if getattr(product, 'product_kind', None) != StoreProductKind.MEETING:
        return False, 'Product is not a bookable meeting.'

    try:
        settings = product.bookable_meeting_settings
    except StoreBookableMeetingSettings.DoesNotExist:
        return False, 'This meeting does not have availability configured yet.'

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

    occupied: List[datetime] = []
    occupied.extend(
        StorePurchase.objects.filter(
            product_id=product.id,
            status__in=[StorePurchase.STATUS_COMPLETED, StorePurchase.STATUS_PENDING],
            booked_slot_start_utc__isnull=False,
        ).values_list('booked_slot_start_utc', flat=True)
    )
    occupied.extend(
        StoreProductSlotHold.objects.filter(
            store_product_id=product.id,
            status=StoreProductSlotHoldStatus.PENDING,
            hold_until__gt=now_utc,
        ).values_list('slot_start_utc', flat=True)
    )

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
        occupied_starts_utc=occupied,
        max_slots=2000,
    )
    for start_utc, _end in intervals:
        if normalize_utc_start(start_utc) == ss:
            return True, ''
    return False, 'That time is not available. Choose another slot from the list.'
