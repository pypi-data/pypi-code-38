# -*- coding: utf-8 -*-

"""Console script for osprey_design."""
import sys
import click

from osprey_design import navigation
from osprey_design.pages.welcome_page import WelcomePage
from .globals import *


@click.command()
def main(args=None):
    palette = [
        (ATTR_BUTTON_NORMAL, 'white', 'dark blue', 'standout'),
        (ATTR_BUTTON_SELECT, 'white', 'dark green'),
        (ATTR_HEADER, 'white', 'dark red', 'bold'),
        (ATTR_FOOTER, 'white', 'dark red', 'bold'),
        (ATTR_EDIT_NORMAL, 'light gray', 'white'),
        (ATTR_EDIT_SELECT, 'black', 'white'),
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
    loop.run()


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
