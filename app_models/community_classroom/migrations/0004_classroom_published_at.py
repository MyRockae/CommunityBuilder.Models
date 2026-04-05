from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community_classroom', '0003_alter_classroom_payment_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='published_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set once when the classroom is first published; remains set if is_published is toggled off so downstream notifications fire only once.',
                null=True,
            ),
        ),
    ]
