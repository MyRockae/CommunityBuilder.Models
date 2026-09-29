from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("community_forms", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="communityformresponse",
            name="enforce_one_per_user",
            field=models.BooleanField(
                default=False,
                help_text="Copied from the form at submit time for the partial unique constraint.",
            ),
        ),
        migrations.AddConstraint(
            model_name="communityformresponse",
            constraint=models.UniqueConstraint(
                condition=models.Q(("enforce_one_per_user", True), ("user__isnull", False)),
                fields=("form", "user"),
                name="cform_resp_one_per_user",
            ),
        ),
    ]
