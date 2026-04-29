from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community_event", "0003_communityevent_summary_attendee_limit"),
    ]

    operations = [
        migrations.AddField(
            model_name="communityevent",
            name="agenda",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Ordered schedule segments as JSON list, e.g. [{"title": str, "description": optional,'
                ' "starts_at": iso-8601, "ends_at": iso-8601}]',
            ),
        ),
    ]
