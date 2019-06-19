from tormor.exceptions import SchemaNotPresent
from tormor.path_helper import get_schema_path
import csv
import click
import os

# String of queries to add module
ADD_MODULE = """INSERT INTO module(name) VALUES($1)"""

# String of queries to create table 'module' and 'migration'
BOOTSTRAP_SQL = """
CREATE TABLE module (
    name text NOT NULL,
    CONSTRAINT module_pk PRIMARY KEY(name)
);

CREATE TABLE migration (
    module_name text NOT NULL,
    CONSTRAINT migration_module_fkey
        FOREIGN KEY (module_name)
        REFERENCES module (name) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE,
    migration text NOT NULL,
    CONSTRAINT migration_pk PRIMARY KEY (module_name, migration)
);
"""
@click.group()
def subcommand():
    pass

@subcommand.command('migrate')
@click.pass_context
@click.option('--dry-run', is_flag=True)
def migrate(ctx, dry_run):
    """Run all migrations"""

    conn = ctx.obj['cnx']
    paths = get_schema_path()
    migrated_modules = set(conn.fetch("SELECT module_name, migration FROM migration"))
    to_be_run_scripts = []
    query = ""
    for each_path in paths:
        for root, dirs, files in os.walk(each_path):
            relpath = os.path.relpath(root, each_path)
            if relpath != "." and relpath in conn.load_modules():
                to_be_run_scripts += [(relpath, filepath, each_path) for filepath in files if filepath.endswith(".sql")]
    to_be_run_scripts.sort(key=lambda m: m[1])
    for (module, migration, path) in to_be_run_scripts:
        if (module, migration) not in migrated_modules:
            query += get_migrate_sql(module, migration, os.path.join(path, module, migration))
    if query:
        if not dry_run:
            print("Migrating modules...")
            conn.execute(query)
            print("Successfully migrated modules")
        else:
            print(query)
    else:
        pass

@subcommand.command('enable-modules')
@click.pass_context
@click.argument('modules', required=True, nargs=-1)
def enable_modules(ctx, modules):
    """Enable modules"""

    conn = ctx.obj['cnx']
    modules_to_be_added = set(modules)
    try:
        current_modules = conn.load_modules()
    except SchemaNotPresent:
        print("No existing module table. Bootstrapping...")
        conn.execute(BOOTSTRAP_SQL)
        current_modules = conn.load_modules()
    for each_module in modules_to_be_added.difference(current_modules):
        conn.execute(ADD_MODULE.replace("$1", "\'" + each_module +"\'"))
        print(each_module, "enabled")

@subcommand.command('sql')
@click.pass_context
@click.argument('sqlfile', nargs=1)
def execute_sql_file(ctx, sqlfile):
    """
    Execute SQL queries in files, useful for running migration scripts
    """

    try:
        conn = ctx.obj['cnx'] 
        with open(sqlfile) as f:
            commands = f.read()
            conn.execute(commands)
        print(sqlfile, "successfully executed")
    except Exception:
        print("Error whilst running", sqlfile)
        raise

@subcommand.command()
@click.pass_context
@click.argument('filename', required=True, nargs=1)
def include(ctx, filename):
    """Run all commands inside a file"""
    with open(filename, newline="") as f:
        lines = csv.reader(f, delimiter=" ")
        for each_line in lines:
            if len(each_line) and not each_line[0].startswith("#"):
                cmd = each_line.pop(0)
                if cmd == "migrate":
                    if len(each_line) == 0:
                        ctx.invoke(migrate, dry_run = False)
                    elif len(each_line) == 1:
                        ctx.invoke(migrate, dry_run = True if each_line[0] == '--dry-run' else False)
                    else:
                        raise click.ClickException("Error in migrate command")
                elif cmd == "enable-modules":
                    ctx.invoke(enable_modules, modules = each_line)
                elif cmd == "sql" and len(each_line) == 1:
                    ctx.invoke(execute_sql_file, sqlfile = each_line[0])
                else:
                    raise click.ClickException("Unknown command or parameter")

def get_migrate_sql(module, migration, filename):
    try:
        with open(filename) as f:
            commands = """
                INSERT INTO module (name) VALUES('{module}') ON CONFLICT (name) DO NOTHING;
                INSERT INTO migration (module_name, migration)  VALUES('{module}', '{migration}') ON CONFLICT (module_name, migration) DO NOTHING;    
                {cmds}
            """.format(
                module=module, migration=migration, cmds=f.read()
            )
            print("Read", filename)
            return commands
    except Exception:
        print("Error whilst running", filename)
        raise
