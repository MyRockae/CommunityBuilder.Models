import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0009_userfiscalprofile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentcheckoutsession',
            name='user',
            field=models.ForeignKey(
                blank=True,
                help_text='Buyer who may redeem this session; null for guest store checkout',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payment_checkout_sessions',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
