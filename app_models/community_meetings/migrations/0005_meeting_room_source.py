from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_meetings', '0004_rename_payment_plans_m2m_to_community_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingseries',
            name='room_source',
            field=models.CharField(
                choices=[
                    ('manual', 'Provide URL manually'),
                    ('google_meet', 'Google Meet'),
                    ('zoom', 'Zoom'),
                ],
                default='manual',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='meetingseries',
            name='provider_meeting_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='meeting',
            name='room_source',
            field=models.CharField(
                choices=[
                    ('manual', 'Provide URL manually'),
                    ('google_meet', 'Google Meet'),
                    ('zoom', 'Zoom'),
                ],
                default='manual',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='meeting',
            name='provider_meeting_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
