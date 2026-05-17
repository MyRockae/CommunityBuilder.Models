# Add has_adaptive_video to existing tier entitlements JSON

from django.db import migrations


PAID_TIERS = frozenset({'hobby', 'professional', 'enterprise'})


def seed_has_adaptive_video(apps, schema_editor):
    AppSubscriptionTier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in AppSubscriptionTier.objects.all():
        entitlements = tier.entitlements if isinstance(tier.entitlements, dict) else {}
        features = dict(entitlements.get('features') or {})
        features['has_adaptive_video'] = tier.tier_name in PAID_TIERS
        entitlements = dict(entitlements)
        entitlements['features'] = features
        limits = entitlements.get('limits')
        if limits is None:
            entitlements['limits'] = {}
        tier.entitlements = entitlements
        tier.save(update_fields=['entitlements'])


def reverse_seed(apps, schema_editor):
    AppSubscriptionTier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in AppSubscriptionTier.objects.all():
        entitlements = tier.entitlements if isinstance(tier.entitlements, dict) else {}
        features = dict(entitlements.get('features') or {})
        features.pop('has_adaptive_video', None)
        entitlements = dict(entitlements)
        entitlements['features'] = features
        tier.entitlements = entitlements
        tier.save(update_fields=['entitlements'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0017_appsubscriptiontier_entitlements'),
    ]

    operations = [
        migrations.RunPython(seed_has_adaptive_video, reverse_seed),
    ]
