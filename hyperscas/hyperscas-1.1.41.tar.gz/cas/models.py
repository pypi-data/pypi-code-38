# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from six.moves.urllib_parse import urlparse
from importlib import import_module
import logging
from traceback import format_exc

from django.conf import settings
# Ed Crewe - add in signals to delete old tickets
# Single Sign Out
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver
from django.core.cache import cache
from .domain import Domain

logger = logging.getLogger('cas')

session_engine = import_module(settings.SESSION_ENGINE)
SessionStore = session_engine.SessionStore


def _get_cas_backend():
    from .backends import CASBackend
    return '{0.__module__}.{0.__name__}'.format(CASBackend)


cas_backend = _get_cas_backend()


class SessionServiceTicket(object):
    service_ticket = ''
    session_key = ''
    user = 0

    def __init__(self, user=None, service_ticket=None, session_key=None):
        if user:
            self.user = user
        if service_ticket:
            self.service_ticket = service_ticket
        if session_key:
            self.session_key = session_key

    @property
    def pk(self):
        key = ':'.join(('CAS', self.service_ticket))
        return key

    @classmethod
    def create(cls, user=None, service_ticket=None, session_key=None):
        data = dict(
            user=user, session_key=session_key, service_ticket=service_ticket)
        obj = cls(**data)
        try:
            cache.set(obj.pk, data, 2 * 60 * 60)
        except Exception:
            logger.error(format_exc())
        return obj

    @classmethod
    def get_by_id(cls, key):
        key = ':'.join(('CAS', key or ''))
        try:
            data = cache.get(key) or {}
        except Exception:
            logger.error(format_exc())
            return None
        return cls(**data)

    def delete(self):
        try:
            cache.delete(self.pk)
        except Exception:
            logger.error(format_exc())
        return self

    def get_session(self):
        """ Searches the session in store and returns it """
        sst = SessionStore(session_key=self.session_key)
        sst[BACKEND_SESSION_KEY] = cas_backend
        return sst

    def __str__(self):
        return '<{}: {}>'.format(self.user, self.service_ticket)

    __repr__ = __str__


def _is_cas_backend(session):
    """ Checks if the auth backend is CASBackend """
    if session:
        backend = session.get(BACKEND_SESSION_KEY)
        return backend == cas_backend
    return None


@receiver(user_logged_in)
def map_service_ticket(sender, **kwargs):

    request = kwargs['request']
    ticket = request.GET.get('ticket')
    if ticket and _is_cas_backend(request.session):
        session_key = request.session.session_key
        SessionServiceTicket.create(
            service_ticket=ticket,
            user=request.user.email,
            session_key=session_key)


@receiver(user_logged_out)
def delete_service_ticket(sender, **kwargs):
    """ Deletes the mapping between session key and service ticket after user
        logged out """
    request = kwargs['request']
    if _is_cas_backend(request.session):
        session_key = request.session.session_key
        sst = SessionServiceTicket.get_by_id(session_key)
        sst and sst.delete()
