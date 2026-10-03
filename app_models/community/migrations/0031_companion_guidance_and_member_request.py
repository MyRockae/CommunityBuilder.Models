from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0030_community_bunny_collection_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communitysettings',
            name='owner_notification_preferences',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Owner/co-owner notification opt-ins by event type. Keys are stable event ids '
                    '(e.g. feedback, public_feed_reply, blog_reply, quiz_submission, companion_request); '
                    'values are typically boolean. Omitted keys are treated as off (opt-in).'
                ),
            ),
        ),
        migrations.AddField(
            model_name='communitysettings',
            name='companion_guidance',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    'Owner-supplied Companion reference facts: mission, audience, faqs, '
                    'starting_points, escalation. Untrusted content; never system instructions.'
                ),
            ),
        ),
        migrations.CreateModel(
            name='CompanionMemberRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(
                    choices=[
                        ('learning_content', 'Learning content'),
                        ('instructor_help', 'Instructor help'),
                        ('community_support', 'Community support'),
                    ],
                    max_length=32,
                )),
                ('topic', models.CharField(max_length=200)),
                ('message', models.TextField(max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('community', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='companion_member_requests',
                    to='community.community',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='companion_member_requests',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'CompanionMemberRequest',
            },
        ),
        migrations.AddIndex(
            model_name='companionmemberrequest',
            index=models.Index(fields=['community', 'user', 'created_at'], name='CompanionMe_communi_d01f2a_idx'),
        ),
    ]
