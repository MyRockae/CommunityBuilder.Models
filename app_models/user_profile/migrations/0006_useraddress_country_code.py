# Generated manually — UserAddress.billing_country → country_code

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_useraddress_address_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useraddress',
            old_name='billing_country',
            new_name='country_code',
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='country_code',
            field=models.CharField(
                blank=True,
                help_text='ISO 3166-1 alpha-2 for this address (tax / billing / residence)',
                max_length=2,
                null=True,
            ),
        ),
    ]
