"""
Systemd services
================

This module provides low-level tools for managing `systemd`_ services.

.. _systemd: http://www.freedesktop.org/wiki/Software/systemd

"""
from __future__ import print_function

from fabric.api import hide, settings

from burlap.utils import run_as_root


def action(action, service):
    return run_as_root('systemctl %s %s.service' % (action, service,))


def enable(service):
    """
    Enable a service.

    ::

        burlap.enable('httpd')

    .. note:: This function is idempotent.
    """
    action('enable', service)


def disable(service):
    """
    Disable a service.

    ::

        burlap.systemd.disable('httpd')

    .. note:: This function is idempotent.
    """
    action('disable', service)


def is_running(service):
    """
    Check if a service is running.

    ::

        if burlap.systemd.is_running('httpd'):
            print("Service httpd is running!")
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        return action('status', service).succeeded


def start(service):
    """
    Start a service.

    ::

        if not burlap.systemd.is_running('httpd'):
            burlap.systemd.start('httpd')

    .. note:: This function is idempotent.
    """
    action('start', service)


def stop(service):
    """
    Stop a service.

    ::

        if burlap.systemd.is_running('foo'):
            burlap.systemd.stop('foo')

    .. note:: This function is idempotent.
    """
    action('stop', service)


def restart(service):
    """
    Restart a service.

    ::

        if burlap.systemd.is_running('httpd'):
            burlap.systemd.restart('httpd')
        else:
            burlap.systemd.start('httpd')
    """
    action('restart', service)


def reload(service): # pylint: disable=redefined-builtin
    """
    Reload a service.

    ::

        burlap.systemd.reload('foo')

    .. warning::

        The service needs to support the ``reload`` operation.
    """
    action('reload', service)


def start_and_enable(service):
    """
    Start and enable a service (convenience function).

    .. note:: This function is idempotent.
    """
    start(service)
    enable(service)


def stop_and_disable(service):
    """
    Stop and disable a service (convenience function).

    .. note:: This function is idempotent.
    """
    stop(service)
    disable(service)
