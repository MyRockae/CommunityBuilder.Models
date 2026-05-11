# Generated manually — data migration: dense 0..n-1 order per collection.

from django.db import migrations


def dense_collection_item_orders(apps, schema_editor):
    ClassroomCollection = apps.get_model('community_classroom', 'ClassroomCollection')
    ClassroomCollectionItem = apps.get_model('community_classroom', 'ClassroomCollectionItem')

    for collection_id in ClassroomCollection.objects.values_list('id', flat=True):
        items = list(
            ClassroomCollectionItem.objects.filter(collection_id=collection_id).order_by('order', 'id')
        )
        to_update = []
        for idx, row in enumerate(items):
            if row.order != idx:
                row.order = idx
                to_update.append(row)
        if to_update:
            ClassroomCollectionItem.objects.bulk_update(to_update, ['order'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom', '0009_rename_classroomco_communi_7e8b2e_idx_classroomco_communi_13e0d2_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(dense_collection_item_orders, noop_reverse),
    ]
