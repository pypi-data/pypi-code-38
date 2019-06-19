import click
from tormor.dsn import makeDSN
from tormor.commands import enable_modules, migrate, execute_sql_file, include
from tormor.connections import Connection
import csv

@click.group()
@click.option('-h', nargs=1, required=False, help="Postgres host")
@click.option('-d', nargs=1, required=False, help="Database name")
@click.option('-u', '-U', nargs=1, required=False, help="Database username (role)")
@click.option('-p', nargs=1, required=False, help="Database port")
@click.option('-password', '-P', nargs=1, required=False, help="Database password (Not recommended, use environment variable PGPASSWORD instead)")
@click.pass_context
def script(ctx, h, d, u, p, password):
    cnx_destination = {
        '-h': h,
        '-d': d,
        '-U': u,
        '-p': p,
        '-P': password
    }
    dsn = makeDSN(cnx_destination)
    ctx.obj = {'cnx': Connection(dsn)}

script.add_command(migrate)
script.add_command(enable_modules)
script.add_command(execute_sql_file)
script.add_command(include)