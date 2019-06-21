import os
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from invoke import task

from ..pipenv import Pipenv
from ..utils.print import print_action, print_error

ALEMBIC_CONFIG = "alembic.ini"
ALEMBIC_TABLE_PREFIX = "alembic_version_cs_"
CORE_PACKAGE = "civilservant-core"
PROJECT_LIBS_PATH = Path(os.environ["CS_PROJECT_LIBS_PATH"])


def _upgrade(lib_name, alembic_config_path):
    """Run alembic revisions from the specified library."""
    alembic_table = ALEMBIC_TABLE_PREFIX + lib_name.split("-")[1]
    os.environ["CS_DB_ALEMBIC_TABLE"] = alembic_table
    alembic_config = Config(alembic_config_path)

    script_location = Path(alembic_config.get_main_option("script_location"))
    if not script_location.is_absolute():
        script_location = Path(alembic_config_path.parent, script_location)
        alembic_config.set_main_option("script_location", str(script_location))

    from ...db import init_engine
    with init_engine().begin() as connection:
        alembic_config.attributes["connection"] = connection
        command.upgrade(alembic_config, "head")
    

@task
def upgrade(c, lib=[]):
    """Run alembic revisions from all included CivilServant libraries."""
    pipenv = Pipenv(c, exit_on_error=True)
    pipenv.ensure_active()

    # Package civilservant-core must be installed to use db.init_engine
    if not pipenv.has_package(CORE_PACKAGE):
        print_error("Package not found: ", CORE_PACKAGE)
        sys.exit(1)

    libs_path = Path(pipenv.root_path, PROJECT_LIBS_PATH)
    if not lib:
        lib = [path.name for path in libs_path.iterdir()]
    for arg in lib:
        alembic_config_path = Path(libs_path, arg, ALEMBIC_CONFIG)
        if alembic_config_path.exists():
            print_action(f"Running revisions for {arg}")
            _upgrade(arg, alembic_config_path)

