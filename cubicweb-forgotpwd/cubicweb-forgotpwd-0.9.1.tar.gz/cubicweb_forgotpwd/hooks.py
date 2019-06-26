"""this module contains server side hooks for cleaning forgotpwd table
"""

import random
import string
from datetime import datetime, timedelta

from logilab.common.decorators import monkeypatch
from yams import ValidationError

from cubicweb import _
from cubicweb.predicates import is_instance
from cubicweb.crypto import encrypt
from cubicweb.server import hook
from cubicweb.server.repository import Repository
from cubicweb.sobjects.notification import NotificationView


class ServerStartupHook(hook.Hook):
    """on startup, register a task to delete old revocation key"""
    __regid__ = 'fpwd_startup'
    events = ('server_startup',)

    def __call__(self):
        # XXX use named args and inner functions to avoid referencing globals
        # which may cause reloading pb
        def cleaning_revocation_key(repo, now=datetime.now):
            with repo.internal_cnx() as cnx:
                cnx.execute('DELETE Fpasswd F WHERE F revocation_date < %(date)s',
                            {'date': now()})
                cnx.commit()
        # run looping task often enough to purge pwd-reset requests
        limit = self.repo.vreg.config['revocation-limit'] * 60
        self.repo.looping_task(limit, cleaning_revocation_key, self.repo)


class PasswordResetNotification(NotificationView):
    __regid__ = 'notif_after_add_entity'
    __select__ = is_instance('Fpasswd')

    content = _('''There was recently a request to change the password of your account
on %(base_url)s (login: %(login)s).
If you requested this password change, please set a new password by following
the link below:

%(resetlink)s

If you do not want to change your password, you may ignore this message. The
link expires in %(limit)s minutes.

See you soon on %(base_url)s !
''')

    def subject(self):
        return self._cw._(u'[%s] Request to change your password' % self._cw.base_url())

    def recipients(self):
        fpasswd = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        user = fpasswd.reverse_has_fpasswd[0]
        return [(user.cw_adapt_to('IEmailable').get_email(), user.property_value('ui.language'))]

    def context(self, **kwargs):
        fpasswd = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        user = fpasswd.reverse_has_fpasswd[0]
        data = {}
        data['use_email'] = user.cw_adapt_to('IEmailable').get_email()
        data['revocation_id'] = fpasswd.revocation_id
        key = encrypt(data, self._cw.vreg.config['forgotpwd-cypher-seed'])
        url = self._cw.build_url('forgottenpasswordrequest',
                                 key=key,)
        return {
            'resetlink': url,
            'login': user.login,
            # NOTE: it would probably be better to display the expiration date
            #       (with correct timezone)
            'limit': self._cw.vreg.config['revocation-limit'],
            'base_url': self._cw.base_url(),
            }

