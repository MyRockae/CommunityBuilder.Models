# Renames implicit M2M through table Forum_payment_plans -> Forum_community_groups (data preserved).

from django.db import migrations


def _table_exists(schema_editor, table: str) -> bool:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return table in connection.introspection.table_names(cursor)


def _rename_table_forward(schema_editor, old: str, new: str) -> None:
    if old == new or not _table_exists(schema_editor, old):
        return
    if _table_exists(schema_editor, new):
        return
    vendor = schema_editor.connection.vendor
    qn = schema_editor.connection.ops.quote_name
    if vendor == 'postgresql':
        schema_editor.execute('ALTER TABLE %s RENAME TO %s' % (qn(old), qn(new)))
    elif vendor == 'sqlite':
        schema_editor.execute('ALTER TABLE %s RENAME TO %s' % (qn(old), qn(new)))
    elif vendor == 'mysql':
        schema_editor.execute('RENAME TABLE %s TO %s' % (qn(old), qn(new)))
    elif vendor == 'microsoft':
        schema_editor.execute(
            "EXEC sp_rename N'%s', N'%s', N'OBJECT'" % (old.replace("'", "''"), new.replace("'", "''"))
        )
    else:
        raise NotImplementedError(
            f'Unsupported database vendor {vendor!r} for M2M table rename; extend 0004_rename_payment_plans_m2m_to_community_groups.'
        )


def rename_forum_m2m_forward(apps, schema_editor) -> None:
    _rename_table_forward(schema_editor, 'Forum_payment_plans', 'Forum_community_groups')


def rename_forum_m2m_backward(apps, schema_editor) -> None:
    _rename_table_forward(schema_editor, 'Forum_community_groups', 'Forum_payment_plans')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('community_forum', '0003_alter_forum_payment_plans'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(rename_forum_m2m_forward, rename_forum_m2m_backward),
            ],
            state_operations=[
                migrations.RenameField(
                    model_name='forum',
                    old_name='payment_plans',
                    new_name='community_groups',
                ),
            ],
        ),
    ]
