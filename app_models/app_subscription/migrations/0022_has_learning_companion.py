from django.db import migrations


def seed_learning_companion(apps, schema_editor):
    Tier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    paid = {'professional', 'enterprise'}
    for tier in Tier.objects.all():
        ent = dict(tier.entitlements or {})
        features = dict(ent.get('features') or {})
        if 'has_learning_companion' in features:
            continue
        features['has_learning_companion'] = tier.tier_name in paid
        ent['features'] = features
        if 'limits' not in ent:
            ent['limits'] = {}
        tier.entitlements = ent
        tier.save(update_fields=['entitlements'])


def unseed_learning_companion(apps, schema_editor):
    Tier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in Tier.objects.all():
        ent = dict(tier.entitlements or {})
        features = dict(ent.get('features') or {})
        if 'has_learning_companion' not in features:
            continue
        features.pop('has_learning_companion', None)
        ent['features'] = features
        tier.entitlements = ent
        tier.save(update_fields=['entitlements'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0021_rename_max_classrooms_to_max_courses'),
    ]

    operations = [
        migrations.RunPython(seed_learning_companion, unseed_learning_companion),
    ]
