from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q

from app_models.account.referral_code import allocate_referral_code


def forwards_fill_referral_codes(apps, schema_editor):
    User = apps.get_model('account', 'User')
    qs = User.objects.filter(Q(referral_code__isnull=True) | Q(referral_code=''))
    for user in qs.iterator(chunk_size=500):
        user.referral_code = allocate_referral_code(User)
        user.save(update_fields=['referral_code'])


def backwards_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_user_token_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.CharField(
                help_text='Public referral code used in ?ref= links. Not the username.',
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='referred_by',
            field=models.ForeignKey(
                blank=True,
                help_text='Platform referrer (set once at signup). Analytics only.',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referrals',
                to='account.user',
            ),
        ),
        migrations.RunPython(forwards_fill_referral_codes, backwards_noop),
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.CharField(
                db_index=True,
                help_text='Public referral code used in ?ref= links. Not the username.',
                max_length=10,
                unique=True,
            ),
        ),
    ]
