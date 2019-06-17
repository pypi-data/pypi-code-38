# -*- coding: utf-8 -*-

"""Console script for osprey_design."""
import sys
import click

from osprey_design import navigation
from osprey_design.globals import ATTR_BUTTON_NORMAL, ATTR_BUTTON_SELECT, ATTR_HEADER, ATTR_FOOTER, ATTR_EDIT_NORMAL, \
    ATTR_EDIT_SELECT, ATTR_QUESTION, ATTR_WHITE_BG, ATTR_BLACK_BG, ATTR_DARK_RED_BG, ATTR_DARK_GREEN_BG, \
    ATTR_DARK_BLUE_BG
from osprey_design.pages.welcome_page import WelcomePage
import osprey_design.globals


@click.command()
def main(args=None):
    palette = [
        (ATTR_BUTTON_NORMAL, 'white', 'dark blue', 'standout'),
        (ATTR_BUTTON_SELECT, 'white', 'dark green'),
        (ATTR_HEADER, 'white', 'dark red', 'bold'),
        (ATTR_FOOTER, 'white', 'dark red', 'bold'),
        (ATTR_EDIT_NORMAL, 'dark red', 'light gray'),
        (ATTR_EDIT_SELECT, 'light cyan', 'white'),
        (ATTR_QUESTION, 'white', 'dark red', 'standout'),
        (ATTR_WHITE_BG, 'black', 'white'),
        (ATTR_BLACK_BG, 'white', 'black'),
        (ATTR_DARK_RED_BG, 'white', 'dark red', 'standout'),
        (ATTR_DARK_GREEN_BG, 'white', 'dark green', 'standout'),
        (ATTR_DARK_BLUE_BG, 'white', 'dark blue', 'standout')
    ]

    loop = navigation.init()
    loop.screen.register_palette(palette)
    navigation.push_page(WelcomePage())
    loop.run()  # Loop finishes when 'ExitMainLoop' exception is raised

    if osprey_design.globals.design_path:
        print(f'Saved design to {osprey_design.globals.design_path}')


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
