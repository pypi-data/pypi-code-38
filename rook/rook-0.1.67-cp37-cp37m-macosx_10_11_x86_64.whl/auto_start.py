"""This module initializes the Rook using default settings when imported."""
import os


def _auto_start():
    disable = os.environ.get('ROOKOUT_DISABLE_AUTOSTART', None)

    if disable is not None and disable != '0':
        return

    import rook
    rook.start()


_auto_start()
