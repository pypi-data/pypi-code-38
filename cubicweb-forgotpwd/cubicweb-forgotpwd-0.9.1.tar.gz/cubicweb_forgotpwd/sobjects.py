import random
import string
from datetime import datetime, timedelta

from cubicweb import _, ValidationError
from cubicweb.predicates import match_kwargs
from cubicweb.server import Service


class ForgotPwdEmailService(Service):
    """Generate a password reset request, store it in the database, and send
    reset email"""

    __regid__ = 'forgotpwd_send_email'
    __select__ = Service.__select__ & match_kwargs('use_email')

    def call(self, use_email=None):
        cnx = self._cw
        repo = cnx.repo
        revocation_limit = repo.config['revocation-limit']
        revocation_id = u''.join(random.choice(string.ascii_letters+string.digits)
                                 for x in range(10))
        revocation_date = datetime.now() + timedelta(minutes=revocation_limit)

        existing_requests = cnx.execute('Any F WHERE U primary_email E, E address %(e)s, U has_fpasswd F',
                                        {'e': use_email})
        if existing_requests:
            raise ValidationError(None, {None: _('You have already asked for a new password.')})
        rset = cnx.execute('INSERT Fpasswd X: X revocation_id %(a)s, X revocation_date %(b)s, '
                           'U has_fpasswd X WHERE U primary_email E, E address %(e)s',
                           {'a':revocation_id, 'b':revocation_date, 'e': use_email})
        if not rset:
            raise ValidationError(None, {None: _(u'An error occured, this email address is unknown.')})


class ForgotPwdChangePwdService(Service):
    """Actually change the user's password"""
    __regid__ = 'forgotpwd_change_passwd'
    __select__ = Service.__select__ & match_kwargs('use_email', 'revocation_id', 'upassword')

    def call(self, use_email=None, revocation_id=None, upassword=None):
        cnx = self._cw
        rset = cnx.execute('Any F, U WHERE U is CWUser, U primary_email E, '
                           'E address %(email)s, EXISTS(U has_fpasswd F, '
                           'F revocation_id %(revid)s)',
                           {'email': use_email,
                            'revid': revocation_id})
        if rset:
            forgotpwd = rset.get_entity(0,0)
            revocation_date = forgotpwd.revocation_date
            user = rset.get_entity(0,1)
            if revocation_date > datetime.now():
                cnx.execute('SET U upassword %(newpasswd)s WHERE U is CWUser, U eid %(usereid)s',
                            {'newpasswd':upassword.encode('UTF-8'), 'usereid':user.eid})
                cnx.execute('DELETE Fpasswd F WHERE F eid %(feid)s',
                            {'feid':forgotpwd.eid})
                msg = cnx._(u'Your password has been changed.')
            else:
                msg = cnx._(u'That link has either expired or is not valid.')
        else:
            msg = cnx._(u'You already changed your password. This link has expired.')
        return msg
