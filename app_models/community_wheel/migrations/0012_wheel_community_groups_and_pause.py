# Adds community group (tier) scoping and pause support to Wheel.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('community_wheel', '0011_remove_wheel_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='wheel',
            name='community_groups',
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    'Community groups (tiers) that have access to this wheel. '
                    'Owners and co-owners have access regardless of tier.'
                ),
                related_name='wheels',
                to='community.communitygroup',
            ),
        ),
        migrations.AddField(
            model_name='wheel',
            name='paused_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the wheel was paused; null while it is running.',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='wheel',
            name='round_paused_seconds',
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    'Seconds the current round has spent paused. Added to the round deadline; '
                    'reset when a round completes.'
                ),
            ),
        ),
        migrations.AlterField(
            model_name='wheel',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('open_for_join', 'Open for Join'),
                    ('in_progress', 'In Progress'),
                    ('paused', 'Paused'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                db_index=True,
                default='draft',
                max_length=20,
            ),
        ),
    ]
