# Migration: Replace UserRole with Role + Permission; add User.is_staff and User.roles M2M

import django.db.models.deletion
from django.db import migrations, models


def create_roles_and_migrate_user_roles(apps, schema_editor):
    User = apps.get_model('account', 'User')
    UserRole = apps.get_model('account', 'UserRole')
    Role = apps.get_model('account', 'Role')

    # Create default roles if they don't exist (by name)
    role_admin, _ = Role.objects.get_or_create(
        name='admin',
        defaults={'is_admin_role': True, 'description': 'Platform administrator'},
    )
    role_user, _ = Role.objects.get_or_create(
        name='user',
        defaults={'is_admin_role': False, 'description': 'Default user role'},
    )
    name_to_role = {'admin': role_admin, 'user': role_user}

    # Migrate: for each User that had a role_id, add the corresponding Role to roles M2M
    for user in User.objects.all():
        try:
            old_role = UserRole.objects.get(id=user.role_id) if user.role_id else None
        except UserRole.DoesNotExist:
            old_role = None
        if old_role:
            role = name_to_role.get(old_role.name)
            if role:
                user.roles.add(role)
            else:
                new_role, _ = Role.objects.get_or_create(
                    name=old_role.name,
                    defaults={'is_admin_role': False, 'description': ''},
                )
                user.roles.add(new_role)
        else:
            user.roles.add(role_user)


def noop_reverse(apps, schema_editor):
    pass  # Reverse not implemented; would require storing old role_id again and recreating UserRole


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Permission',
                'verbose_name_plural': 'Permissions',
                'db_table': 'Permission',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_admin_role', models.BooleanField(default=False, help_text='If True, treated as staff/admin for access control.')),
                ('permissions', models.ManyToManyField(blank=True, help_text='Permissions granted by this role.', related_name='roles', to='account.permission')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'db_table': 'Roles',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates staff/admin access (e.g. Django admin).'),
        ),
        migrations.AddField(
            model_name='user',
            name='roles',
            field=models.ManyToManyField(blank=True, help_text='Roles assigned to this user (replaces single role for scaling).', related_name='users', to='account.role'),
        ),
        migrations.RunPython(create_roles_and_migrate_user_roles, noop_reverse),
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
    ]
