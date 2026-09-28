import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0011_rename_classroom_to_course'),
        ('learning_journey', '0004_learningjourneynode_layout_coords'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='learningjourneynode',
            name='learning_journey_node_target_xor',
        ),
        migrations.RemoveConstraint(
            model_name='learningjourneynode',
            name='uniq_ljnode_journey_collection',
        ),
        migrations.RemoveConstraint(
            model_name='learningjourneynode',
            name='uniq_ljnode_journey_classroom',
        ),
        migrations.RenameField(
            model_name='learningjourneynode',
            old_name='classroom',
            new_name='course',
        ),
        migrations.RenameField(
            model_name='learningjourneynode',
            old_name='classroom_collection',
            new_name='course_bundle',
        ),
        migrations.AlterField(
            model_name='learningjourneynode',
            name='course',
            field=models.ForeignKey(
                blank=True,
                help_text='Single course for this stage (mutually exclusive with course_bundle)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='learning_journey_nodes',
                to='community_course.course',
            ),
        ),
        migrations.AlterField(
            model_name='learningjourneynode',
            name='course_bundle',
            field=models.ForeignKey(
                blank=True,
                help_text='Course bundle for this stage (mutually exclusive with course)',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='learning_journey_nodes',
                to='community_course.coursebundle',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.CheckConstraint(
                condition=(
                    Q(course_bundle__isnull=False, course__isnull=True)
                    | Q(course_bundle__isnull=True, course__isnull=False)
                ),
                name='learning_journey_node_target_xor',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.UniqueConstraint(
                condition=Q(course_bundle__isnull=False),
                fields=('journey', 'course_bundle'),
                name='uniq_ljnode_journey_bundle',
            ),
        ),
        migrations.AddConstraint(
            model_name='learningjourneynode',
            constraint=models.UniqueConstraint(
                condition=Q(course__isnull=False),
                fields=('journey', 'course'),
                name='uniq_ljnode_journey_course',
            ),
        ),
    ]
