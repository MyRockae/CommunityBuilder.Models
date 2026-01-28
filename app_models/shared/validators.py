"""
Shared validators for app_models. Reusable across community (alias), account (username), etc.
"""
from django.core.validators import RegexValidator

# Letters, numbers, hyphen (-) and underscore (_) only. Use for alias, username, and similar slug-like fields.
slug_username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9_-]+$',
    message='May only contain letters, numbers, hyphens (-) and underscores (_).',
    code='invalid_slug_username',
)
