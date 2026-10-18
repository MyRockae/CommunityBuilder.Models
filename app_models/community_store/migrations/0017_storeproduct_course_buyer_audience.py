# Generated manually for course-for-sale + buyer_audience

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_course', '0015_course_public_preview_scope'),
        ('community_store', '0016_delete_storeguestemailchallenge'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeproduct',
            name='buyer_audience',
            field=models.CharField(
                choices=[
                    ('anyone', 'Anyone'),
                    ('members', 'Community members only'),
                    ('non_members', 'Non-members only'),
                ],
                db_index=True,
                default='anyone',
                help_text='Who may purchase this product: anyone, members, or non_members',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='storeproduct',
            name='course',
            field=models.ForeignKey(
                blank=True,
                help_text='Course unlocked by this product when product_kind is course',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='store_products',
                to='community_course.course',
            ),
        ),
        migrations.AlterField(
            model_name='storeproduct',
            name='product_kind',
            field=models.CharField(
                choices=[
                    ('file', 'File download'),
                    ('link', 'External link'),
                    ('meeting', 'Bookable meeting'),
                    ('course', 'Course'),
                ],
                db_index=True,
                default='file',
                help_text='How the product is delivered after purchase',
                max_length=20,
            ),
        ),
        migrations.AddIndex(
            model_name='storeproduct',
            index=models.Index(
                fields=['course', 'is_active'],
                name='storeproduct_course_active_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='storeproduct',
            constraint=models.UniqueConstraint(
                condition=models.Q(course__isnull=False, product_kind='course'),
                fields=('store', 'course'),
                name='storeproduct_unique_store_course',
            ),
        ),
    ]
