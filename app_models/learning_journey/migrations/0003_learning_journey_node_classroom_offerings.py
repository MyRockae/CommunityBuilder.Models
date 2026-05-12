# Generated manually: node targets collection XOR classroom + offerings JSON.

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom', '0010_dense_classroom_collection_item_order'),
        ('learning_journey', '0002_rename_learningjourney_community_idx_learningjou_communi_96deef_idx_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='learningjourneynode',
            name='uniq_learningjourneynode_journey_collection',
        ),
        migrations.AddField(
            model_name='learningjourneynode',
            name='classroom',
            field=models.ForeignKey(
                blank=True,
                help_text='Single classroom for this stage (mutually exclusive with classroom_collection)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='learning_journey_nodes',
                to='community_classroom.classroom',
            ),
        ),
        migrations.AddField(
            model_name='learningjourneynode',
            name='offerings',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Owner-defined perks/copy for this stage (e.g. bullets, headline)',
            ),
        ),
        migrations.AlterField(
            model_name='learningjourneynode',
            name='classroom_collection',
            field=models.ForeignKey(
                blank=True,
                help_text='Course bundle for this stage (mutually exclusive with classroom)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='learning_journey_nodes',
                to='community_classroom.classroomcollection',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.CheckConstraint(
                condition=(
                    Q(classroom_collection__isnull=False, classroom__isnull=True)
                    | Q(classroom_collection__isnull=True, classroom__isnull=False)
                ),
                name='learning_journey_node_target_xor',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.UniqueConstraint(
                condition=Q(classroom_collection__isnull=False),
                fields=('journey', 'classroom_collection'),
                name='uniq_ljnode_journey_collection',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.UniqueConstraint(
                condition=Q(classroom__isnull=False),
                fields=('journey', 'classroom'),
                name='uniq_ljnode_journey_classroom',
            ),
        ),
    ]
