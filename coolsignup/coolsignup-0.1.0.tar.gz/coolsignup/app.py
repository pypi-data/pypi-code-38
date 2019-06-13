from coolsignup import api
import json
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Finish, Application

def toRequestHandler(api_func, i18 = False):
    class RH(RequestHandler):
        async def post(self):
            try:
                dct = json.loads(
                    self.request.body.decode('utf-8')
                )
            except json.JSONDecodeError:
                self.set_status(400)
                raise Finish(
                    {"success": False, "error": "Not a valid JSON document"}
                )
            else:
                lang = self.get_query_argument('lang', 'en')
                if i18:
                    response = await api_func(dct, lang)
                else:
                    response = await api_func(dct)
                response.translate(lang)
                self.set_status(response.status)
                self.finish(response.dct)
    return RH

class App(object):

    def __init__(self):
        self.urlmap = [
            (url, toRequestHandler(func))
            for url, func in (

                ('/api/email/check-registration-code', api.check_registration_code),
                ('/api/email/register', api.register),
                ('/api/activate-user', api.activate_user),
                ('/api/deactivate-user', api.deactivate_user),
                ('/api/delete-user', api.delete_user),
                ('/api/email/login', api.login),
                ('/api/logout', api.logout),
                ('/api/get-user-id', api.get_user_id),
                ('/api/get-user-fields', api.get_user_fields),
                ('/api/set-user-fields', api.set_user_fields),
                ('/api/email/check-reset-password-code', api.check_reset_password_code),
                ('/api/email/reset-password', api.reset_password),
                ('/api/email/check-change-email-code', api.check_change_email_code),
                ('/api/email/change-email', api.change_email),
                ('/api/email/change-password', api.change_password),
            )
        ]
        for url, func in (
            ('/api/email/send-registration-code', api.send_registration_code),
            ('/api/email/send-reset-password-code', api.send_reset_password_code),
            ('/api/email/send-change-email-code', api.send_change_email_code)
        ):
            self.urlmap.append((url, toRequestHandler(func, i18=True)))

    def serve(self, port):
        app = Application(self.urlmap)

        app.listen(port)
        IOLoop.instance().start()
