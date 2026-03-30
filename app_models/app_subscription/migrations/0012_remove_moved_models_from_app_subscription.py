# Remove PaymentTransaction, CreatorPayoutAccount, and StorageUsage from this app's *state* only.
# Physical tables unchanged; see app_payments.0001_initial and storage_usage.0001_initial.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0011_appsubscriptiontierprice'),
        ('app_payments', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='PaymentTransaction'),
                migrations.DeleteModel(name='CreatorPayoutAccount'),
                migrations.DeleteModel(name='StorageUsage'),
            ],
        ),
    ]
