# DB: rename AppSubscriptionTier limit columns. State: tier + CommunityMemberSubscription FK (DB column renamed in community.0011).

from typing import Optional

import django.db.models.deletion
from django.db import migrations, models


def _table_exists(schema_editor, table: str) -> bool:
    with schema_editor.connection.cursor() as cursor:
        return table in schema_editor.connection.introspection.table_names(cursor)


def _column_names(schema_editor, table: str) -> dict:
    with schema_editor.connection.cursor() as cursor:
        return {
            c.name.lower(): c.name
            for c in schema_editor.connection.introspection.get_table_description(
                cursor, table
            )
        }


def _resolve_column(cols: dict, want: str) -> Optional[str]:
    return cols.get(want.lower())


def _rename_column(schema_editor, table: str, old: str, new: str) -> None:
    if not _table_exists(schema_editor, table):
        return
    cols = _column_names(schema_editor, table)
    old_actual = _resolve_column(cols, old)
    if old_actual is None or _resolve_column(cols, new) is not None:
        return
    vendor = schema_editor.connection.vendor
    qn = schema_editor.connection.ops.quote_name
    if vendor == 'microsoft':
        schema_editor.execute(
            "EXEC sp_rename N'%s.%s', N'%s', N'COLUMN'"
            % (
                table.replace("'", "''"),
                old_actual.replace("'", "''"),
                new.replace("'", "''"),
            )
        )
    elif vendor in ('postgresql', 'sqlite'):
        schema_editor.execute(
            'ALTER TABLE %s RENAME COLUMN %s TO %s'
            % (qn(table), qn(old_actual), qn(new))
        )
    elif vendor == 'mysql':
        raise NotImplementedError(
            'MySQL column renames are not automated in this migration; use a manual migration or ALTER.'
        )
    else:
        raise NotImplementedError(
            f'Unsupported database vendor {vendor!r} for column rename; extend 0003_rename_community_group_fields.'
        )


def tier_columns_forward(apps, schema_editor) -> None:
    _rename_column(
        schema_editor,
        'AppSubscriptionTier',
        'max_free_payment_plans',
        'max_free_community_groups',
    )
    _rename_column(
        schema_editor,
        'AppSubscriptionTier',
        'max_paid_payment_plans',
        'max_paid_community_groups',
    )


def tier_columns_backward(apps, schema_editor) -> None:
    _rename_column(
        schema_editor,
        'AppSubscriptionTier',
        'max_free_community_groups',
        'max_free_payment_plans',
    )
    _rename_column(
        schema_editor,
        'AppSubscriptionTier',
        'max_paid_community_groups',
        'max_paid_payment_plans',
    )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('community', '0011_rename_payment_plan_models'),
        ('app_subscription', '0002_storageusage_parent_entity'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(tier_columns_forward, tier_columns_backward),
            ],
            state_operations=[
                migrations.RenameField(
                    model_name='appsubscriptiontier',
                    old_name='max_free_payment_plans',
                    new_name='max_free_community_groups',
                ),
                migrations.RenameField(
                    model_name='appsubscriptiontier',
                    old_name='max_paid_payment_plans',
                    new_name='max_paid_community_groups',
                ),
                migrations.AlterField(
                    model_name='appsubscriptiontier',
                    name='max_free_community_groups',
                    field=models.IntegerField(
                        blank=True,
                        help_text='Maximum free community groups (tiers) per community (null = unlimited)',
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name='appsubscriptiontier',
                    name='max_paid_community_groups',
                    field=models.IntegerField(
                        blank=True,
                        help_text='Maximum paid community groups (tiers) per community (null = unlimited)',
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterField(
                    model_name='communitymembersubscription',
                    name='payment_plan',
                    field=models.ForeignKey(
                        help_text='Community group (tier) the member is subscribed to',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='member_subscriptions',
                        to='community.communitygroup',
                    ),
                ),
                migrations.RenameField(
                    model_name='communitymembersubscription',
                    old_name='payment_plan',
                    new_name='community_group',
                ),
            ],
        ),
    ]
