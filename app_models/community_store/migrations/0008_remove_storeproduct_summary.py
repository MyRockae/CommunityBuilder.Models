# Generated manually for community store cleanup

from django.db import migrations


def merge_summary_into_description(apps, schema_editor):
    StoreProduct = apps.get_model('community_store', 'StoreProduct')
    for p in StoreProduct.objects.iterator():
        desc = (p.description or '').strip()
        summ = (getattr(p, 'summary', None) or '').strip()
        if not desc and summ:
            p.description = summ
            p.save(update_fields=['description'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community_store', '0007_rename_storeownera_setting_idx_storeownera_setting_53b679_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(merge_summary_into_description, noop_reverse),
        migrations.RemoveField(
            model_name='storeproduct',
            name='summary',
        ),
    ]
