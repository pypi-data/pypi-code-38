# encoding: utf-8

import os
import sys
from functools import partial

import click

print_ok = partial(click.secho)
print_err = partial(click.secho, fg="red")

start_pdb = False


@click.group()
@click.option(
    "--pdb", is_flag=True, help="start python debugger in case of exceptions."
)
def main(pdb):
    """the `{pool}` command provides sub commands to run imports from eawag data
    warehouse landing zones and supports test runs during development and integration of
    data sources
    """
    if pdb:
        global start_pdb
        start_pdb = True


def print_banner(function):
    from datapool import __version__

    def inner(*a, **kw):
        import inspect

        command_name = inspect.stack()[2].frame.f_locals.get("self").name
        print()
        click.secho("> this is datapool version {}".format(__version__), fg="green")
        click.secho("> {}".format(command_name), fg="blue")
        return function(*a, **kw)

    # click needs this to generate help texts from doc strings:
    inner.__doc__ = function.__doc__
    inner.function = function
    return inner



def inject_pdb(function):
    def inner(*a, **kw):
        try:
            return function(*a, **kw)
        except SystemExit:
            raise
        except Exception as e:
            import pdb
            import traceback

            global start_pdb
            traceback.print_exc()
            if start_pdb or os.getenv("PDB"):
                type, value, tb = sys.exc_info()
                pdb.post_mortem(tb)
            else:
                print()
                print("set environment variable PDB to start debugger automatically.")
                raise e

    # click needs this to generate help texts from doc strings:
    inner.__doc__ = function.__doc__
    return inner


@main.command("version")
def version():
    """prints current version of {datapool} software"""
    import datapool

    print("{} {}".format(os.path.basename(sys.argv[0]), datapool.__version__))


@main.command("init-config")
@click.option(
    "--verbose", is_flag=True, help="dumps lots of output from interaction with db"
)
@click.option("--use-sqlitedb", is_flag=True, help="use sqlite db")
@click.option(
    "--force",
    "force_count",
    count=True,
    help="use this twice to overwrite existing config files",
)
@click.argument("landing-zone-folder", type=str)
@print_banner
@inject_pdb
def init_config(verbose, landing_zone_folder, use_sqlitedb, force_count):
    """initializes /etc/{datapool}/ folder with config files.

    landing_zone_folder must be a non-existing folder on the current machine.
    """

    from .commands import init_config

    sys.exit(
        init_config(
            landing_zone_folder,
            use_sqlitedb,
            force_count > 1,
            print_ok,
            print_err,
            verbose,
        )
    )


@main.command("check-config")
@click.option(
    "--verbose", is_flag=True, help="dumps lots of output from interaction with db"
)
@print_banner
@inject_pdb
def check_config(verbose):
    """checks if config file(s) in /etc/{datapool} are valid.
    """
    from .commands import check_config

    sys.exit(check_config(print_ok, print_err, verbose))


@main.command("init-db")
@click.option(
    "--verbose", is_flag=True, help="dumps lots of output from interaction with db"
)
@click.option(
    "--force", "force_count", count=True, help="use this twice to overwrite existing db"
)
@print_banner
@inject_pdb
def init_db(verbose, force_count):
    """creates empty tables in operational database. Run check_config first to see if
    the configured data base settings are valid.
    """
    from .commands import init_db

    sys.exit(init_db(force_count > 1, verbose, print_ok, print_err))


@main.command("create-example")
@click.option(
    "--force",
    "force_count",
    count=True,
    help="use this twice to overwrite existing folder",
)
@click.argument("example-landing-zone-folder", type=str)
@print_banner
@inject_pdb
def create_example(example_landing_zone_folder, force_count):
    """setup landing zone in given folder with example files.
    """
    from .commands import create_example

    reset = force_count > 1
    sys.exit(create_example(example_landing_zone_folder, reset, print_ok, print_err))


@main.command("start-develop")
@click.option(
    "--verbose", is_flag=True, help="dumps lots of output from interaction with db"
)
@click.option(
    "--force", "force_count", count=True, help="use this twice to overwrite existing db"
)
@click.argument("development-landing-zone-folder", type=str)
@print_banner
@inject_pdb
def start_develop(development_landing_zone_folder, force_count, verbose):
    """setup local landing zone for adding new site / instrument / conversion script.
    this command will clone the operational landing zone (might be empty).
    """
    from .commands import start_develop

    reset = force_count > 1
    sys.exit(
        start_develop(
            development_landing_zone_folder, reset, verbose, print_ok, print_err
        )
    )


