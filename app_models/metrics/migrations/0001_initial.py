# Generated manually for UserMetricRollup

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0001_initial'),
        ('community', '0024_remove_communitygroup_legacy_billing_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMetricRollup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('metric_key', models.CharField(db_index=True, help_text='Stable metric identifier (e.g. likes_given, likes_received)', max_length=64)),
                ('value', models.BigIntegerField(default=0)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community', models.ForeignKey(blank=True, help_text='Null for platform-wide metrics; set for community-scoped metrics', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_metric_rollups', to='community.community')),
                ('user', models.ForeignKey(help_text='User this metric applies to', on_delete=django.db.models.deletion.CASCADE, related_name='metric_rollups', to='account.user')),
            ],
            options={
                'verbose_name': 'User metric rollup',
                'verbose_name_plural': 'User metric rollups',
                'db_table': 'UserMetricRollup',
            },
        ),
        migrations.AddIndex(
            model_name='usermetricrollup',
            index=models.Index(fields=['community', 'metric_key', '-value'], name='user_metric_rollup_leader_idx'),
        ),
        migrations.AddIndex(
            model_name='usermetricrollup',
            index=models.Index(fields=['user', 'metric_key'], name='umrollup_user_key_idx'),
        ),
        migrations.AddConstraint(
            model_name='usermetricrollup',
            constraint=models.UniqueConstraint(
                condition=Q(community__isnull=True),
                fields=('user', 'metric_key'),
                name='user_metric_rollup_global_uq',
            ),
        ),
        migrations.AddConstraint(
            model_name='usermetricrollup',
            constraint=models.UniqueConstraint(
                condition=Q(community__isnull=False),
                fields=('user', 'community', 'metric_key'),
                name='user_metric_rollup_scoped_uq',
            ),
        ),
    ]
