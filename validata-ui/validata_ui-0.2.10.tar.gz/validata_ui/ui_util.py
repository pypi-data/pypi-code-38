"""
    Util UI functions
"""
from flask import flash


def flash_error(msg):
    """ Flash bootstrap error message """
    flash(msg, 'danger')


def flash_warning(msg):
    """ Flash bootstrap warning message """
    flash(msg, 'warning')


def flash_success(msg):
    """ Flash bootstrap success message """
    flash(msg, 'success')


def flash_info(msg):
    """ Flash bootstrap info message """
    flash(msg, 'info')
