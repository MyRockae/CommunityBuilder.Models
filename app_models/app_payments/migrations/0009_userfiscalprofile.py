# Generated manually for UserFiscalProfile rename + identity_document_type

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0008_rename_paymenttran_event_r_6194a6_idx_paymenttran_event_r_9ed163_idx'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payoutprofile',
            name='preferred_payment_gateway',
        ),
        migrations.AddField(
            model_name='payoutprofile',
            name='identity_document_type',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Document type for KYC (e.g. passport, national_id, drivers_license)',
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name='payoutprofile',
            name='user',
            field=models.OneToOneField(
                help_text='User this fiscal profile belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='fiscal_profile',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RenameModel(
            old_name='PayoutProfile',
            new_name='UserFiscalProfile',
        ),
        migrations.AlterModelOptions(
            name='userfiscalprofile',
            options={
                'verbose_name': 'User fiscal profile',
                'verbose_name_plural': 'User fiscal profiles',
            },
        ),
        migrations.AlterModelTable(
            name='userfiscalprofile',
            table='UserFiscalProfile',
        ),
    ]
