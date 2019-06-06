# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os
import pathlib
import shutil
from collections import OrderedDict
from contextlib import closing

import datapool

from ..config import Config, MagicConfig, read_ini, write_ini
from ..database import connect_to_db
from ..errors import InvalidOperationError
from ..julia_runner import JuliaRunner
from ..logger import resolve_logger_config_path
from ..matlab_runner import MatlabRunner
from ..python_runner import PythonRunner
from ..r_runner import RRunner
from ..utils import abs_folder, find_executable, iter_to_list


def guess_config(known_config):
    """you can provide known config settings as

       known_config = { "db.connection_string:"...",
                        "worker.port": 3333 }

       which will overrung the settings we guess in this function
    """

    assert isinstance(known_config, dict)

    from datapool import __version__

    executables = ("matlab", "R", "julia", "python3")
    sections = ("matlab", "r", "julia", "python")

    messages = []

    # we use OrderedDict to guarantee stable ordering of entries in config
    # file(s)
    config = OrderedDict()
    config["datapool.__version__"] = __version__
    for executable, section in zip(executables, sections):
        path = find_executable(executable, "")
        if not path:
            messages.append("{!r} not found on $PATH".format(executable))
        config["{}.executable".format(section)] = path

    config.update(known_config)

    return default_config(config), messages


def default_config(
    known_config,
    default_connection_string="postgresql://user:password@127.0.0.1:5432/datapool",
    default_pid_path="/var/run/datapool.pid",
    default_local_user_folder=".datapool",
):
    """you can overwrite with calls like:

        default_config(db.connections_string="....",
                       worker.port=3333)
    """

    def set_defaults():

        config = MagicConfig()

        config.db.connection_string = default_connection_string

        config.backup_landing_zone.folder = ""

        config.r.extension = ".r"

        config.matlab.extension = ".m"

        config.julia.extension = ".jl"
        config.julia.version = "1.0.1"

        config.python.extension = ".py"

        config.logging.config_file = "./logging_config.yaml"
        config.log_receiver.port = 5559

        config.worker.port = 5555
        config.worker.count = 5

        config.http_server.port = 8000

        config.conversion.block_size = 20000

        if os.getpid() == 0:
            config.server.pid_file = default_pid_path
        else:
            folder = pathlib.Path("~").expanduser() / default_local_user_folder
            folder.mkdir(parents=True, exist_ok=True)
            config.server.pid_file = str(folder / "datapool.pid")

        return config

    def update_config(config, known_config):

        for key, value in known_config.items():
            fields = key.split(".")
            if len(fields) == 2:
                section, field = fields
                setattr(getattr(config, section), field, value)
            elif len(fields) == 1:
                field = fields[0]
                assert field.startswith("__")
                assert field.endswith("__")
                setattr(config, field, value)

    config = set_defaults()
    update_config(config, known_config)

    return config


def config_for_develop_db(landing_zone_folder):
    config = MagicConfig()
    path = os.path.join(landing_zone_folder, ".develop.db")
    config.connection_string = "sqlite+pysqlite:///{}".format(path)
    return config, path


def check_folder(folder):

    if not os.path.exists(folder):
        return "folder '{}' does not exist".format(folder)

    try:
        existing_files = os.listdir(folder)
    except IOError:
        return "can not list content of folder '{}'".format(folder)

    existing_files = [f for f in existing_files if not f.startswith(".")]

    if existing_files:
        return "folder is not empty '{}'".format(folder)

    marker_file = os.path.join(folder, ".marker")
    try:
        open(marker_file, "w").close()
    except IOError:
        return "can not write to folder '{}'".format(folder)

    os.remove(marker_file)
    return None


@iter_to_list
def check_config(config):

    yield from _check_landing_zone(config)
    yield from _check_backup_landing_zone(config)
    yield from _check_db(config)
    yield from _check_logging(config)
    yield from _check_runners(config)
    yield from _check_pid_file(config)
    yield from _check_worker(config)
    yield from _check_webserver(config)
    yield from _check_conversion(config)


