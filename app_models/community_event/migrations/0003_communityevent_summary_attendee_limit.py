from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community_event", "0002_rename_communityev_communi_b6c73a_idx_communityev_communi_bd9b69_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="communityevent",
            name="summary",
            field=models.CharField(
                blank=True,
                help_text="Short event summary",
                max_length=500,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="communityevent",
            name="attendee_limit",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Maximum attendees; 0 means no limit",
            ),
        ),
    ]
