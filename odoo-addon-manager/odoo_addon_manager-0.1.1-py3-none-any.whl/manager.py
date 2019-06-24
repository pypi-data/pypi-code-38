import ast
import re
from datetime import datetime
from io import TextIOWrapper
from typing import List, Dict, Any
from urllib.parse import urlparse

import callable_pip
import click
import pygit2
import yaml
from fs.base import FS
from fs.copy import copy_dir
from fs.osfs import OSFS
from fs.path import join
from fs.tempfs import TempFS
from fs.zipfs import ZipFS
from packaging import version

SOURCE_GIT = "git"
SOURCE_LOCAL_DIR = "dir"
SOURCE_LOCAL_ZIP = "zip"

HISTORY_FILE_NAME = "oam.hst"
CHANGELOG_FILE_NAME = "changelog.md"
TEMP_DIR_NAME = "OAM"

OPERATION_INSTALL = "Installation"
OPERATION_UPDATE = "Update"
OPERATION_UNINSTALL = "Uninstall"

LOG_STATUS_OK = "ok"
LOG_STATUS_PENDING = "pending"
LOG_STATUS_WARNING = "warning"
LOG_STATUS_ERROR = "error"

VERBOSE_NONE = 0
VERBOSE_NORMAL = 1
VERBOSE_FULL = 2


