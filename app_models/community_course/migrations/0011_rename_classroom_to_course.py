# Rename Classroom* models/tables/fields to Course* / CourseBundle*.
#
# Existing databases: BEFORE migrate, remap Django's app labels:
#   UPDATE django_migrations SET app = 'community_course' WHERE app = 'community_classroom';
#   UPDATE django_migrations SET app = 'community_course_content' WHERE app = 'community_classroom_content';
#   UPDATE django_content_type SET app_label = 'community_course' WHERE app_label = 'community_classroom';
#   UPDATE django_content_type SET app_label = 'community_course_content' WHERE app_label = 'community_classroom_content';
# See CommunityBuilder.DataMigration/pre_migrate_rename_classroom_apps.sql
# Fresh databases skip that SQL; 0001–0010 still create Classroom* then this migration renames them.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0010_dense_classroom_collection_item_order'),
        ('community', '0024_remove_communitygroup_legacy_billing_flags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name='Classroom', new_name='Course'),
        migrations.RenameModel(old_name='ClassroomReview', new_name='CourseReview'),
        migrations.RenameModel(old_name='ClassroomCollection', new_name='CourseBundle'),
        migrations.RenameModel(old_name='ClassroomCollectionItem', new_name='CourseBundleItem'),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-created_at'], 'verbose_name': 'Course', 'verbose_name_plural': 'Courses'},
        ),
        migrations.AlterModelOptions(
            name='coursereview',
            options={'ordering': ['-created_at'], 'verbose_name': 'Course Review', 'verbose_name_plural': 'Course Reviews'},
        ),
        migrations.AlterModelOptions(
            name='coursebundle',
            options={'ordering': ['-created_at'], 'verbose_name': 'Course Bundle', 'verbose_name_plural': 'Course Bundles'},
        ),
        migrations.AlterModelOptions(
            name='coursebundleitem',
            options={'ordering': ['order', 'id'], 'verbose_name': 'Course Bundle Item', 'verbose_name_plural': 'Course Bundle Items'},
        ),
        migrations.AlterField(
            model_name='course',
            name='community',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='courses',
                to='community.community',
            ),
        ),
        migrations.AlterField(
            model_name='course',
            name='community_groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='Community groups (tiers) that have access to this course',
                related_name='courses',
                to='community.communitygroup',
            ),
        ),
        migrations.RenameField(model_name='coursereview', old_name='classroom', new_name='course'),
        migrations.AlterUniqueTogether(name='coursereview', unique_together={('user', 'course')}),
        migrations.AlterField(
            model_name='coursereview',
            name='user',
            field=models.ForeignKey(
                help_text='User who left the review',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='course_reviews',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='coursebundle',
            name='community',
            field=models.ForeignKey(
                help_text='Community this bundle belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='course_bundles',
                to='community.community',
            ),
        ),
        migrations.RenameField(model_name='coursebundleitem', old_name='classroom', new_name='course'),
        migrations.RenameField(model_name='coursebundleitem', old_name='collection', new_name='bundle'),
        migrations.RemoveConstraint(
            model_name='coursebundleitem',
            name='uniq_classroomcollectionitem_collection_classroom',
        ),
        migrations.AddConstraint(
            model_name='coursebundleitem',
            constraint=models.UniqueConstraint(
                fields=('bundle', 'course'),
                name='uniq_coursebundleitem_bundle_course',
            ),
        ),
        migrations.AlterField(
            model_name='coursebundleitem',
            name='course',
            field=models.ForeignKey(
                help_text='Course placed in the bundle',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='bundle_items',
                to='community_course.course',
            ),
        ),
        migrations.AlterField(
            model_name='coursebundleitem',
            name='bundle',
            field=models.ForeignKey(
                help_text='Bundle this row belongs to',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='community_course.coursebundle',
            ),
        ),
        migrations.RemoveIndex(model_name='coursereview', name='ClassroomRe_classro_d01c7a_idx'),
        migrations.RemoveIndex(model_name='coursereview', name='ClassroomRe_user_id_b4e024_idx'),
        migrations.AddIndex(
            model_name='coursereview',
            index=models.Index(fields=['course'], name='coursereview_course_idx'),
        ),
        migrations.AddIndex(
            model_name='coursereview',
            index=models.Index(fields=['user', 'course'], name='coursereview_user_course_idx'),
        ),
        migrations.RemoveIndex(model_name='coursebundleitem', name='ClassroomCo_collect_0cf7dd_idx'),
        migrations.AddIndex(
            model_name='coursebundleitem',
            index=models.Index(fields=['bundle', 'order'], name='cbi_bundle_order_idx'),
        ),
    ]
