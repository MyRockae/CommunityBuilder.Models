"""
Canonical schema for AppSubscriptionTier.entitlements JSONField.

Structure:
  {"limits": {...}, "features": {...}}

Numeric limits use null for unlimited (same semantics as former nullable IntegerFields).
"""

from django.core.exceptions import ValidationError

LIMIT_KEYS = frozenset(
    {
        "max_communities",
        "max_members",
        "max_admins",
        "max_free_community_groups",
        "max_paid_community_groups",
        "max_quiz_generations_per_month",
        "max_forums",
        "max_classrooms",
        "max_resources",
        "storage_limit_gb",
    }
)

FEATURE_KEYS = frozenset(
    {
        "has_store_access",
        "has_events_access",
        "has_blog_access",
        "has_api_access",
        "has_custom_domain",
        "has_custom_email",
    }
)


def validate_tier_entitlements(value):
    """Raise ValidationError if value is not a valid entitlements payload (strict keys)."""
    if value is None:
        value = {}
    if not isinstance(value, dict):
        raise ValidationError("Entitlements must be a JSON object.")

    limits = value.get("limits", {})
    features = value.get("features", {})

    if limits is None:
        limits = {}
    if features is None:
        features = {}

    if not isinstance(limits, dict):
        raise ValidationError({"limits": "Must be an object."})
    if not isinstance(features, dict):
        raise ValidationError({"features": "Must be an object."})

    unknown_l = set(limits.keys()) - LIMIT_KEYS
    if unknown_l:
        raise ValidationError({"limits": f"Unknown keys: {sorted(unknown_l)}"})

    unknown_f = set(features.keys()) - FEATURE_KEYS
    if unknown_f:
        raise ValidationError({"features": f"Unknown keys: {sorted(unknown_f)}"})

    for key, v in limits.items():
        if v is None:
            continue
        if not isinstance(v, int):
            raise ValidationError({"limits": f"{key} must be an integer or null."})
        if v < 0:
            raise ValidationError({"limits": f"{key} must be non-negative."})

    for key, v in features.items():
        if not isinstance(v, bool):
            raise ValidationError({"features": f"{key} must be a boolean."})

    extra_top = set(value.keys()) - {"limits", "features"}
    if extra_top:
        raise ValidationError(f"Unknown top-level keys: {sorted(extra_top)}")


def empty_entitlements():
    return {"limits": {}, "features": {}}
