from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0032_communitysettings_member_companion_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitysettings',
            name='owner_notification_preferences',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Owner/co-owner notification opt-ins by event type. Keys are stable event ids '
                    '(e.g. feedback, public_feed_reply, blog_reply, quiz_submission); '
                    'values are typically boolean. Omitted keys are treated as off (opt-in).'
                ),
            ),
        ),
    ]
