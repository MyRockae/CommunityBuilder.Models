from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0024_remove_communitygroup_legacy_billing_flags'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaderboardPointAward',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_key', models.CharField(db_index=True, max_length=64)),
                ('source_id', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'community_member',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='leaderboard_point_awards',
                        to='community.communitymember',
                    ),
                ),
            ],
            options={
                'db_table': 'LeaderboardPointAward',
            },
        ),
        migrations.CreateModel(
            name='LeaderboardChatDailyCounter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('award_date', models.DateField(db_index=True)),
                ('award_count', models.PositiveSmallIntegerField(default=0)),
                (
                    'community_member',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='leaderboard_chat_daily_counters',
                        to='community.communitymember',
                    ),
                ),
            ],
            options={
                'db_table': 'LeaderboardChatDailyCounter',
            },
        ),
        migrations.AddConstraint(
            model_name='leaderboardpointaward',
            constraint=models.UniqueConstraint(
                fields=('community_member', 'action_key', 'source_id'),
                name='uniq_leaderboard_point_award_member_action_source',
            ),
        ),
        migrations.AddConstraint(
            model_name='leaderboardchatdailycounter',
            constraint=models.UniqueConstraint(
                fields=('community_member', 'award_date'),
                name='uniq_leaderboard_chat_daily_member_date',
            ),
        ),
    ]
