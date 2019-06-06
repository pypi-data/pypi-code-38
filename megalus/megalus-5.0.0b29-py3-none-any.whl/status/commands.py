"""Status command module."""
import sys

import click
from blessed import Terminal
from colorama import Style

from megalus.main import Megalus
from megalus.status.dashboard import Dashboard


@click.command()
@click.option('--all', is_flag=True)
@click.pass_obj
def status(meg: Megalus, all: bool) -> None:
    """Return docker services status.

    :param all: Show all services
    :param meg: Megalus instance
    :return: None
    """
    dashboard = Dashboard(meg)
    term = Terminal()
    try:
        with term.fullscreen():
            with term.hidden_cursor():
                with term.cbreak():
                    while True:
                        ui = dashboard.get_layout(term, all)
                        ui.display()
                        key_pressed = term.inkey(timeout=5)
                        if 'd' in key_pressed.lower():
                            diff = not diff
                        if 'q' in key_pressed.lower():
                            raise KeyboardInterrupt

    except KeyboardInterrupt:
        print(term.color(0))
        sys.exit(0)
    except BaseException as exc:
        print(term.exit_fullscreen)
        print(Style.RESET_ALL)
        raise exc
