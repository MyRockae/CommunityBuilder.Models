from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_subscription', '0013_alter_appsubscriptiontier_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appsubscriptiontier',
            name='price',
        ),
    ]
