from django.db import migrations, models


def _backfill_storepurchase_buyer_user(apps, schema_editor):
    StorePurchase = apps.get_model('community_store', 'StorePurchase')
    User = apps.get_model('account', 'User')

    null_rows = StorePurchase.objects.filter(buyer_user__isnull=True).only('id', 'buyer_email')
    unresolved_ids = []
    for row in null_rows.iterator(chunk_size=500):
        email = (row.buyer_email or '').strip()
        if not email:
            unresolved_ids.append(row.id)
            continue
        user = User.objects.filter(email__iexact=email).only('id').first()
        if not user:
            unresolved_ids.append(row.id)
            continue
        row.buyer_user_id = user.id
        row.save(update_fields=['buyer_user'])

    if unresolved_ids:
        sample = ', '.join(str(i) for i in unresolved_ids[:10])
        raise RuntimeError(
            'Cannot enforce NOT NULL on StorePurchase.buyer_user. '
            f'{len(unresolved_ids)} rows could not be mapped by buyer_email (sample ids: {sample}). '
            'Backfill/delete these rows, then re-run migrations.'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0010_storepurchase_unique_constraints_split'),
    ]

    operations = [
        migrations.RunPython(_backfill_storepurchase_buyer_user, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='storepurchase',
            name='buyer_user',
            field=models.ForeignKey(
                help_text='Logged-in buyer',
                on_delete=models.deletion.PROTECT,
                related_name='store_purchases',
                to='account.user',
            ),
        ),
    ]
