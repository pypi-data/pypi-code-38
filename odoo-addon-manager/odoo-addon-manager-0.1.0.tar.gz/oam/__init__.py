from .manager import (OdooAddonManager, VERBOSE_FULL, VERBOSE_NONE, VERBOSE_NORMAL)

from typing import List
import click

VERSION = "0.1.0"
INSTALL_FILE_NAME = "addons.yml"

@click.group()
def cli():
    """
    - Odoo Addons Manager -
    Install, update or remove your addons based on a description file
    ('addons.yml' in your current directory by default).
    Keep track of every performed operation within a single description file version in the 'changelog.md' file.
    Exhaustive logs can be found in the 'oam.hst' file.
    """
    pass


@cli.command("install")
@click.option("--description-file", "-d", type=click.Path(exists=True, dir_okay=False), default=INSTALL_FILE_NAME,
              help="Path to the file describing modules to install")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.option("-f", "--force", is_flag=True, default=False, help="Overwrite already-installed modules")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Print details for each addon")
@click.option("-vv", "--vverbose", is_flag=True, default=False, help="Print even more details for each addon")
@click.argument('modules', nargs=-1)
def oam_install(description_file: str, output_directory: str, force: bool, verbose: bool, vverbose: bool,
                modules: List[str]):
    """
    Install all modules described in the description file ('addons.yml' by default) into the installation directory.
    Provide a list of module names to restrict installation to those only.
    Modules that are already present will not be overwritten, unless force option is specified.
    """
    oam_manager = OdooAddonManager(
        description_file,
        output_directory,
        verbose_level=VERBOSE_FULL if vverbose else VERBOSE_NORMAL if verbose else VERBOSE_NONE
    )

    if modules:
        for module in modules:
            oam_manager.install(module, force=force)
    else:
        oam_manager.install_all(force=force)


@cli.command("update")
@click.option("--description-file", "-d", type=click.Path(exists=True, dir_okay=False), default=INSTALL_FILE_NAME,
              help="Path to the file describing modules to install")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.option("-f", "--force", is_flag=True, default=False, help="Skip version check before updating")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Print details for each addon")
@click.option("-vv", "--vverbose", is_flag=True, default=False, help="Print even more details for each addon")
@click.argument('modules', nargs=-1)
def oam_update(description_file: str, output_directory: str, force: bool, verbose: bool, vverbose: bool,
               modules: List[str]):
    """
    Update all modules described in the description file that are installed in the current directory.
    Provide a list of module names to restrict update to those only.
    If the version of a module fetched from its source is strictly inferior to the one currently installed,
    it will not be updated, unless force option is specified.
    """
    oam_manager = OdooAddonManager(
        description_file,
        output_directory,
        verbose_level=VERBOSE_FULL if vverbose else VERBOSE_NORMAL if verbose else VERBOSE_NONE
    )

    if modules:
        for module in modules:
            oam_manager.update(module, force=force)
    else:
        oam_manager.update_all(force=force)


@cli.command("uninstall")
@click.option("--description-file", "-d", type=click.Path(exists=True, dir_okay=False), default=INSTALL_FILE_NAME,
              help="Path to the file describing modules to install")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Print details for each addon")
@click.option("-vv", "--vverbose", is_flag=True, default=False, help="Print even more details for each addon")
@click.argument('modules', nargs=-1)
def oam_uninstall(description_file: str, output_directory: str, verbose: bool, vverbose: bool, modules: List[str]):
    """
    Uninstall all modules that are installed in the installation directory but no longer present in the
    description file.
    A list of modules can be specified to uninstall them regardless of the description file.
    """

    verbose_level = VERBOSE_FULL if vverbose else VERBOSE_NORMAL if verbose else VERBOSE_NONE

    if modules:
        oam_manager = OdooAddonManager(install_directory=output_directory, verbose_level=verbose_level)
        for module in modules:
            oam_manager.uninstall(module)
    else:
        oam_manager = OdooAddonManager(description_file, output_directory, verbose_level=verbose_level)
        oam_manager.uninstall_all()


@cli.command("refresh")
@click.option("--description-file", "-d", type=click.Path(exists=True, dir_okay=False), default=INSTALL_FILE_NAME,
              help="Path to the file describing modules to install")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.option("-v", "--verbose", is_flag=True, default=False, help="Print details for each addon")
@click.option("-vv", "--vverbose", is_flag=True, default=False, help="Print even more details for each addon")
def oam_refresh(description_file: str, output_directory: str, verbose: bool, vverbose: bool):
    """
    Run uninstall, update and install commands to fully match with the description file.
    """
    oam_manager = OdooAddonManager(
        description_file,
        output_directory,
        verbose_level=VERBOSE_FULL if vverbose else VERBOSE_NORMAL if verbose else VERBOSE_NONE
    )
    oam_manager.uninstall_all(auto_confirm=True)
    oam_manager.update_all()
    oam_manager.install_all()


@cli.group()
def depends():
    """
    Manage external dependencies of the modules currently installed.
    """
    pass


@depends.command("list")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.option("--requirements", "-r", is_flag=True, default=False,
              help="Print only python dependencies, in a raw format, ready for a pip requirement file")
@click.argument('modules', nargs=-1)
def dependencies_list(output_directory: str, requirements: bool, modules: List[str]):
    """
    List all external dependencies required by the modules currently installed.
    For Python dependencies, check if they are satisfied ('OK' or 'missing').
    """
    oam_manager = OdooAddonManager(install_directory=output_directory)
    oam_manager.list_external_dependencies(raw=requirements, modules=modules)


@depends.command("install")
@click.option("--output-directory", "-o", default=".",
              help="Path to the directory where the modules are or will be installed")
@click.argument('modules', nargs=-1)
def dependencies_install(output_directory: str, modules: List[str]):
    """
    Use pip to install all missing dependencies of the modules currently installed.
    """
    oam_manager = OdooAddonManager(install_directory=output_directory)
    oam_manager.install_missing_dependencies(modules)
