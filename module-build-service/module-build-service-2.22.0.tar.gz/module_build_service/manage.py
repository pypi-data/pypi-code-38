# -*- coding: utf-8 -*-
# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Matt Prahl <mprahl@redhat.com> except for the test functions

from __future__ import print_function
from flask_script import Manager, prompt_bool
from functools import wraps
import flask_migrate
import logging
import os
import getpass
import textwrap

from werkzeug.datastructures import FileStorage
from module_build_service import app, conf, db, create_app
from module_build_service import models
from module_build_service.utils import (
    submit_module_build_from_yaml,
    load_local_builds,
    load_mmd_file,
    import_mmd,
    import_builds_from_local_dnf_repos,
)
from module_build_service.errors import StreamAmbigous
import module_build_service.messaging
import module_build_service.scheduler.consumer


manager = Manager(create_app)
help_args = ("-?", "--help")
manager.help_args = help_args
migrations_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              'migrations')
migrate = flask_migrate.Migrate(app, db, directory=migrations_dir)
manager.add_command("db", flask_migrate.MigrateCommand)
manager.add_option("-d", "--debug", dest="debug", action="store_true")
manager.add_option("-v", "--verbose", dest="verbose", action="store_true")
manager.add_option("-q", "--quiet", dest="quiet", action="store_true")


def console_script_help(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        import sys

        if any([arg in help_args for arg in sys.argv[1:]]):
            command = os.path.basename(sys.argv[0])
            print(textwrap.dedent(
                """\
                    {0}

                    Usage: {0} [{1}]

                    See also:
                    mbs-manager(1)
                """).strip().format(command, "|".join(help_args))
            )
            sys.exit(2)
        r = f(*args, **kwargs)
        return r

    return wrapped


@console_script_help
@manager.command
def upgradedb():
    """ Upgrades the database schema to the latest revision
    """
    app.config["SERVER_NAME"] = "localhost"
    # TODO: configurable?
    migrations_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "migrations")
    with app.app_context():
        flask_migrate.upgrade(directory=migrations_dir)


@manager.command
def cleardb():
    """ Clears the database
    """
    models.ModuleBuild.query.delete()
    models.ComponentBuild.query.delete()


@console_script_help
@manager.command
def import_module(mmd_file):
    """ Imports the module from mmd_file
    """
    mmd = load_mmd_file(mmd_file)
    import_mmd(db.session, mmd)


