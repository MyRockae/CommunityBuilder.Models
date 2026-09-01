from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bulk_notification', '0002_email_campaign_and_platform_preference'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailcampaign',
            name='attachments',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text=(
                    'Downloadable files sent with the campaign. Each item is '
                    '{storage_ref, filename, content_type, size_bytes} under the public/ zone.'
                ),
            ),
        ),
    ]
