import click

from threedi_modelchecker.model_checks import ThreediModelChecker
from threedi_modelchecker.threedi_database import ThreediDatabase
from threedi_modelchecker import exporters


# TODO: --file option currently does nothing!
@click.group()
@click.option("-f", "--file", help="Write errors to file, instead of stdout")
@click.option(
    "-s", "--sum/--no-sum", default=False, help="Prints a summary instead of all errors"
)
@click.pass_context
def check_model(ctx, file, sum):
    """Checks the threedi-model for errors"""
    click.echo("Parsing threedi-model for any errors")
    if file:
        click.echo("Model errors will be written to %s" % file)
    if sum:
        click.echo("Printing a summary of the found errors")


@check_model.command()
@click.option("-d", "--database", required=True, help="database name to connect to")
@click.option("-h", "--host", required=True, help="database server host")
@click.option("-p", "--port", required=True, default=5432, help="database server port")
@click.option("-u", "--username", required=True, help="database username")
@click.pass_context
def postgis(context, database, host, port, username, password):
    """Parse a postgis model"""
    postgis_settings = {
        "host": host,
        "port": port,
        "database": database,
        "username": username,
        "password": password,
    }
    db = ThreediDatabase(
        connection_settings=postgis_settings, db_type="postgres", echo=False
    )
    process(db, context.parent)


@check_model.command()
@click.option(
    "-s",
    "--sqlite",
    required=True,
    type=click.Path(exists=True, readable=True),
    help="sqlite file",
)
@click.pass_context
def sqlite(context, sqlite):
    """Parse a sqlite model"""
    sqlite_settings = {"db_path": sqlite, "db_file": sqlite}
    db = ThreediDatabase(
        connection_settings=sqlite_settings, db_type="spatialite", echo=False
    )
    process(db, context.parent)


def process(threedi_db, context):
    mc = ThreediModelChecker(threedi_db)
    model_errors = mc.parse_model()

    file_output = context.params.get("file")
    summary = context.params.get("sum")
    if context.params.get("file"):
        exporters.export_to_file(model_errors, file_output)
    if summary:
        error_summary, total_errors = exporters.summarize_type_errors(model_errors)
        click.echo("---SUMMARY---")
        click.echo("Total number of errors: %s" % total_errors)
        click.echo(error_summary)
    if not summary and not file_output:
        exporters.print_errors(model_errors)

    click.echo("Finished processing model")


if __name__ == "__main__":
    exit(check_model())