def _check_landing_zone(config):
    errors = _check(config, "landing_zone", "folder", str, False)
    yield from errors

    if not errors and config.landing_zone.folder:
        yield True, "- check landing zone '{}'".format(config.landing_zone.folder)
        msg = check_folder(config.landing_zone.folder)
        if msg is not None:
            yield False, "- {}".format(msg)


def _check_backup_landing_zone(config):
    errors = _check(config, "backup_landing_zone", "folder", str, True)
    yield from errors

    if not errors and config.backup_landing_zone.folder:
        yield True, "- check backup folder '{}'".format(
            config.backup_landing_zone.folder
        )
        msg = check_folder(config.backup_landing_zone.folder)
        if msg is not None:
            yield False, "- {}".format(msg)


def _check_db(config):

    errors = _check(config, "db", "connection_string", str, False)
    yield from errors

    if not errors:
        try:
            yield True, "- try to connect to db"
            connect_to_db(config.db)
            yield True, "  - connected to db"
        except Exception as e:
            yield False, "  - {}".format(e)


def _check_logging(config):
    errors = _check(config, "logging", "config_file", str, "")
    yield from errors

    if not errors and not os.path.exists(resolve_logger_config_path(config)):
        yield (
            False,
            "- configured config logging config {} does not exist".format(
                config.logging.config_file
            ),
        )

    errors = _check(config, "log_receiver", "port", int)
    yield from errors

    if not errors:
        port = config.log_receiver.port
        if is_port_used(port):
            yield False, "- configured log_receiver port {} is already in use".format(
                port
            )


def _check_pid_file(config):
    pid_file = config.server.pid_file
    if os.path.exists(pid_file):
        if not os.access(pid_file, os.W_OK):
            yield False, "- can not write to pid file at {}".format(pid_file)
    else:
        folder = os.path.dirname(pid_file)
        if not os.path.exists(folder):
            yield False, "- folder {} for pid file {} does not exist".format(
                folder, pid_file
            )
        else:
            try:
                open(pid_file, "w").close()
                os.unlink(pid_file)
            except IOError:
                yield False, "- can not write to pid file {}".format(pid_file)


def _check_worker(config):
    errors = _check(config, "worker", "port", int)
    yield from errors

    if not errors:
        port = config.worker.port
        if is_port_used(port):
            yield False, "- configured worker port {} is already in use".format(port)

    errors = _check(config, "worker", "count", int)
    yield from errors
    if not errors and config.worker.count <= 0:
        yield (
            False,
            "- configured worker count value {} is not greater than zero".format(
                config.worker.count
            ),
        )


def _check_webserver(config):
    errors = _check(config, "http_server", "port", int)
    yield from errors
    if not errors:
        port = config.http_server.port
        if is_port_used(port):
            yield False, "- configured webserver port {} is already in use".format(port)


def _check_conversion(config):
    errors = _check(config, "conversion", "block_size", int)
    yield from errors
    if not errors:
        block_size = config.conversion.block_size
        if block_size < 1000:
            yield False, "- configured convesion block_size {} must be >= 1000".format(
                block_size
            )


@iter_to_list
def _check(config, section, field, type, maybe_empty=True):
    if section not in config.keys():
        yield False, "- section {} missing".format(section)
    if field not in config[section].keys():
        yield False, "- field {} in section {} missing".format(field, section)

    value = config[section][field]
    if not maybe_empty and value == "":
        yield False, "- field {} in section {} has no value set".format(field, section)
    if not isinstance(value, type):
        yield (
            False,
            "- field {} in section {} is not of type {}".format(
                field, section, type.__name__
            ),
        )


