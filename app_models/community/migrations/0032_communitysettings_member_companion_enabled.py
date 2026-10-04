from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0031_companion_guidance_and_member_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitysettings',
            name='member_companion_enabled',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Owner opt-in for the member Companion rail. Does not enable a future '
                    'owner companion. Preference only; never system instructions.'
                ),
            ),
        ),
    ]
