"""Whether an owner may refund a charge. No database access."""

from datetime import timedelta

REASON_OUTSIDE_WINDOW = "outside_window"
REASON_EVENT_ENDED = "event_ended"
REASON_ALREADY_PAID_OUT = "already_paid_out"


def refund_availability(
    *,
    paid_at,
    transferred_to_owner,
    window_hours,
    now,
    ends_at=None,
    has_succeeded_charge=True,
):
    """
    Return ``(available, reason)``.

    ``reason`` is set only for a succeeded charge that cannot be refunded.
    ``ends_at`` is the event end. Group subscriptions pass none.
    """
    if not has_succeeded_charge:
        return False, None
    if ends_at is not None and ends_at <= now:
        return False, REASON_EVENT_ENDED
    if transferred_to_owner:
        return False, REASON_ALREADY_PAID_OUT
    if paid_at is None:
        return False, REASON_OUTSIDE_WINDOW
    try:
        hours = int(window_hours)
    except (TypeError, ValueError):
        hours = 336
    if hours < 0:
        hours = 0
    if now - paid_at > timedelta(hours=hours):
        return False, REASON_OUTSIDE_WINDOW
    return True, None
