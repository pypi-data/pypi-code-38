from importlib import import_module


def get_migration_abspath(app_label, migration_name):
    from django.db.migrations.loader import MigrationLoader

    module_name, _ = MigrationLoader.migrations_module(app_label)
    migration_path = "{}.{}".format(module_name, migration_name)
    migration_module = import_module(migration_path)

    migration_file = migration_module.__file__
    if migration_file.endswith(".pyc"):
        migration_file = migration_file[:-1]
    return migration_file
