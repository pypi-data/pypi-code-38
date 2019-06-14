"""User interface module for symbol_please."""
import os

import gi

from symbol_please.ui.profile_select_window import ProfileSelectWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa: E402

STYLESHEET = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'res', 'style.css')


def main(config):
    """Initialize the UI."""
    style_provider = Gtk.CssProvider()
    with open(STYLESHEET, 'rb') as f:
        style_provider.load_from_data(f.read())

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = ProfileSelectWindow(config)
    win.show_all()

    try:
        Gtk.main()
    finally:
        win.on_exit()

    return 0
