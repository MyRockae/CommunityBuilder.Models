from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0034_community_is_listed'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='communitymember',
            name='referred_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Community referrer stamped once when this membership row is created.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referred_community_members',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='referral_bonus_enabled',
            field=models.BooleanField(
                default=False,
                help_text='If true, the community referrer may earn on the referred member’s first paid group charge.',
            ),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='referral_bonus_percent',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                help_text='Percent of community_amount (list price) paid to the referrer. Max 50.',
                max_digits=5,
                validators=[
                    django.core.validators.MinValueValidator(Decimal('0.00')),
                    django.core.validators.MaxValueValidator(Decimal('50.00')),
                ],
            ),
        ),
    ]
