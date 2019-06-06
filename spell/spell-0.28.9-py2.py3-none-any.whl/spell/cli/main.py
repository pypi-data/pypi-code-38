from functools import wraps
import logging
import os
import sys
import platform
import distutils.spawn

import click
import yaml

from spell.api.client import APIClient
from spell.cli import api_constants
from spell import version
from spell.cli.adapters import UpdateNoticeAdapter
from spell.cli.constants import DEFAULT_SUPPORTED_OPTIONS
from spell.cli.utils import HiddenOption
import spell.cli.utils.sentry as sentry
from spell.cli.log import logger, configure_logger
from spell.cli.exceptions import (
    ExitException,
    api_client_exception_handler,
)
from spell.configs.config_handler import ConfigHandler, ConfigException, default_config_dir
from spell.cli.commands.archive import archive
from spell.cli.commands.cp import cp
from spell.cli.commands.feedback import feedback
from spell.cli.commands.info import info
from spell.cli.commands.keys import keys
from spell.cli.commands.kill import kill
from spell.cli.commands.link import link
from spell.cli.commands.login import login
from spell.cli.commands.logout import logout
from spell.cli.commands.logs import logs
from spell.cli.commands.ls import ls
from spell.cli.commands.me import me
from spell.cli.commands.owner import owner
from spell.cli.commands.passwd import passwd
from spell.cli.commands.ps import ps
from spell.cli.commands.repos import repos
from spell.cli.commands.rm import rm
from spell.cli.commands.run import run
from spell.cli.commands.model_servers import model_servers
from spell.cli.commands.stats import stats
from spell.cli.commands.status import status
from spell.cli.commands.stop import stop
from spell.cli.commands.unlink import unlink
from spell.cli.commands.upload import upload
from spell.cli.commands.workflow import workflow
from spell.cli.commands.hyper import hyper
from spell.cli.commands.cluster import cluster
from spell.cli.commands.jupyter import jupyter


