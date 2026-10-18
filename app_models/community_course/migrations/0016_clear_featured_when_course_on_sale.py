"""Prefer sale over preview when a course is both featured and actively listed for sale.

Keeps placement is_preview flags as sale sample lessons. Clears is_featured only.
"""

from django.db import migrations
from django.db.models import Exists, OuterRef


def clear_featured_for_active_sale_courses(apps, schema_editor):
    Course = apps.get_model('community_course', 'Course')
    StoreProduct = apps.get_model('community_store', 'StoreProduct')

    active_sale = StoreProduct.objects.filter(
        course_id=OuterRef('pk'),
        product_kind='course',
        is_active=True,
        store__is_active=True,
    )
    (
        Course.objects.filter(is_featured=True)
        .filter(Exists(active_sale))
        .update(is_featured=False)
    )


def noop_reverse(apps, schema_editor):
    # Cannot safely restore featured flags.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('community_course', '0015_course_public_preview_scope'),
        ('community_store', '0017_storeproduct_course_buyer_audience'),
    ]

    operations = [
        migrations.RunPython(clear_featured_for_active_sale_courses, noop_reverse),
    ]
