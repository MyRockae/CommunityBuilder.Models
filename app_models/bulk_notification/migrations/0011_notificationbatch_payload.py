from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_notification', '0010_inbox_image_ref'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationbatch',
            name='payload',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Inbox copy and audience hints for BulkNotification.Service: '
                    'object_type, title, excerpt, deep_link, image_ref, actor_name, '
                    'actor_avatar_ref, audience (members|owners|explicit|scoped), '
                    'optional recipient_user_ids, group_ids, staff_roles, extra_user_ids.'
                ),
            ),
        ),
    ]
