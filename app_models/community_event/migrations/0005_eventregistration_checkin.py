from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("community_event", "0004_communityevent_agenda"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="eventregistration",
            name="checked_in_at",
            field=models.DateTimeField(
                blank=True,
                help_text="When staff checked in this attendee (physical events only).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="eventregistration",
            name="checked_in_by",
            field=models.ForeignKey(
                blank=True,
                help_text="Staff user who recorded check-in.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="event_registrations_checked_in",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
