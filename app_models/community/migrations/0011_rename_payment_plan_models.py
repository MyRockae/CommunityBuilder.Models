# Renames PaymentPlan/UserPaymentPlan tables and FK/M2M columns; state moves to CommunityGroup/CommunityGroupAccess.

from typing import Optional

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


M2M_THROUGH_TABLES = (
    'Classroom_payment_plans',
    'Quiz_payment_plans',
    'Meeting_payment_plans',
    'MeetingSeries_payment_plans',
    'Forum_payment_plans',
    'Resource_payment_plans',
)


def _table_exists(schema_editor, table: str) -> bool:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return table in connection.introspection.table_names(cursor)


def _column_names(schema_editor, table: str) -> dict:
    """Map lowercased column name -> actual identifier as returned by the DB."""
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return {
            c.name.lower(): c.name
            for c in connection.introspection.get_table_description(cursor, table)
        }


def _resolve_column(cols: dict, want: str) -> Optional[str]:
    return cols.get(want.lower())


def _rename_table_forward(schema_editor, old: str, new: str) -> None:
    if old == new or not _table_exists(schema_editor, old):
        return
    if _table_exists(schema_editor, new):
        return
    vendor = schema_editor.connection.vendor
    qn = schema_editor.connection.ops.quote_name
    if vendor == 'microsoft':
        # sp_rename must not run inside a transaction on some SQL Server versions.
        schema_editor.execute(
            "EXEC sp_rename N'%s', N'%s', N'OBJECT'" % (old.replace("'", "''"), new.replace("'", "''"))
        )
    elif vendor == 'postgresql':
        schema_editor.execute('ALTER TABLE %s RENAME TO %s' % (qn(old), qn(new)))
    elif vendor == 'sqlite':
        schema_editor.execute('ALTER TABLE %s RENAME TO %s' % (qn(old), qn(new)))
    elif vendor == 'mysql':
        schema_editor.execute('RENAME TABLE %s TO %s' % (qn(old), qn(new)))
    else:
        raise NotImplementedError(
            f'Unsupported database vendor {vendor!r} for table rename; extend 0011_rename_payment_plan_models.'
        )


def _rename_column_forward(schema_editor, table: str, old: str, new: str) -> None:
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
            f'Unsupported database vendor {vendor!r} for column rename; extend 0011_rename_payment_plan_models.'
        )


def rename_payment_schema_forward(apps, schema_editor) -> None:
    _rename_table_forward(schema_editor, 'PaymentPlan', 'CommunityGroup')
    _rename_table_forward(schema_editor, 'UserPaymentPlan', 'CommunityGroupAccess')
    _rename_column_forward(
        schema_editor, 'CommunityGroupAccess', 'payment_plan_id', 'community_group_id'
    )
    _rename_column_forward(
        schema_editor, 'CommunityMemberSubscription', 'payment_plan_id', 'community_group_id'
    )
    for m2m in M2M_THROUGH_TABLES:
        _rename_column_forward(schema_editor, m2m, 'paymentplan_id', 'communitygroup_id')


def _rename_table_backward(schema_editor, old: str, new: str) -> None:
    _rename_table_forward(schema_editor, old, new)


def rename_payment_schema_backward(apps, schema_editor) -> None:
    for m2m in M2M_THROUGH_TABLES:
        _rename_column_forward(schema_editor, m2m, 'communitygroup_id', 'paymentplan_id')
    _rename_column_forward(
        schema_editor, 'CommunityMemberSubscription', 'community_group_id', 'payment_plan_id'
    )
    _rename_column_forward(
        schema_editor, 'CommunityGroupAccess', 'community_group_id', 'payment_plan_id'
    )
    _rename_table_backward(schema_editor, 'CommunityGroupAccess', 'UserPaymentPlan')
    _rename_table_backward(schema_editor, 'CommunityGroup', 'PaymentPlan')


class Migration(migrations.Migration):
    # SQL Server: sp_rename often cannot run inside an atomic migration block.
    atomic = False

    dependencies = [
        ('community', '0010_community_is_active_flag_count'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(rename_payment_schema_forward, rename_payment_schema_backward),
            ],
            state_operations=[
                migrations.RenameModel('PaymentPlan', 'CommunityGroup'),
                migrations.AlterModelTable('CommunityGroup', 'CommunityGroup'),
                migrations.AlterField(
                    model_name='communitygroup',
                    name='community',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='community_groups',
                        to='community.community',
                    ),
                ),
                migrations.AlterField(
                    model_name='userpaymentplan',
                    name='payment_plan',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='access_assignments',
                        to='community.communitygroup',
                    ),
                ),
                migrations.RenameModel('UserPaymentPlan', 'CommunityGroupAccess'),
                migrations.AlterModelTable('CommunityGroupAccess', 'CommunityGroupAccess'),
                migrations.RenameField(
                    model_name='communitygroupaccess',
                    old_name='payment_plan',
                    new_name='community_group',
                ),
                migrations.AlterField(
                    model_name='communitygroupaccess',
                    name='user',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='community_group_accesses',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                migrations.AlterField(
                    model_name='communitygroupaccess',
                    name='community',
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='community_group_access_entries',
                        to='community.community',
                    ),
                ),
                migrations.AlterField(
                    model_name='communitygroupaccess',
                    name='expires_at',
                    field=models.DateTimeField(
                        blank=True,
                        help_text='When access expires (null for lifetime)',
                        null=True,
                    ),
                ),
                migrations.AlterField(
                    model_name='communitygroupaccess',
                    name='is_active',
                    field=models.BooleanField(
                        default=True,
                        help_text='Whether this access is currently active',
                    ),
                ),
            ],
        ),
    ]
