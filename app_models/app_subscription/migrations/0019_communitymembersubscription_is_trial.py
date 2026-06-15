from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0018_seed_has_adaptive_video_entitlement'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitymembersubscription',
            name='is_trial',
            field=models.BooleanField(
                default=False,
                help_text='True when access was granted via a free trial (no payment yet).',
            ),
        ),
    ]
