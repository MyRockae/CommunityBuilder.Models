import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('community_meetings', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Meeting title', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Meeting description/notes', null=True)),
                ('location', models.CharField(blank=True, help_text='Physical meeting location', max_length=500, null=True)),
                ('meeting_url', models.URLField(blank=True, help_text='Virtual meeting URL (Zoom, Google Meet, etc.)', null=True)),
                ('time_zone', models.CharField(default='UTC', help_text='IANA timezone name (e.g. America/New_York)', max_length=64)),
                ('recurrence_frequency', models.CharField(choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], help_text='How often occurrences repeat', max_length=20)),
                ('interval', models.PositiveIntegerField(default=1, help_text='Every N days/weeks/months/years depending on frequency', validators=[django.core.validators.MinValueValidator(1)])),
                ('weekly_days', models.JSONField(blank=True, default=list, help_text='When frequency is weekly: non-empty list of ISO weekdays 1–7 (Mon=1 … Sun=7)', null=True)),
                ('recurrence_end_type', models.CharField(choices=[('never', 'Never'), ('on_date', 'On date'), ('after_count', 'After count')], default='never', max_length=20)),
                ('recurrence_end_date', models.DateField(blank=True, help_text='Last possible occurrence date in time_zone when end type is ON_DATE', null=True)),
                ('occurrence_count', models.PositiveIntegerField(blank=True, help_text='Total occurrences including the first when end type is AFTER_COUNT', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_series', to='community.community')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_meeting_series', to=settings.AUTH_USER_MODEL)),
                ('attendees', models.ManyToManyField(blank=True, help_text='Users invited to occurrences in this series', related_name='meeting_series_attending', to=settings.AUTH_USER_MODEL)),
                ('payment_plans', models.ManyToManyField(blank=True, help_text='Payment plans that have access to this series', related_name='meeting_series', to='community.paymentplan')),
            ],
            options={
                'verbose_name': 'Meeting Series',
                'verbose_name_plural': 'Meeting Series',
                'db_table': 'MeetingSeries',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='meetingseries',
            index=models.Index(fields=['community', 'created_at'], name='MeetingSer_communi_8a1b2c_idx'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='series',
            field=models.ForeignKey(blank=True, help_text='Recurring series this occurrence belongs to, if any', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='community_meetings.meetingseries'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='series_sequence',
            field=models.PositiveIntegerField(blank=True, help_text='Stable ordering within a series (e.g. 1-based occurrence index)', null=True),
        ),
        migrations.AddIndex(
            model_name='meeting',
            index=models.Index(fields=['series', 'start_datetime'], name='Meeting_series_start_idx'),
        ),
        migrations.AddIndex(
            model_name='meeting',
            index=models.Index(fields=['community', 'start_datetime'], name='Meeting_community_start_idx'),
        ),
    ]
