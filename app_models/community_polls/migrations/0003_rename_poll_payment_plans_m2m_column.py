# Poll_payment_plans was omitted from community.0011_rename_payment_plan_models M2M_THROUGH_TABLES;
# ORM expects communitygroup_id after Poll.payment_plans targets CommunityGroup.

from typing import Optional

from django.db import migrations


def _table_exists(schema_editor, table: str) -> bool:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return table in connection.introspection.table_names(cursor)


def _column_names(schema_editor, table: str) -> dict:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return {
            c.name.lower(): c.name
            for c in connection.introspection.get_table_description(cursor, table)
        }


def _resolve_column(cols: dict, want: str) -> Optional[str]:
    return cols.get(want.lower())


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
            f'Unsupported database vendor {vendor!r} for column rename; extend 0003_rename_poll_payment_plans_m2m_column.'
        )


def rename_poll_m2m_forward(apps, schema_editor) -> None:
    _rename_column_forward(schema_editor, 'Poll_payment_plans', 'paymentplan_id', 'communitygroup_id')


def rename_poll_m2m_backward(apps, schema_editor) -> None:
    _rename_column_forward(schema_editor, 'Poll_payment_plans', 'communitygroup_id', 'paymentplan_id')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('community_polls', '0002_alter_poll_payment_plans'),
    ]

    operations = [
        migrations.RunPython(rename_poll_m2m_forward, rename_poll_m2m_backward),
    ]
