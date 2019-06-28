from zope.publisher.browser import BrowserView
from zope.i18n import translate

TEMPLATE = """\
var delete_confirm_message = "%(delete_confirm_message)s";
"""


class JSVariables(BrowserView):

    def __call__(self, *args, **kwargs):
        response = self.request.response
        response.setHeader('content-type', 'text/javascript;;charset=utf-8')

        delete_confirm_message = translate('delete_confirm_message',
                                           domain='imio.actionspanel',
                                           context=self.request)

        return TEMPLATE % dict(
            delete_confirm_message=delete_confirm_message,
        )
