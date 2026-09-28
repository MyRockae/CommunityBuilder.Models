from django.db import migrations, models


def _rename_dedupe(apps, old_prefix, new_prefix):
    NotificationBatch = apps.get_model('bulk_notification', 'NotificationBatch')
    for batch in NotificationBatch.objects.filter(dedupe_key__startswith=old_prefix).iterator():
        batch.dedupe_key = new_prefix + batch.dedupe_key[len(old_prefix):]
        batch.save(update_fields=['dedupe_key'])


def rename_classroom_published(apps, schema_editor):
    NotificationBatch = apps.get_model('bulk_notification', 'NotificationBatch')
    NotificationDelivery = apps.get_model('bulk_notification', 'NotificationDelivery')
    NotificationBatch.objects.filter(event_type='classroom_published').update(event_type='course_published')
    NotificationDelivery.objects.filter(event_type='classroom_published').update(event_type='course_published')
    _rename_dedupe(apps, 'classroom_published:', 'course_published:')


def reverse_classroom_published(apps, schema_editor):
    NotificationBatch = apps.get_model('bulk_notification', 'NotificationBatch')
    NotificationDelivery = apps.get_model('bulk_notification', 'NotificationDelivery')
    NotificationBatch.objects.filter(event_type='course_published').update(event_type='classroom_published')
    NotificationDelivery.objects.filter(event_type='course_published').update(event_type='classroom_published')
    _rename_dedupe(apps, 'course_published:', 'classroom_published:')


EVENT_CHOICES = [
    ('town_hall_post', 'Town hall post'),
    ('forum_post', 'Forum post'),
    ('blog_post', 'Blog post'),
    ('course_published', 'Course published'),
    ('inactive_user', 'Inactive user'),
    ('views_momentum', 'Community views momentum'),
    ('marketing_campaign', 'Marketing campaign'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_notification', '0003_emailcampaign_attachments'),
    ]

    operations = [
        migrations.RunPython(rename_classroom_published, reverse_classroom_published),
        migrations.AlterField(
            model_name='notificationbatch',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Which notification this batch represents',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='notificationdelivery',
            name='event_type',
            field=models.CharField(
                choices=EVENT_CHOICES,
                help_text='Denormalised from the batch so cooldown lookups avoid a join',
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name='notificationbatch',
            name='object_id',
            field=models.BigIntegerField(
                blank=True,
                help_text='Primary key of the triggering object (post, blog post, course); null for platform-wide scans',
                null=True,
            ),
        ),
    ]
