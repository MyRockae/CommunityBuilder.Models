from django.db import migrations


def pop_has_adaptive_video(apps, schema_editor):
    AppSubscriptionTier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in AppSubscriptionTier.objects.all():
        entitlements = tier.entitlements or {}
        features = entitlements.get('features')
        if not isinstance(features, dict) or 'has_adaptive_video' not in features:
            continue
        features = dict(features)
        features.pop('has_adaptive_video', None)
        entitlements = dict(entitlements)
        entitlements['features'] = features
        tier.entitlements = entitlements
        tier.save(update_fields=['entitlements'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0019_communitymembersubscription_is_trial'),
    ]

    operations = [
        migrations.RunPython(pop_has_adaptive_video, noop_reverse),
    ]
