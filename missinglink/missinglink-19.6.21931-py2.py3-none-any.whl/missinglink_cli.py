#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
import click
# DON'T PUT HERE ANY MISSINGLINK import directly, use local imports


# This function is duplicate as we cannot put it in a shared file and import
# The import of the shared file (which will be under missinglink.commands
# will trigger the load of the missinglink namespace that will load the missinglink.sdk
# and we will missing the by the time the function below will be executed the
# global exception hook will be already installed by the SDK
def disable_sdk_disable_exception_hook():
    os.environ['MISSINGLINKAI_DISABLE_EXCEPTION_HOOK'] = '1'
    os.environ['ML_DISABLE_LOGGING_HOOK'] = '1'


def _main_cli():
    from missinglink.commands import add_commands, cli
    from missinglink.core.exceptions import MissingLinkException
    from missinglink.legit.gcp_services import GooglePackagesMissing, GoogleAuthError

    add_commands()
    try:
        cli()
    except GooglePackagesMissing:
        click.echo('you need to run "pip install missinglink[gcp]" in order to run this command', err=True)
        sys.exit(1)
    except GoogleAuthError:
        click.echo('Google default auth credentials not found, run gcloud auth application-default login', err=True)
        sys.exit(1)
    except MissingLinkException as ex:
        click.echo(ex, err=True)
        sys.exit(1)


def _warn_if_using_mali():
    if sys.argv[0].endswith('/mali') and not os.environ.get('ML_DISABLE_DEPRECATED_WARNINGS'):
        click.echo('instead of mali use ml (same tool with a different name)', err=True)


def _self_update_if_needed():
    if os.environ.get('MISSINGLINKAI_ENABLE_SELF_UPDATE'):
        from missinglink.commands.global_cli import self_update

        self_update()


def main():
    disable_sdk_disable_exception_hook()

    from missinglink.commands.ml_sentry import sentry_capture_exceptions

    @sentry_capture_exceptions
    def run_main():
        from missinglink.commands.global_cli import set_pre_call_hook, setup_pre_call

        set_pre_call_hook(setup_pre_call)

        _warn_if_using_mali()
        _self_update_if_needed()

        _main_cli()

    run_main()


if __name__ == "__main__":
    main()
