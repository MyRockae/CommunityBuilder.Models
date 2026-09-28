from django.db import migrations


def rename_max_classrooms_limit(apps, schema_editor):
    AppSubscriptionTier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in AppSubscriptionTier.objects.all().iterator():
        entitlements = tier.entitlements or {}
        limits = entitlements.get('limits') or {}
        if 'max_classrooms' not in limits:
            continue
        limits['max_courses'] = limits.pop('max_classrooms')
        entitlements['limits'] = limits
        tier.entitlements = entitlements
        tier.save(update_fields=['entitlements'])


def reverse_max_classrooms_limit(apps, schema_editor):
    AppSubscriptionTier = apps.get_model('app_subscription', 'AppSubscriptionTier')
    for tier in AppSubscriptionTier.objects.all().iterator():
        entitlements = tier.entitlements or {}
        limits = entitlements.get('limits') or {}
        if 'max_courses' not in limits:
            continue
        limits['max_classrooms'] = limits.pop('max_courses')
        entitlements['limits'] = limits
        tier.entitlements = entitlements
        tier.save(update_fields=['entitlements'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0020_pop_has_adaptive_video_entitlement'),
    ]

    operations = [
        migrations.RunPython(rename_max_classrooms_limit, reverse_max_classrooms_limit),
    ]
