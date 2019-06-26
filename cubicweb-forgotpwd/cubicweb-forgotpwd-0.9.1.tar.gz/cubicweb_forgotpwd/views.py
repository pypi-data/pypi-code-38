"""cube-specific forms/views/actions/components

:organization: Logilab
:copyright: 2001-2011 LOGILAB S.A. (Paris, FRANCE), license is LGPL v2.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: GNU Lesser General Public License, v2.1 - http://www.gnu.org/licenses
"""

from six import text_type

from yams import ValidationError

from logilab.mtconverter import xml_escape

from cubicweb import _
from cubicweb.view import StartupView
from cubicweb.crypto import decrypt
from cubicweb.web import (Redirect, controller, form, captcha,
                          formwidgets as wdg, formfields as ff)
from cubicweb.web.views import forms, urlrewrite, basetemplates


# Login form
# ----------

class ForgotPasswordLinkWidget(wdg.FieldWidget):
    def render(self, form, field, renderer):
        req = form._cw
        ret = u'<span class="forgotpwdLink"><a href="%s">%s</a></span>' % (
            xml_escape(req.build_url('forgottenpassword')),
            req._('Forgot your password?'))
        return ret

basetemplates.LogForm.append_field(
    ff.Field(name='__forgotpwd', label=None, widget=ForgotPasswordLinkWidget)
    )

# First form, send an email
# -------------------------

class ForgottenPasswordForm(forms.FieldsForm):
    __regid__ = 'forgottenpassword'

    form_buttons = [wdg.SubmitButton()]
    @property
    def action(self):
        return self._cw.build_url(u'forgottenpassword_sendmail')

    use_email = ff.StringField(widget=wdg.TextInput(), required=True, label=_(u'your email address'))
    captcha = ff.StringField(widget=captcha.CaptchaWidget(), required=True,
                             label=_('captcha'),
                             help=_('please copy the letters from the image'))


class ForgottenPasswordFormView(form.FormViewMixIn, StartupView):
    __regid__ = 'forgottenpassword'

    def call(self):
        form = self._cw.vreg['forms'].select('forgottenpassword', self._cw)
        self.w(u'<p>%s</p>' % self._cw._(u'Forgot your password?'))
        form.render(w=self.w)

class ForgottenPasswordSendMailController(controller.Controller):
    __regid__ = 'forgottenpassword_sendmail'

    def publish(self, rset=None):
        data = self.checked_data()
        try:
            with self.appli.repo.internal_cnx() as cnx:
                cnx.call_service(
                    'forgotpwd_send_email', use_email=data['use_email'])
                cnx.commit()
        except ValidationError:
            raise
        except Exception as exc:
            msg = text_type(exc)
        else:
            msg = self._cw._(u'An email has been sent, follow instructions in there to change your password.')
        raise Redirect(self._cw.build_url('pwdsent', __message=msg))

    def checked_data(self):
        '''only basic data check here (required attributes and password
        confirmation check)
        '''
        fieldsform = self._cw.vreg['forms'].select('forgottenpassword', self._cw)
        data = {}
        errors = {}
        for field in fieldsform._fields_:
            value = self._cw.form.get(field.name, u'').strip()
            if not value:
                if field.required:
                    errors[field.name] = self._cw._('required attribute')
            data[field.name] = value
        captcha = self._cw.session.data.pop('captcha', None)
        if captcha is None:
            errors[None] = self._cw._('unable to check captcha, please try again')
        elif data['captcha'].lower() != captcha.lower():
            errors['captcha'] = self._cw._('incorrect captcha value')
        if errors:
            raise ValidationError(None, errors)
        return data


class PasswordSentView(StartupView):
    __regid__ = 'pwdsent'

    def call(self):
        self.wview('index', self.cw_rset)


# Second form, ask for a new password
# -----------------------------------

class ForgottenPasswordRequestForm(forms.FieldsForm):
    __regid__ = 'forgottenpasswordrequest'

    form_buttons = [wdg.SubmitButton()]
    @property
    def action(self):
        return self._cw.build_url(u'forgottenpassword-requestconfirm')

    upassword = ff.StringField(widget=wdg.PasswordInput(), required=True)


class ForgottenPasswordRequestView(form.FormViewMixIn, StartupView):
    __regid__ = 'forgottenpasswordrequest'

    def check_key(self):
        try:
            return decrypt(self._cw.form['key'],
                           self._cw.vreg.config['forgotpwd-cypher-seed'])
        except:
            msg = self._cw._(u'Invalid link. Please try again.')
            raise Redirect(self._cw.build_url(u'forgottenpassword', __message=msg))

    def call(self):
        key = self.check_key()
        form = self._cw.vreg['forms'].select('forgottenpasswordrequest', self._cw)
        form.add_hidden('use_email', key['use_email'])
        form.add_hidden('revocation_id', key['revocation_id'])
        self.w(u'<p>%s</p>' % self._cw._(u'Update your password:'))
        form.render(w=self.w)


class ForgottenPasswordRequestConfirm(controller.Controller):
    __regid__ = 'forgottenpassword-requestconfirm'

    def publish(self, rset=None):
        data = self.checked_data()
        with self.appli.repo.internal_cnx() as cnx:
            msg = cnx.call_service(
                'forgotpwd_change_passwd', use_email=data['use_email'],
                revocation_id=data['revocation_id'], upassword=data['upassword'])
            cnx.commit()
        raise Redirect(self._cw.build_url('pwdreset', __message=msg))

    def checked_data(self):
        cw = self._cw
        fieldsform = cw.vreg['forms'].select('forgottenpasswordrequest', cw)
        data = {}
        errors = {}
        for field in fieldsform.fields:
            value = cw.form.get(field.name, u'').strip()
            if not value and field.required:
                errors[field.name] = cw._('required attribute')
            data[field.name] = value
        data['use_email'] = cw.form.get('use_email', '').strip()
        data['revocation_id'] = cw.form.get('revocation_id', '').strip()
        if data['upassword'] != cw.form.get('upassword-confirm'):
            errors['upassword'] = _('passwords are different')
        if errors:
            raise ValidationError(None, errors)
        return data


class PasswordResetView(StartupView):
    __regid__ = 'pwdreset'

    def call(self):
        self.wview('index')


# URL rewriting
# -------------

class RegistrationSimpleReqRewriter(urlrewrite.SimpleReqRewriter):
    rules = [
        ('/forgottenpassword', dict(vid='forgottenpassword')),
        ('/forgottenpasswordrequest', dict(vid='forgottenpasswordrequest')),
        ('/pwdsent', dict(vid='pwdsent')),
        ('/pwdreset', dict(vid='pwdreset')),
        ]
