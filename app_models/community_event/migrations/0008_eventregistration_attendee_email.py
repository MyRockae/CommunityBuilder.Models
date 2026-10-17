from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_attendee_contact(apps, schema_editor):
    EventRegistration = apps.get_model("community_event", "EventRegistration")
    User = apps.get_model("account", "User")
    UserProfile = apps.get_model("user_profile", "UserProfile")
    user_ids = list(
        EventRegistration.objects.exclude(attendee_user_id=None)
        .values_list("attendee_user_id", flat=True)
        .distinct()
    )
    if not user_ids:
        return
    users = {row.id: row for row in User.objects.filter(id__in=user_ids)}
    profiles = {row.user_id: row for row in UserProfile.objects.filter(user_id__in=user_ids)}
    for reg in EventRegistration.objects.exclude(attendee_user_id=None).iterator():
        user = users.get(reg.attendee_user_id)
        if user is None:
            continue
        email = (user.email or "").strip().lower()
        profile = profiles.get(user.id)
        first = (getattr(profile, "first_name", "") or "").strip() if profile else ""
        last = (getattr(profile, "last_name", "") or "").strip() if profile else ""
        name = f"{first} {last}".strip() or (getattr(user, "username", None) or "").strip()
        if not name and email:
            name = email.split("@")[0]
        reg.attendee_email = email
        reg.attendee_name = (name or "")[:255]
        reg.save(update_fields=["attendee_email", "attendee_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("community_event", "0007_event_room_source"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("user_profile", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventregistration",
            name="attendee_email",
            field=models.EmailField(blank=True, db_index=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="eventregistration",
            name="attendee_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="eventregistration",
            name="attendance_emailed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="eventregistration",
            name="attendee_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="event_registrations",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(backfill_attendee_contact, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="eventregistration",
            constraint=models.UniqueConstraint(
                condition=models.Q(status="completed") & ~models.Q(attendee_email=""),
                fields=("event", "attendee_email"),
                name="eventregistration_unique_completed_email_per_event",
            ),
        ),
    ]