@manager.option("--stream", action="store", dest="stream")
@manager.option("--file", action="store", dest="yaml_file")
@manager.option("--srpm", action="append", default=[], dest="srpms", metavar="SRPM")
@manager.option("--skiptests", action="store_true", dest="skiptests")
@manager.option("--offline", action="store_true", dest="offline")
@manager.option("-l", "--add-local-build", action="append", default=None, dest="local_build_nsvs")
@manager.option("-s", "--set-stream", action="append", default=[], dest="default_streams")
@manager.option(
    "-r", "--platform-repo-file", action="append", default=[], dest="platform_repofiles"
)
@manager.option("-p", "--platform-id", action="store", default=None, dest="platform_id")
def build_module_locally(
    local_build_nsvs=None,
    yaml_file=None,
    srpms=None,
    stream=None,
    skiptests=False,
    default_streams=None,
    offline=False,
    platform_repofiles=None,
    platform_id=None,
):
    """ Performs local module build using Mock
    """
    if "SERVER_NAME" not in app.config or not app.config["SERVER_NAME"]:
        app.config["SERVER_NAME"] = "localhost"

        if app.config["RESOLVER"] == "db":
            raise ValueError(
                "Please set RESOLVER to 'mbs' in your configuration for local builds.")

    with app.app_context():
        conf.set_item("system", "mock")
        conf.set_item("base_module_repofiles", platform_repofiles)

        # Use our own local SQLite3 database.
        confdir = os.path.abspath(os.getcwd())
        dbdir = \
            os.path.abspath(os.path.join(confdir, "..")) if confdir.endswith("conf") else confdir
        dbpath = "/{0}".format(os.path.join(dbdir, ".mbs_local_build.db"))
        dburi = "sqlite://" + dbpath
        app.config["SQLALCHEMY_DATABASE_URI"] = dburi
        conf.set_item("sqlalchemy_database_uri", dburi)
        if os.path.exists(dbpath):
            os.remove(dbpath)

        db.create_all()
        if offline:
            import_builds_from_local_dnf_repos(platform_id)
        load_local_builds(local_build_nsvs)

        params = {}
        params["local_build"] = True
        params["default_streams"] = {}
        for ns in default_streams:
            n, s = ns.split(":")
            params["default_streams"][n] = s
        if srpms:
            params["srpms"] = srpms

        username = getpass.getuser()
        if not yaml_file or not yaml_file.endswith(".yaml"):
            raise IOError("Provided modulemd file is not a yaml file.")

        yaml_file_path = os.path.abspath(yaml_file)
        with open(yaml_file_path) as fd:
            filename = os.path.basename(yaml_file)
            handle = FileStorage(fd)
            handle.filename = filename
            try:
                modules_list = submit_module_build_from_yaml(
                    username, handle, params, stream=str(stream), skiptests=skiptests
                )
            except StreamAmbigous as e:
                logging.error(str(e))
                logging.error("Use '-s module_name:module_stream' to choose the stream")
                return

        stop = module_build_service.scheduler.make_simple_stop_condition(db.session)

        # Run the consumer until stop_condition returns True
        module_build_service.scheduler.main([], stop)

        if any(module.state == models.BUILD_STATES["failed"] for module in modules_list):
            raise RuntimeError("Module build failed")


@manager.option(
    "identifier",
    metavar="NAME:STREAM[:VERSION[:CONTEXT]]",
    help="Identifier for selecting module builds to retire",
)
@manager.option(
    "--confirm",
    action="store_true",
    default=False,
    help="Perform retire operation without prompting",
)
def retire(identifier, confirm=False):
    """ Retire module build(s) by placing them into 'garbage' state.
    """
    # Parse identifier and build query
    parts = identifier.split(":")
    if len(parts) < 2:
        raise ValueError("Identifier must contain at least NAME:STREAM")
    if len(parts) >= 5:
        raise ValueError("Too many parts in identifier")

    filter_by_kwargs = {"state": models.BUILD_STATES["ready"], "name": parts[0], "stream": parts[1]}

    if len(parts) >= 3:
        filter_by_kwargs["version"] = parts[2]
    if len(parts) >= 4:
        filter_by_kwargs["context"] = parts[3]

    # Find module builds to retire
    module_builds = db.session.query(models.ModuleBuild).filter_by(**filter_by_kwargs).all()

    if not module_builds:
        logging.info("No module builds found.")
        return

    logging.info("Found %d module builds:", len(module_builds))
    for build in module_builds:
        logging.info("\t%s", ":".join((build.name, build.stream, build.version, build.context)))

    # Prompt for confirmation
    is_confirmed = confirm or prompt_bool("Retire {} module builds?".format(len(module_builds)))
    if not is_confirmed:
        logging.info("Module builds were NOT retired.")
        return

    # Retire module builds
    for build in module_builds:
        build.transition(conf, models.BUILD_STATES["garbage"], "Module build retired")
    db.session.commit()
    logging.info("Module builds retired.")


@console_script_help
@manager.command
def run(host=None, port=None, debug=None):
    """ Runs the Flask app, locally.
    """
    host = host or conf.host
    port = port or conf.port
    debug = debug or conf.debug

    logging.info("Starting Module Build Service frontend")

    app.run(host=host, port=port, debug=debug)


def manager_wrapper():
    manager.run()


if __name__ == "__main__":
    manager_wrapper()
