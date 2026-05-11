# Generated manually for Learning Journey (DAG of course bundles).

import uuid

import django
import django.db.models.deletion
from django.db import migrations, models
from django.db.models import F, Q


def _edge_no_self_loop_constraint():
    q = ~Q(from_node=F('to_node'))
    if django.VERSION >= (5, 0):
        return models.CheckConstraint(condition=q, name='learning_journey_edge_no_self_loop')
    return models.CheckConstraint(check=q, name='learning_journey_edge_no_self_loop')


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_roles_permissions_and_user_roles'),
        ('community', '0024_remove_communitygroup_legacy_billing_flags'),
        ('community_classroom', '0010_dense_classroom_collection_item_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningJourney',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('banner_url', models.URLField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False, help_text='Visible to members when True')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'community',
                    models.ForeignKey(
                        help_text='Community this journey belongs to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='learning_journeys',
                        to='community.community',
                    ),
                ),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        help_text='Owner/co-owner who created the journey',
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='learning_journeys_created',
                        to='account.user',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Learning Journey',
                'verbose_name_plural': 'Learning Journeys',
                'db_table': 'LearningJourney',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='LearningJourneyNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'stable_id',
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text='Stable identity for API graph replace operations',
                    ),
                ),
                (
                    'classroom_collection',
                    models.ForeignKey(
                        help_text='Course bundle represented by this node',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='learning_journey_nodes',
                        to='community_classroom.classroomcollection',
                    ),
                ),
                (
                    'journey',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='nodes',
                        to='learning_journey.learningjourney',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Learning Journey Node',
                'verbose_name_plural': 'Learning Journey Nodes',
                'db_table': 'LearningJourneyNode',
            },
        ),
        migrations.CreateModel(
            name='LearningJourneyEdge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'from_node',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='out_edges',
                        to='learning_journey.learningjourneynode',
                    ),
                ),
                (
                    'journey',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='edges',
                        to='learning_journey.learningjourney',
                    ),
                ),
                (
                    'to_node',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='in_edges',
                        to='learning_journey.learningjourneynode',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Learning Journey Edge',
                'verbose_name_plural': 'Learning Journey Edges',
                'db_table': 'LearningJourneyEdge',
            },
        ),
        migrations.CreateModel(
            name='LearningJourneyEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                (
                    'community_member',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='learning_journey_enrollments',
                        to='community.communitymember',
                    ),
                ),
                (
                    'journey',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='enrollments',
                        to='learning_journey.learningjourney',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Learning Journey Enrollment',
                'verbose_name_plural': 'Learning Journey Enrollments',
                'db_table': 'LearningJourneyEnrollment',
            },
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.UniqueConstraint(
                fields=('journey', 'classroom_collection'),
                name='uniq_learningjourneynode_journey_collection',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneyedge',
            constraint=models.UniqueConstraint(
                fields=('journey', 'from_node', 'to_node'),
                name='uniq_learningjourneyedge_journey_from_to',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneyedge',
            constraint=_edge_no_self_loop_constraint(),
        ),
        migrations.AddConstraint(
            model_name='learningjourneyenrollment',
            constraint=models.UniqueConstraint(
                fields=('journey', 'community_member'),
                name='uniq_learningjourneyenrollment_journey_member',
            ),
        ),
        migrations.AddIndex(
            model_name='learningjourney',
            index=models.Index(fields=['community'], name='LearningJourney_community_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourney',
            index=models.Index(fields=['community', 'is_published'], name='LearningJourney_communi_e85470_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneynode',
            index=models.Index(fields=['journey'], name='LearningJourneyNode_journey_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneyedge',
            index=models.Index(fields=['journey'], name='LearningJourneyEdge_journey_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneyedge',
            index=models.Index(fields=['from_node'], name='LearningJourneyEdge_from_node_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneyedge',
            index=models.Index(fields=['to_node'], name='LearningJourneyEdge_to_node_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneyenrollment',
            index=models.Index(fields=['journey'], name='LearningJourneyEnrollment_journey_idx'),
        ),
        migrations.AddIndex(
            model_name='learningjourneyenrollment',
            index=models.Index(
                fields=['community_member'],
                name='LearningJourneyEnrollment_member_idx',
            ),
        ),
    ]
