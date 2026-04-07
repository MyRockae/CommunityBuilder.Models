from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0002_payoutprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='payoutprofile',
            name='legal_full_name',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Legal name as shown on tax or bank documents',
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name='payoutprofile',
            name='tax_id',
            field=models.CharField(
                blank=True,
                help_text='Tax identifier (e.g. EIN, VAT, SSN format varies by jurisdiction)',
                max_length=64,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='payoutprofile',
            name='identity_document_number',
            field=models.CharField(
                blank=True,
                help_text='Government-issued ID number (national ID, passport, etc.) for KYC / payout verification',
                max_length=64,
                null=True,
            ),
        ),
    ]