class OdooAddonManager:
    """
    Class wrapping the OAM behaviour

    Attributes
    ----------
    install_dir: OSFS
        The installation directory
    src_cache: dict
        A dictionary containing, for each source type supporting cache (git), the temporary location of the previously
        downloaded sources
    odoo_version: str
        Version of Odoo using the addons
    desc_version: str
        Version of the description file used to log changes
    modules_to_install: dict
        Modules to install as described in the YAML file
    verbose_level: str
        Level of details to print
    """

    install_dir: OSFS
    modules_to_install: Dict[str, Dict[str, Any]]
    src_cache: Dict[str, Dict[str, Any]]
    odoo_version: str
    desc_version: str = None
    verbose_level: str
    _tmp_dir: TempFS = None
    _hst_file: TextIOWrapper = None
    _chglog_file: TextIOWrapper = None

    def __init__(self, description_file: str = None, install_directory: str = ".", verbose_level: str = VERBOSE_NONE):
        self.install_dir = OSFS(install_directory)
        self.verbose_level = verbose_level
        self.src_cache = {
            "git": {},
        }

        if description_file:
            with open(description_file, "r") as description_file:
                install_data = yaml.load(description_file, Loader=yaml.Loader)
                self.modules_to_install = install_data.get("modules", [])
                self.odoo_version = install_data.get("odoo_version")
                self.desc_version = install_data.get("version")

    def __del__(self):
        self.install_dir.close()
        if self._tmp_dir:
            self._tmp_dir.close()
        if self._hst_file:
            self._hst_file.close()
        if self._chglog_file:
            self._chglog_file.close()

    @property
    def tmp_dir(self) -> TempFS:
        """
        The temporary directory used to download modules before installing them if needed.
        """
        if not self._tmp_dir:
            self._tmp_dir = TempFS(TEMP_DIR_NAME)
        return self._tmp_dir

    @property
    def history_file(self) -> TextIOWrapper:
        """
        The history file where are logged the operations performed in the installation directory
        """
        if not self._hst_file:
            self._hst_file = open(self.install_dir.getsyspath(HISTORY_FILE_NAME), 'a+')
        return self._hst_file

    @property
    def changelog_file(self) -> TextIOWrapper:
        """
        The markdown changelog file listing changes in a human-readable format
        """
        if not self._chglog_file:
            self._chglog_file = open(self.install_dir.getsyspath(CHANGELOG_FILE_NAME), "a+")
            self._chglog_file.seek(0)
            if not self._chglog_file.read():
                self._chglog_file.write("# CHANGELOG")

        self._chglog_file.seek(0)

        return self._chglog_file

    def install_all(self, force: bool = False):
        """
        Install all modules described in the description file.
        :param force: whether to overwrite installed modules or not
        """
        installed_modules = []

        if self.verbose_level == VERBOSE_NONE:
            with click.progressbar(self.modules_to_install) as modules:
                for module in modules:
                    if self.install(module, force):
                        installed_modules.append(module)
        else:
            for module in self.modules_to_install:
                if self.install(module, force):
                    installed_modules.append(module)

        # Modules installed are removed from the list to avoid being processed twice e.g. in case of a refresh
        for module in installed_modules:
            self.modules_to_install.pop(module)

        click.echo("{} module(s) installed.".format(len(installed_modules)))

    def install(self, module_name: str, force: bool = False) -> bool:
        """
        Install a single module from its source.
        :param module_name: Name of the module
        :param force: Whether to overwrite the module if it is already installed
        :param: Whether the module has been installed or not
        """
        success = False
        self.pretty_print(module_name, "Installing...", level=VERBOSE_FULL)

        source = self.modules_to_install[module_name]
        origin_name = source.get("origin_name", module_name)
        installed_version = self.get_module_version(module_name, self.install_dir)

        if force or not installed_version:
            try:
                source_fs = self.fetch_module_from_source(module_name)
                self.install_from_fs(origin_name, source_fs, output_name=module_name)
                version = self.get_module_version(module_name, self.install_dir)
                self.log(module_name, OPERATION_INSTALL, force=force, extra=version)
                if not force:
                    self.log_md(module_name, OPERATION_INSTALL, new_version=version)

                success = True
            except InvalidModuleError as err:
                self.pretty_print(module_name, err.message, status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
            except pygit2.errors.GitError:
                self.pretty_print(module_name, "Installation failed - Could not fetch from Git repository.",
                                  status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
            except Exception as e:
                self.pretty_print(module_name, "Installation failed ({})".format(type(e).__name__),
                                  status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
        else:
            self.pretty_print(
                module_name,
                "Already installed. Skipping installation.",
                status=LOG_STATUS_WARNING,
                level=VERBOSE_NORMAL
            )

        return success

    def update_all(self, force: bool = False):
        """
        Update all modules
        :param force: Whether to skip version check or not.
            If True, modules are just replaced no matter if they are being downgraded or installed for the first time.
        """
        updated_modules = []

        if self.verbose_level == VERBOSE_NONE:
            with click.progressbar(self.modules_to_install) as modules:
                for module in modules:
                    if self.update(module, force):
                        updated_modules.append(module)
        else:
            for module in self.modules_to_install:
                if self.update(module, force):
                    updated_modules.append(module)

        # Modules updated are removed from the list to avoid being processed twice in case of a refresh
        for module in updated_modules:
            self.modules_to_install.pop(module)

        click.echo("{} module(s) updated.".format(len(updated_modules)))

    def update(self, module_name: str, force: bool = False) -> bool:
        """
        Update a single module.
        :param module_name: Name of the module
        :param force: Whether to skip version check or not.
            If True, modules are just replaced no matter if they are being downgraded or installed for the first time.
        :return: Whether the module has been updated or not
        """
        success = False
        self.pretty_print(module_name, "Updating...", level=VERBOSE_FULL)

        installed_version = self.get_module_version(module_name, self.install_dir)

        if force or installed_version:
            try:
                source_fs = self.fetch_module_from_source(module_name)
                origin_name = self.modules_to_install[module_name].get("origin_name", module_name)
                new_version = self.get_module_version(origin_name, source_fs)

                if force or version.parse(new_version) >= version.parse(installed_version):
                    self.pretty_print(
                        module_name,
                        "Updating from {0} to {1}".format(installed_version, new_version),
                        level=VERBOSE_FULL
                    )
                    self.install_from_fs(origin_name, source_fs, output_name=module_name)
                    self.log(module_name, OPERATION_UPDATE, force=force, extra="from {0} to {1}".format(
                        installed_version,
                        new_version
                    ))
                    if not force:
                        self.log_md(module_name, OPERATION_UPDATE, installed_version, new_version)

                    success = True
                else:
                    self.pretty_print(
                        module_name,
                        "Fetched version ({0}) is inferior to current version ({1}). Skipping update.".format(
                            new_version, installed_version
                        ),
                        status=LOG_STATUS_ERROR,
                        level=VERBOSE_NORMAL
                    )
            except InvalidModuleError as err:
                self.pretty_print(module_name, err.message, status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
            except pygit2.errors.GitError:
                self.pretty_print(module_name, "Update failed - Could not fetch from Git repository.",
                                  status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
            except Exception as e:
                self.pretty_print(module_name, "Update failed ({})".format(type(e).__name__),
                                  status=LOG_STATUS_ERROR, level=VERBOSE_NONE)
        else:
            self.pretty_print(
                module_name,
                "Not installed. Skipping update.".format(module_name),
                status=LOG_STATUS_WARNING,
                level=VERBOSE_NORMAL
            )

        return success

    def uninstall_all(self, auto_confirm=False):
        """
        Uninstall all modules that are installed but not present in the description file.
        Ask confirmation to the user.
        :param auto_confirm: Do not ask the user to confirm if True
        """
        installed_modules = self.get_installed_modules()
        modules_to_uninstall = set(installed_modules.keys()) - set(self.modules_to_install.keys())

        if not auto_confirm:
            click.echo("The following modules will be removed:")
            for module in modules_to_uninstall:
                click.echo(module)
            click.confirm('Do you want to continue?', abort=True)

        count = 0

        if self.verbose_level == VERBOSE_NONE:
            with click.progressbar(modules_to_uninstall) as modules:
                for module in modules:
                    count += self.uninstall(module)
        else:
            for module in modules_to_uninstall:
                count += self.uninstall(module)

        click.echo("{} module(s) removed.".format(count))

    def uninstall(self, module_name: str) -> bool:
        """
        Uninstall a single module if it is installed.
        :param module_name: Name of the module
        :return: Whether the module has been uninstalled or not
        """
        success = False

        if module_name in self.install_dir.listdir("."):
            self.pretty_print(module_name, "Uninstalling...", level=VERBOSE_FULL)
            self.install_dir.removetree(module_name)
            success = True
            self.log(module_name, OPERATION_UNINSTALL)
            self.log_md(module_name, OPERATION_UNINSTALL)
            self.pretty_print(module_name, "Uninstalled.", status=LOG_STATUS_OK, level=VERBOSE_NORMAL)
        else:
            self.pretty_print(module_name, "Not installed. Skipping uninstall.", status=LOG_STATUS_ERROR, level=VERBOSE_NORMAL)

        return success

    def get_installed_modules(self) -> Dict[str, str]:
        """
        Scan installation directory to list currently installed modules
        :return: A dictionary of module names as keys and their currently installed version as values
        """
        modules = {}
        for module in self.install_dir.scandir("."):
            if module.is_dir and "__manifest__.py" in self.install_dir.listdir(module.name):
                manifest_file = self.install_dir.getsyspath(join(module.name, "__manifest__.py"))
                with open(manifest_file, "r") as manifest:
                    modules[module.name] = ast.literal_eval(manifest.read())["version"]

        return modules

    @staticmethod
    def get_module_version(module_name: str, directory: FS) -> str:
        """
        Get the version of the module in the given directory
        :param module_name: name of the module
        :param directory: FS object pointing to the parent directory of the module
        :return: version of the module or None if it is not present in the directory
        """
        version = None
        if module_name in directory.listdir("."):
            manifest = directory.readtext(join(module_name, "__manifest__.py"))
            version = ast.literal_eval(manifest)["version"]

        return version

    def fetch_module_from_source(self, module_name: str) -> FS:
        """
        Download a module from its source if needed and return the directory where it is located.
        :param module_name: Name of the module
        :return: An FS object pointing to the module location
        """
        source = self.modules_to_install[module_name]
        source_fs: FS

        if source["source_type"] == SOURCE_LOCAL_DIR:
            source_fs = OSFS(source["path"])
        elif source["source_type"] == SOURCE_LOCAL_ZIP:
            source_fs = ZipFS(source["path"])
        elif source["source_type"] == SOURCE_GIT:
            source_fs = self.download_from_git(
                module_name,
                source["url"],
                source.get("branch", self.odoo_version),
                source.get("path", ".")
            )

        return source_fs

    def download_from_git(self, module_name: str, url: str, branch: str, path: str = ".") -> OSFS:
        """
        Clone a git repository or find it in the source cache.
        :param module_name: name of the module being installed
        :param url: URL of the repository
        :param branch: branch of the desired module version
        :param path: path to the module inside the repository (default to '.')
        :return: an OSFS object pointing to the module location inside the repository
        """
        repo_dir_name = urlparse(url).path.replace("/", "_")

        if url in self.src_cache["git"]:
            self.pretty_print(module_name, "Repository found in cache", level=VERBOSE_FULL)
            repo = self.src_cache["git"][url]
            repo.checkout("refs/remotes/origin/{}".format(branch))
        else:
            self.pretty_print(module_name, "Cloning repository", level=VERBOSE_FULL)
            repo = pygit2.clone_repository(url, self.tmp_dir.getsyspath(repo_dir_name), checkout_branch=branch)

        self.src_cache["git"][url] = repo
        return OSFS(join(repo.workdir, path))

    def install_from_fs(self, name: str, source_fs: FS, path: str = ".", output_name: str = None):
        """
        Copy a module directory from where it is located to the installation directory.
        :param name: Name of the module
        :param source_fs: FS object pointing to the source location
        :param path: Path to the module directory from the source location root
        :param output_name: Name to give to the module's directory at installation
        """
        path_to_module = join(path, name)

        if name not in source_fs.listdir(path):
            raise InvalidModuleError(name,
                                     "Module directory not found - Given path should be the parent directory")
        if "__manifest__.py" not in source_fs.listdir(path_to_module):
            raise InvalidModuleError(name, "Manifest not found - Given path should be the parent directory")

        self.pretty_print(
            output_name,
            "Copying from {}".format(source_fs.desc(path_to_module)),
            level=VERBOSE_FULL
        )
        copy_dir(source_fs, path_to_module, self.install_dir, output_name or name)

        self.pretty_print(output_name, "Installed and up to date.", status=LOG_STATUS_OK, level=VERBOSE_NORMAL)

    def log(self, module_name: str, operation: str, force=False, extra: str = ""):
        """
        Log an operation in the history file.
        :param module_name: Name of the module
        :param operation: Type of the operation
        :param force: Whether the operation was performed with the force option or not
        :param extra: Extra information to log
        """
        log_line = "{0} - {1}{2}: {3} {4}\n".format(
            datetime.now().replace(microsecond=0),
            operation,
            " (forced)" if force else "",
            module_name,
            extra
        )
        self.history_file.write(log_line)

    def log_md(self, module: str, operation: str, old_version: str = None, new_version: str = None):
        """
        Log an operation in the markdown log file in human-readable format.
        :param module: Name of the module
        :param operation: Type of the operation
        :param old_version: Overwritten version of the module, in case of an update
        :param new_version: New version of the module, in case of an installation/update
        """
        current_log_content = self.changelog_file.read()

        # Look for the section concerning the current version, or write a scaffold if not found
        version = self.desc_version or datetime.today().strftime("%Y-%m-%d")
        log_index = current_log_content.find("## {}".format(version))
        if log_index >= 0:
            new_log_content = current_log_content[log_index:]
        else:
            new_log_content = "\n\n## {}\n\n**Added**\n\n\n**Updated**\n\n\n**Removed**\n\n".format(version)
            log_index = len(current_log_content)

        # Remove previous log entry concerning the module
        if module in new_log_content:
            new_log_content = re.sub(r"\n.*{}.*".format(module), "", new_log_content)

        # Append the new log line under the right operation type
        if operation == OPERATION_INSTALL:
            index = new_log_content.find("**Updated**") - 2
            log_line = "\n * {0} ({1})".format(module, new_version)
        elif operation == OPERATION_UPDATE:
            index = new_log_content.find("**Removed**") - 2
            log_line = "\n * {0} ({1} from {2})".format(module, new_version, old_version)
        elif operation == OPERATION_UNINSTALL:
            index = len(new_log_content) - 1
            log_line = "\n * {0}".format(module)

        new_log_content = "{0}{1}{2}".format(new_log_content[:index], log_line, new_log_content[index:])

        # Overwrite file with the updated logs
        old_log_content = current_log_content[:log_index]

        self.changelog_file.truncate()
        self.changelog_file.write(old_log_content + new_log_content)

    def list_external_dependencies(self, raw=False, modules: List[str] = None):
        """
        Show external dependencies of all installed modules.
        :param raw: Whether to print only python dependencies in a 'requirements.txt' format
        :param modules: If given, show dependencies of those modules only
        """
        dependencies = self.get_all_dependencies(modules=modules)

        if raw:
            for dep in dependencies.get("python", []):
                click.echo(dep)
        else:
            for type in dependencies:
                click.echo(type)
                for dep in dependencies[type]:
                    if type == "python":
                        dep_installed = self.check_python_dependency(dep)
                        click.echo("\t{0} {1}".format(dep, "(OK)" if dep_installed else "(missing)"))
                    else:
                        click.echo("\t{}".format(dep))

    def install_missing_dependencies(self, modules: List[str] = None):
        """
        Install all missing dependencies.
        :param modules: If given, install dependencies of those modules only
        """
        dependencies = self.get_all_dependencies(modules=modules)
        self.install_python_dependencies(dependencies.get("python", []))

    def get_all_dependencies(self, modules: List[str] = None) -> Dict[str, List[str]]:
        """
        Get all missing dependencies from the installed modules.
        :param modules: If given, return dependencies of those modules only
        :return: A dictionary containing a list of dependencies for each type
        """

        # Filter installed modules to keep the ones given
        modules = {mod: self.get_installed_modules()[mod] for mod in modules} if modules \
            else self.get_installed_modules()
        all_deps = {}

        for module in modules:
            module_deps = self.parse_dependencies(module, self.install_dir)
            for type, deps in module_deps.items():
                all_deps.setdefault(type, set()).update(set(deps))

        return all_deps

    @staticmethod
    def parse_dependencies(module_name: str, directory: FS) -> Dict[str, List[str]]:
        """
        Retrieve external dependencies from a module's manifest.
        :param module_name: Name of the module
        :param directory: Location of the module
        :return: A dictionary containing a list of dependencies for each type
        """
        manifest = directory.readtext(join(module_name, "__manifest__.py"))
        manifest_dict = ast.literal_eval(manifest)

        return manifest_dict.get("external_dependencies", {})

    @staticmethod
    def check_python_dependency(dependency: str) -> bool:
        """
        Check if a python dependency is satisfied i.e. if the python module is installed.
        :param dependency: Name of the python module
        :return: True if the module is installed, False otherwise
        """
        try:
            __import__(dependency)
        except ImportError:
            return False
        return True

    @staticmethod
    def install_python_dependencies(dependencies: List[str]):
        """
        Call pip to install the given python dependencies.
        :param dependencies: List of python modules to install
        """
        callable_pip.main("install", *dependencies)

    def pretty_print(self, module_name: str, message: str = "", status: str = LOG_STATUS_PENDING, level: int = 0):
        """
        Format and print a log to the console.
        :param module_name: Name of the module concerned
        :param message: Message to print
        :param status: Status of the log ('pending', 'ok', 'warning', 'error')
        :param level: Minimum verbose level to actually print the log (0, 1, 2)
        """
        if level <= self.verbose_level:
            if status == LOG_STATUS_OK:
                msg_color = "green"
            elif status == LOG_STATUS_WARNING:
                msg_color = "yellow"
            elif status == LOG_STATUS_ERROR:
                msg_color = "red"
            else:
                msg_color = "white"

            click.echo(
                click.style(module_name.ljust(30), fg="blue") +
                click.style(message, fg=msg_color)
            )


class InvalidModuleError(Exception):
    """
    Exception raised when a module is not valid, i.e. the directory is not found or it does not contain a manifest file.
    """
    def __init__(self, module_name: str, message: str):
        self.module_name = module_name
        self.message = message


if __name__ == '__main__':
    oam()