def _check_runners(config):

    yield from _check_executable("r", "R", config, RRunner)
    yield from _check_executable("python", "python", config, PythonRunner)
    yield from _check_executable("matlab", "matlab", config, MatlabRunner)
    julia_ok = True
    for ok, message in _check_executable("julia", "julia", config, JuliaRunner):
        julia_ok = julia_ok and ok
        yield ok, message

    if julia_ok and config.julia.executable:
        m = JuliaRunner(config.julia.executable)
        try:
            m.start_interpreter()
        except OSError as e:
            yield False, "- can not start julia a second time: {}".format(e)
        else:
            actual_version = m.get_julia_version_tuple()
            configured_version = tuple(map(int, config.julia.version.split(".")))

            if configured_version != actual_version:
                yield False, (
                    "- julia interpreter is of version {}, configured is {}"
                    "".format(actual_version, configured_version)
                )
            else:
                yield True, "- checked julia version."


def _check_executable(section, name, config, runner):
    errors = _check(config, section, "extension", str, False)
    yield from errors

    errors = _check(config, section, "executable", str)
    yield from errors
    if errors:
        return

    executable = getattr(config, section).executable

    if executable == "":
        yield True, "- {} not configured, skip tests".format(name)
    else:
        yield True, "- check {} configuration + code execution".format(name)
        m = runner(executable)
        try:
            m.start_interpreter()
            yield True, "- {} interpreter works".format(name)
        except OSError as e:
            yield False, "  - could not start {} from {}: {}".format(
                name, executable, e
            )


def is_port_used(port):
    import socket

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def config_folder():
    etc = os.environ.get("ETC", "/etc")
    data_pool_folder = os.path.join(etc, "datapool")
    return os.path.abspath(data_pool_folder)


def config_ini_file_path():
    folder = config_folder()
    path = os.path.join(folder, "datapool.ini")
    return path


def init_config(landing_zone_folder, sqlite_db=False, overwrite=False):

    config_folder_ = config_folder()

    if os.path.exists(config_folder_):
        if not overwrite:
            raise InvalidOperationError(
                "datapool folder {} already exists".format(config_folder_)
            )
    else:
        try:
            os.makedirs(config_folder_)
        except PermissionError:
            raise InvalidOperationError(
                "creation of {} failed. try sudo.".format(config_folder_)
            )

    path = config_ini_file_path()

    # we use OrderedDict to guarantee stable ordering of entries in config
    # file(s)
    known_settings = OrderedDict([("landing_zone.folder", landing_zone_folder)])
    if sqlite_db:
        db_path = os.path.join(landing_zone_folder, ".simple.db")
        known_settings["db.connection_string"] = "sqlite+pysqlite:///{}".format(db_path)

    config, messages = guess_config(known_settings)

    try:
        write_ini(config, path)
    except PermissionError:
        raise InvalidOperationError("could not write {}. try sudo.".format(path))

    default_log_config = os.path.join(
        abs_folder(__file__), "..", "cmdline_logging.yaml"
    )
    shutil.copy(
        default_log_config, os.path.join(config_folder_, config.logging.config_file)
    )

    return config_folder_, messages


def read_config(**variable_settings):
    path = config_ini_file_path()
    if os.path.exists(path):
        return migrate(read_ini(path, variable_settings))
    else:
        return None


def write_config(config):
    assert "__file__" in config.keys()
    write_ini(config, config.__file__)


def migrate(config):

    # versioned config was introduced in datapool 0.4.2

    if "datapool" not in config:
        config.datapool = Config()

    if "__version__" not in config.datapool:
        config.datapool.__version__ = "0.4.2"

    v_tuple = tuple(map(int, config.datapool.__version__.split(".")))

    if v_tuple <= (0, 4, 2):
        # http server was introduces post 0.4.2
        config.http_server = Config()
        config.http_server["port"] = 8000
    if v_tuple <= (0, 4, 7):
        config.conversion = Config()
        config.conversion["block_size"] = 5000
    return config
