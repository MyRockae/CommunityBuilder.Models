from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0003_payoutprofile_legal_tax_identity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payoutprofile',
            name='identity_document_number',
            field=models.CharField(
                blank=True,
                help_text='Hashed government ID number for KYC; never store plaintext',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='payoutprofile',
            name='tax_id',
            field=models.CharField(
                blank=True,
                help_text='Hashed tax identifier (e.g. EIN, VAT); never store plaintext',
                max_length=255,
                null=True,
            ),
        ),
    ]
