from django.db import migrations, models
import django.db.models.deletion


def seed_usd_prices_from_legacy_fee(apps, schema_editor):
    CommunityGroup = apps.get_model('community', 'CommunityGroup')
    CommunityGroupPrice = apps.get_model('community', 'CommunityGroupPrice')
    for g in CommunityGroup.objects.filter(is_free=False):
        fee = g.fee
        if fee is None or fee == 0:
            continue
        CommunityGroupPrice.objects.update_or_create(
            community_group=g,
            currency='USD',
            defaults={'amount': fee},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0013_alter_communitygroupaccess_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityGroupPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(help_text='ISO 4217 code (e.g. USD, NGN, GHS, ZAR)', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, help_text='Fee in major units of this currency', max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community_group',
                    models.ForeignKey(
                        help_text='Community group tier this price applies to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='prices',
                        to='community.communitygroup',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Community group price',
                'verbose_name_plural': 'Community group prices',
                'db_table': 'CommunityGroupPrice',
            },
        ),
        migrations.AddConstraint(
            model_name='communitygroupprice',
            constraint=models.UniqueConstraint(fields=('community_group', 'currency'), name='commgroupprice_unique_group_currency'),
        ),
        migrations.RunPython(seed_usd_prices_from_legacy_fee, noop_reverse),
        migrations.AlterField(
            model_name='communitygroup',
            name='fee',
            field=models.DecimalField(
                decimal_places=2,
                help_text='Legacy fee (kept for admin/list UX); canonical per-currency amounts live on CommunityGroupPrice',
                max_digits=10,
            ),
        ),
    ]
