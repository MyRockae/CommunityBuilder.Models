from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('community_resource', '0005_resourcecontent_order_resource_type_thumbnail'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='resource',
                    name='payment_plans',
                    field=models.ManyToManyField(
                        blank=True,
                        help_text='Community groups (tiers) that have access to this resource. Zero or many.',
                        related_name='resources',
                        to='community.communitygroup',
                    ),
                ),
            ],
        ),
    ]