def requires_login(command):
    '''add requirement for existing global config file to a click.Command object'''

    # wrap the click.Command callback to require that user has logged in
    def req_config(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            config = click.get_current_context().obj["config_handler"].config
            if config is None or config.token is None:
                raise ExitException('No login session found. Please log in ("spell login").')
            else:
                f(*args, **kwds)
        return wrapper
    command.callback = req_config(command.callback)
    return command


def get_supported_options_init(ctx):
    def get_supported_options(config_type):
        """Retrieve supported configuration options from API"""
        # Create the global cache path
        cache_path = os.path.join(ctx.obj["config_handler"].spell_dir, "cache")
        try:
            os.makedirs(cache_path)
        except OSError:
            pass

        so_cache_path = os.path.join(cache_path, "supported_options")
        client = ctx.obj["client"]
        # Try to retrieve options from the API
        try:
            with api_client_exception_handler():
                opts = client.get_options(config_type, cache_path=so_cache_path)
                values = opts["values"] if opts["values"] is not None else []
                return values, opts.get("default")
        except ExitException:
            pass
        # Fall back to the cached supported options file
        try:
            with open(so_cache_path) as cache_file:
                opts = yaml.safe_load(cache_file)[config_type]
                return opts["values"], opts.get("default")
        except (IOError, KeyError):
            pass
        # Fall back to our best guess, and finally nil-values if we can't find anything
        opts = DEFAULT_SUPPORTED_OPTIONS.get(config_type, {"values": []})
        return opts["values"], opts.get("default")

    return get_supported_options


@click.command(name="help", help="Display help information")
@click.pass_context
def help(ctx):
    click.echo(ctx.parent.get_help())


@click.group(context_settings={"max_content_width": 120})
@click.pass_context
@click.option("--api-url", cls=HiddenOption, type=str,
              default="https://api.spell.run",
              help="url of the spell api server")
@click.option("--api-version", cls=HiddenOption, type=str,
              default="v1")
@click.option("--spell-dir", cls=HiddenOption, type=click.Path(),
              default=default_config_dir)
@click.option("--verbose", cls=HiddenOption,
              is_flag=True, default=False)
@click.option("--debug", cls=HiddenOption,
              is_flag=True, default=False)
@click.help_option("--help", "-h")
@click.version_option(version=version.__version__)
def cli(ctx, api_url, api_version, spell_dir, verbose, debug):
    if distutils.spawn.find_executable("git") is None:
        raise ExitException("Unable to find git, for installation instructions see "
                            "https://git-scm.com/")

    level = logging.WARNING
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    configure_logger(logger, level)
    ctx.obj = {}
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["interactive"] = sys.stdout.isatty()
    try:
        ctx.obj["utf8"] = sys.stdout.encoding.lower() == "utf-8"
    except AttributeError:
        ctx.obj["utf8"] = False

    # set up platform tags for sentry
    sentry.set_tag("platform_system", platform.system())
    sentry.set_tag("platform_version", platform.version())
    sentry.set_tag("platform_release", platform.release())
    sentry.set_tag("py_major_ver", sys.version_info[0])
    sentry.set_tag("py_minor_ver", sys.version_info[1])
    sentry.set_tag("py_micro_ver", sys.version_info[2])
    sentry.set_tag("spell_version", version.__version__)

    # set up args for base API client
    ctx.obj["client_args"] = client_args = {
        "base_url": api_url,
        "version_str": api_version,
        "adapter": UpdateNoticeAdapter(),
    }

    # parameterize get_supported_options with ctx and pass it off to the api_constants module
    api_constants.get_supported_options = get_supported_options_init(ctx)

    # attempt to load global config file
    ctx.obj["config_handler"] = cfg_handler = ConfigHandler(spell_dir, logger=logger)
    try:
        cfg_handler.load_config_from_file()
        config = cfg_handler.config
    except ConfigException:
        config = None

    if config:
        ctx.obj["token"] = client_args["token"] = config.token
        ctx.obj["owner"] = client_args["owner"] = config.owner or config.user_name
        sentry.set_user({
            "username": config.user_name,
            "email": config.email,
        })

    ctx.obj["client"] = APIClient(**client_args)


cli.add_command(help)
cli.add_command(login)
cli.add_command(requires_login(logout))
cli.add_command(requires_login(me))
cli.add_command(requires_login(owner))
cli.add_command(requires_login(keys))
cli.add_command(requires_login(archive))
cli.add_command(requires_login(rm))
cli.add_command(requires_login(run))
cli.add_command(requires_login(ps))
cli.add_command(requires_login(link))
cli.add_command(requires_login(logs))
cli.add_command(requires_login(info))
cli.add_command(requires_login(ls))
cli.add_command(requires_login(kill))
cli.add_command(requires_login(cp))
cli.add_command(requires_login(passwd))
cli.add_command(requires_login(feedback))
cli.add_command(requires_login(stats))
cli.add_command(requires_login(model_servers))
cli.add_command(requires_login(status))
cli.add_command(requires_login(unlink))
cli.add_command(requires_login(upload))
cli.add_command(requires_login(stop))
cli.add_command(requires_login(repos))
cli.add_command(requires_login(workflow))
cli.add_command(requires_login(hyper))
cli.add_command(requires_login(cluster))
cli.add_command(requires_login(jupyter))


def main():
    # Configure the logger
    configure_logger(logger, logging.WARNING)

    # Copy the environment
    env = os.environ.copy()
    is_nested_env = env.get("_SPELL_LANG_ENV") == "true"

    try:
        if is_nested_env:
            locale = env["LANG"]
            msg = ("Using inferred locale {locale}. Please explicitly specify a locale by "
                   "setting the LC_ALL and LANG environment variables.\n")
            if os.name == "posix":
                msg += ("    export LC_ALL={locale}\n"
                        "    export LANG={locale}\n"
                        "Append these lines to your bash profile to persist them between terminal sessions.\n")
            msg += "\n"
            logger.warn(msg.format(locale=locale))
        cli()
    except RuntimeError as e:
        """
        This code is taken from the click package to find appropriate locales with some minor changes to
        store the found locale and also check for the en_US.UTF-8 locale
        https://github.com/pallets/click/blob/7eb990fab5783b32c7028b0aa8a752e6862d0997/click/_unicodefun.py

        Copyright (c) 2001-2006 Gregory P. Ward.  All rights reserved.
        Copyright (c) 2002-2006 Python Software Foundation.  All rights reserved.
        Copyright (c) 2014 by Armin Ronacher. Some rights reserved.

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are
        met:

            * Redistributions of source code must retain the above copyright
              notice, this list of conditions and the following disclaimer.

            * Redistributions in binary form must reproduce the above
              copyright notice, this list of conditions and the following
              disclaimer in the documentation and/or other materials provided
              with the distribution.

            * The names of the contributors may not be used to endorse or
              promote products derived from this software without specific
              prior written permission.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
        "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
        LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
        A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
        OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
        SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
        LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
        DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        """
        if is_nested_env:
            sentry.capture_exception(e)
            logger.error("{}: {}".format(type(e).__name__, str(e)))
            sys.exit(1)

        # ========== START CLICK CODE ==========
        good_locales = []
        c_utf8 = ""
        en_utf8 = ""
        if os.name == "posix":
            import subprocess
            try:
                rv = subprocess.Popen(['locale', '-a'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE).communicate()[0]
            except OSError:
                rv = b''

            # Make sure we're operating on text here.
            if isinstance(rv, bytes):
                rv = rv.decode('ascii', 'replace')

            for line in rv.splitlines():
                locale = line.strip()
                if locale.lower().endswith(('.utf-8', '.utf8')):
                    good_locales.append(locale)
                    if locale.lower() in ('c.utf8', 'c.utf-8'):
                        c_utf8 = locale
                    if locale.lower() in ('en_us.utf-8', 'en_us.utf8'):
                        en_utf8 = locale
        # ========== END CLICK CODE ==========

        if c_utf8:
            # Try using the C.UTF-8 locale if it exists
            env["LANG"] = "C.UTF-8"
            env["LC_ALL"] = "C.UTF-8"
        elif en_utf8:
            # Fall back to the US English locale
            env["LANG"] = "en_US.UTF-8"
            env["LC_ALL"] = "en_US.UTF-8"
        elif good_locales:
            # Fall back to the first available UTF-8 locale
            env["LANG"] = good_locales[0]
            env["LC_ALL"] = good_locales[0]
        else:
            logger.error(str(e))
            sys.exit(1)
        env["_SPELL_LANG_ENV"] = "true"
        os.execvpe(sys.executable, [sys.executable] + sys.argv, env)
    except Exception as e:
        sentry.capture_exception(e)
        strerror = "{}: {}".format(type(e).__name__, str(e))
        logger.error("Fatal exception: {}.\nPlease contact support@spell.run if the problem persists.".format(strerror))
        sys.exit(1)


if __name__ == "__main__":
    main()