@main.command("update-operational")
@click.option("--verbose", is_flag=True, help="might dump lots of output")
@click.option(
    "--force",
    "force_count",
    count=True,
    help="use this twice to overwrite existing landing zone in case of errors when"
    " checking",
)
@click.option(
    "--copy-raw-files",
    is_flag=True,
    help="copy raw files also to operational landing zone",
)
@click.argument("development-landing-zone-folder", type=str)
@print_banner
@inject_pdb
def update_operational(
    development_landing_zone_folder, force_count, verbose, copy_raw_files
):
    """deploys local changes to operational landing zone.
    """
    from .commands import update_operational

    overwrite = force_count > 1
    sys.exit(
        update_operational(
            development_landing_zone_folder,
            verbose,
            overwrite,
            copy_raw_files,
            print_ok,
            print_err,
        )
    )


@main.command("check")
@click.option(
    "--result-folder", type=str, default=None, help="provide target for results"
)
@click.option("--verbose", is_flag=True, help="might dump lots of output")
@click.argument("development-landing-zone-folder", type=str)
@print_banner
@inject_pdb
def check(development_landing_zone_folder, result_folder, verbose):
    """checks scripts and produced results in given landing zone. does not write to
    database.  """
    from .commands import check

    sys.exit(
        check(
            development_landing_zone_folder, result_folder, verbose, print_ok, print_err
        )
    )


@main.command("run-simple-server")
@click.option("--verbose", is_flag=True, help="might dump lots of output")
@print_banner
def run_simple_server(verbose):
    """Runs single process {datapool} server. Mostly used for testing.
    """
    from .commands import run_simple_server
    from .database import install_excepthook
    install_excepthook()
    sys.exit(run_simple_server(verbose, print_ok, print_err))


def _create_add():
    """dynamic setup of doc string to provide cmdline help only configured
    by the scripts themselves to avoid duplication"""

    def add(development_landing_zone_folder, what, settings):
        from .commands import add

        sys.exit(
            add(development_landing_zone_folder, what, settings, print_ok, print_err)
        )

    from . import templates

    add.__doc__ = """creates boilerplate entries for {}

    example:  {{pool}} add develop_landing_zone site name=test_site x=123
    """.format(
        ", ".join(templates.scripts)
    )
    return add


add = main.command("add")(
    click.argument("development-landing-zone-folder", type=str)(
        click.argument("what", type=str)(
            click.argument("settings", type=str, nargs=-1)(
                print_banner(inject_pdb(_create_add()))
            )
        )
    )
)


@main.command("delete-signals")
@click.option(
    "--force",
    "force_count",
    count=True,
    help="use this twice to perform deletion, else only checks are performed and "
    "number of affected db entries is estimated",
)
@click.option(
    "--max-rows",
    type=click.INT,
    default=10,
    help="number of signals to print before deletion, default is 10",
)
@click.argument("filters", type=str, nargs=-1)
@print_banner
@inject_pdb
def delete_signals(force_count, max_rows, filters):
    """
    This command deletes all signals where all filter conditions are
    true.

    Filters are exressions like "timestamp>=2000-01-01,site==abc", the
    surrounding quotes are required if symbols '<' or '>' are occur in
    such expressions.
    """
    from .commands.delete import delete_signals, delete_meta

    if os.getuid() != 0:
        print_err("- you must run this command as root")
        sys.exit(1)

    do_delete = force_count >= 2
    sys.exit(delete_signals(do_delete, max_rows, filters, print_ok, print_err))


@main.command("delete-entity")
@click.option(
    "--what",
    type=click.Choice(["signals", "source", "source_type", "site", "parameter"]),
)
@click.option(
    "--force",
    "force_count",
    count=True,
    help="use this twice to perform deletion, else only checks are performed and "
    "number of affected db entries is estimated",
)
@click.option(
    "--max-rows",
    type=click.INT,
    default=10,
    help="number of signals to print before deletion, default is 10",
)
@click.argument("name", type=str, nargs=1)
@print_banner
@inject_pdb
def delete_entity(what, name, force_count, max_rows):
    """
    This command deletes a given entity (like site, source..) and the
    corresponding signals.
    """
    from .commands.delete import delete_signals, delete_meta

    if os.getuid() != 0:
        print_err("- you must run this command as root")
        sys.exit(1)

    do_delete = force_count >= 2

    sys.exit(delete_meta(do_delete, max_rows, what, name, print_ok, print_err))


def fix_help_texts(pool, datapool):
    for name, obj in globals().items():
        if isinstance(obj, click.core.Group):
            pass  # continue
        if isinstance(obj, click.core.Command):
            obj.help = obj.help.format(pool=pool, datapool=datapool)
            obj.short_help = obj.get_short_help_str().format(
                pool=pool, datapool=datapool
            )


# delay fixes for other instances of software:
if os.path.basename(sys.argv[0]) == "pool":
    fix_help_texts("pool", "datapool")
