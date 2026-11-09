import django
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


def forwards_clear_stub_earnings(apps, schema_editor):
    UserEarning = apps.get_model('app_payments', 'UserEarning')
    UserEarning.objects.all().delete()


def _userearning_kind_subject_check_constraint():
    q = (
        Q(kind='community_group', community_group__isnull=False, store_product__isnull=True)
        | Q(kind='store_product', store_product__isnull=False, community_group__isnull=True)
    )
    name = 'userearning_kind_matches_subject'
    if django.VERSION >= (5, 2):
        return models.CheckConstraint(condition=q, name=name)
    return models.CheckConstraint(check=q, name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('app_payments', '0013_userearning'),
        ('app_subscription', '0023_learning_companion_all_tiers'),
        ('community', '0035_referral_stamps_and_group_bonus'),
        ('community_store', '0018_referral_bonus_and_purchase_referrer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(forwards_clear_stub_earnings, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='userearning',
            name='kind',
        ),
        migrations.AddField(
            model_name='userearning',
            name='kind',
            field=models.CharField(
                choices=[
                    ('community_group', 'Community group'),
                    ('store_product', 'Store product'),
                ],
                help_text='How this credit was earned',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='status',
            field=models.CharField(
                choices=[('owed', 'Owed'), ('cancelled', 'Cancelled')],
                default='owed',
                help_text='owed until paid out or cancelled on refund before transfer',
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='percent_snapshot',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Referral percent applied when this earning was created',
                max_digits=5,
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='payment_transaction',
            field=models.OneToOneField(
                help_text='Succeeded charge this commission was calculated from',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='referral_earning',
                to='app_payments.paymenttransaction',
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='referred_user',
            field=models.ForeignKey(
                help_text='Member or buyer whose payment generated this credit',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='referral_earnings_as_buyer',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='community',
            field=models.ForeignKey(
                help_text='Community the referred payment belonged to',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='referral_earnings',
                to='community.community',
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='community_group',
            field=models.ForeignKey(
                blank=True,
                help_text='Set when kind is community_group',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referral_earnings',
                to='community.communitygroup',
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='store_product',
            field=models.ForeignKey(
                blank=True,
                help_text='Set when kind is store_product',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referral_earnings',
                to='community_store.storeproduct',
            ),
        ),
        migrations.AddField(
            model_name='userearning',
            name='community_member_subscription',
            field=models.ForeignKey(
                blank=True,
                help_text='Group subscription this commission is tied to (first payment only)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referral_earnings',
                to='app_subscription.communitymembersubscription',
            ),
        ),
        migrations.AlterField(
            model_name='userearning',
            name='percent_snapshot',
            field=models.DecimalField(
                decimal_places=2,
                help_text='Referral percent applied when this earning was created',
                max_digits=5,
            ),
        ),
        migrations.AlterField(
            model_name='userearning',
            name='payment_transaction',
            field=models.OneToOneField(
                help_text='Succeeded charge this commission was calculated from',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='referral_earning',
                to='app_payments.paymenttransaction',
            ),
        ),
        migrations.AlterField(
            model_name='userearning',
            name='referred_user',
            field=models.ForeignKey(
                help_text='Member or buyer whose payment generated this credit',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='referral_earnings_as_buyer',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='userearning',
            name='community',
            field=models.ForeignKey(
                help_text='Community the referred payment belonged to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='referral_earnings',
                to='community.community',
            ),
        ),
        migrations.AddConstraint(
            model_name='userearning',
            constraint=_userearning_kind_subject_check_constraint(),
        ),
        migrations.AddConstraint(
            model_name='userearning',
            constraint=models.UniqueConstraint(
                condition=Q(community_member_subscription__isnull=False),
                fields=('community_member_subscription',),
                name='userearning_unique_group_subscription',
            ),
        ),
    ]
