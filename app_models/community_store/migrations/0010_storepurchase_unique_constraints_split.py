# Generated manually for multiple meeting bookings per buyer+product.

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0009_alter_storeproduct_template_meeting'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='storepurchase',
            name='storepurchase_unique_completed_email_per_product',
        ),
        migrations.AddConstraint(
            model_name='storepurchase',
            constraint=models.UniqueConstraint(
                condition=Q(status='completed') & Q(booked_slot_start_utc__isnull=True),
                fields=('product', 'buyer_email'),
                name='storepurchase_unique_completed_file_link',
            ),
        ),
        migrations.AddConstraint(
            model_name='storepurchase',
            constraint=models.UniqueConstraint(
                condition=Q(status='completed') & Q(booked_slot_start_utc__isnull=False),
                fields=('product', 'buyer_email', 'booked_slot_start_utc'),
                name='storepurchase_unique_completed_meeting_slot',
            ),
        ),
    ]
