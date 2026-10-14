from django.db import migrations

LOWER_TIERS = {'free_hobby', 'hobby'}


def enable_learning_companion_all_tiers(apps, schema_editor):
    Tier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in Tier.objects.all():
        ent = dict(tier.entitlements or {})
        features = dict(ent.get('features') or {})
        features['has_learning_companion'] = True
        ent['features'] = features
        if 'limits' not in ent:
            ent['limits'] = {}
        tier.entitlements = ent
        tier.save(update_fields=['entitlements'])


def restore_learning_companion_lower_tiers(apps, schema_editor):
    Tier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in Tier.objects.all():
        if tier.tier_name not in LOWER_TIERS:
            continue
        ent = dict(tier.entitlements or {})
        features = dict(ent.get('features') or {})
        features['has_learning_companion'] = False
        ent['features'] = features
        if 'limits' not in ent:
            ent['limits'] = {}
        tier.entitlements = ent
        tier.save(update_fields=['entitlements'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0022_has_learning_companion'),
    ]

    operations = [
        migrations.RunPython(
            enable_learning_companion_all_tiers,
            restore_learning_companion_lower_tiers,
        ),
    ]
