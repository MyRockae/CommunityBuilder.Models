from django.db import migrations, models


def forwards_billing_flags(apps, schema_editor):
    CommunityGroup = apps.get_model('community', 'CommunityGroup')
    CommunityGroupPrice = apps.get_model('community', 'CommunityGroupPrice')
    for g in CommunityGroup.objects.all():
        has_paid = CommunityGroupPrice.objects.filter(community_group=g, amount__gt=0).exists()
        if not has_paid:
            g.is_monthly = False
            g.is_yearly = False
            g.is_lifetime = False
        elif g.is_recurring:
            g.is_monthly = True
            g.is_yearly = False
            g.is_lifetime = False
        else:
            g.is_monthly = False
            g.is_yearly = True
            g.is_lifetime = False
        g.save(
            update_fields=[
                'is_monthly',
                'is_yearly',
                'is_lifetime',
            ]
        )


def backwards_billing_flags(apps, schema_editor):
    CommunityGroup = apps.get_model('community', 'CommunityGroup')
    for g in CommunityGroup.objects.all():
        g.is_recurring = bool(g.is_monthly)
        g.save(update_fields=['is_recurring'])


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0016_remove_communitygroup_is_free'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitygroup',
            name='is_monthly',
            field=models.BooleanField(
                default=False,
                help_text='Member is charged each billing month (recurring; payment service must enforce)',
            ),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='is_yearly',
            field=models.BooleanField(
                default=False,
                help_text='Member is charged each billing year (recurring; payment service must enforce)',
            ),
        ),
        migrations.AddField(
            model_name='communitygroup',
            name='is_lifetime',
            field=models.BooleanField(
                default=False,
                help_text='One purchase: no further charges; access does not expire by period (expires_at null)',
            ),
        ),
        migrations.RunPython(forwards_billing_flags, backwards_billing_flags),
        migrations.RemoveField(
            model_name='communitygroup',
            name='is_recurring',
        ),
    ]
