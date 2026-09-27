from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_event', '0006_alter_communityevent_agenda'),
    ]

    operations = [
        migrations.AddField(
            model_name='communityevent',
            name='room_source',
            field=models.CharField(
                choices=[
                    ('manual', 'Provide URL manually'),
                    ('google_meet', 'Google Meet'),
                    ('zoom', 'Zoom'),
                ],
                default='manual',
                help_text='manual, google_meet, or zoom',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='communityevent',
            name='provider_meeting_id',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
