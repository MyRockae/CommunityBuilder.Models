# Generated manually for Member Engagement Service (MES) telemetry.

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_roles_permissions_and_user_roles'),
        ('community', '0024_remove_communitygroup_legacy_billing_flags'),
        ('community_classroom', '0010_dense_classroom_collection_item_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngagementSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('client_session_key', models.CharField(help_text='Opaque client-generated session id (per tab).', max_length=64)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen_at', models.DateTimeField(auto_now=True)),
                ('user_agent', models.CharField(blank=True, max_length=512, null=True)),
                (
                    'classroom',
                    models.ForeignKey(
                        blank=True,
                        help_text='Classroom context when tracking classroom surfaces; null for community-only events.',
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='engagement_sessions',
                        to='community_classroom.classroom',
                    ),
                ),
                (
                    'community',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='engagement_sessions',
                        to='community.community',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='engagement_sessions',
                        to='account.user',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Engagement session',
                'verbose_name_plural': 'Engagement sessions',
                'db_table': 'EngagementSession',
            },
        ),
        migrations.CreateModel(
            name='EngagementEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('occurred_at_client', models.DateTimeField(blank=True, null=True)),
                ('received_at', models.DateTimeField(auto_now_add=True)),
                (
                    'surface',
                    models.CharField(
                        choices=[
                            ('classroom_home', 'Classroom home'),
                            ('lesson', 'Lesson'),
                            ('content', 'Content'),
                            ('material', 'Material'),
                            ('video', 'Video'),
                        ],
                        max_length=32,
                    ),
                ),
                ('resource_type', models.CharField(blank=True, max_length=64, null=True)),
                ('resource_id', models.CharField(blank=True, max_length=64, null=True)),
                ('event_type', models.CharField(max_length=32)),
                ('duration_ms', models.PositiveIntegerField(blank=True, null=True)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('idempotency_key', models.CharField(max_length=128, unique=True)),
                (
                    'session',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='events',
                        to='member_engagement.engagementsession',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Engagement event',
                'verbose_name_plural': 'Engagement events',
                'db_table': 'EngagementEvent',
            },
        ),
        migrations.AddConstraint(
            model_name='engagementsession',
            constraint=models.UniqueConstraint(
                fields=('user', 'community', 'client_session_key'),
                name='uniq_engagementsession_user_community_clientkey',
            ),
        ),
        migrations.AddIndex(
            model_name='engagementsession',
            index=models.Index(fields=['community', 'classroom', '-last_seen_at'], name='engsess_comm_cl_last_idx'),
        ),
        migrations.AddIndex(
            model_name='engagementsession',
            index=models.Index(fields=['user', '-last_seen_at'], name='engsess_user_last_idx'),
        ),
        migrations.AddIndex(
            model_name='engagementevent',
            index=models.Index(fields=['session', 'received_at'], name='engevent_sess_recv_idx'),
        ),
    ]
