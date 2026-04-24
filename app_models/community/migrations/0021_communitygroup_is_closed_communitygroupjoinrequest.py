# Generated manually for CommunityGroup.is_closed + CommunityGroupJoinRequest

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('community', '0020_communitysettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='communitygroup',
            name='is_closed',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'If true, self-serve subscribe requires an approved CommunityGroupJoinRequest for this tier; '
                    'legacy members with CommunityGroupAccess may auto-approve on subscribe per payment rules.'
                ),
            ),
        ),
        migrations.CreateModel(
            name='CommunityGroupJoinRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('approved', 'Approved'),
                        ('rejected', 'Rejected'),
                        ('cancelled', 'Cancelled'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('message', models.TextField(blank=True, help_text='Optional note from the member', null=True)),
                ('source', models.CharField(
                    blank=True,
                    help_text='Optional audit tag (e.g. owner_grant, subscribe_auto_legacy)',
                    max_length=64,
                    null=True,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                (
                    'community',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='community_group_join_requests',
                        to='community.community',
                    ),
                ),
                (
                    'community_group',
                    models.ForeignKey(
                        help_text='Tier this request applies to; CASCADE removes requests when the tier is hard-deleted.',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='join_requests',
                        to='community.communitygroup',
                    ),
                ),
                (
                    'resolved_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='Owner/co-owner who approved or rejected; null for system-created rows',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='resolved_community_group_join_requests',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='community_group_join_requests',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'Community group join request',
                'verbose_name_plural': 'Community group join requests',
                'db_table': 'CommunityGroupJoinRequest',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='communitygroupjoinrequest',
            index=models.Index(fields=['community_group', 'status'], name='cgjoinreq_grp_status_idx'),
        ),
        migrations.AddIndex(
            model_name='communitygroupjoinrequest',
            index=models.Index(fields=['user', 'community_group'], name='cgjoinreq_user_grp_idx'),
        ),
    ]
