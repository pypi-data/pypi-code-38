#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
import click
# DON'T PUT HERE ANY MISSINGLINK import directly, use local imports


def main():
    from missinglink.commands import add_commands, cli
    from missinglink.commands.global_cli import self_update, set_pre_call_hook, setup_sentry_sdk, setup_pre_call
    from missinglink.core.exceptions import MissingLinkException
    from missinglink.legit.gcp_services import GooglePackagesMissing, GoogleAuthError

    setup_sentry_sdk()
    set_pre_call_hook(setup_pre_call)

    if sys.argv[0].endswith('/mali') and not os.environ.get('ML_DISABLE_DEPRECATED_WARNINGS'):
        click.echo('instead of mali use ml (same tool with a different name)', err=True)

    if os.environ.get('MISSINGLINKAI_ENABLE_SELF_UPDATE'):
        self_update()

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


if __name__ == "__main__":
    main()
