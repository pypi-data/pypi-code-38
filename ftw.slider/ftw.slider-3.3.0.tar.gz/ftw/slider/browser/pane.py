from ftw.slider.browser import utils
from plone import api
from Products.Five.browser import BrowserView


class SliderPaneView(BrowserView):

    def __call__(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return self.request.RESPONSE.redirect(redirect_url)
        else:
            return super(SliderPaneView, self).__call__()

    def get_redirect_url(self):
        """Redirect view adopted from plone's link_redirect_view.py"""

        can_edit = api.user.has_permission('Modify portal content',
                                           obj=self.context)

        link = self.get_link()
        if not can_edit and link:
            return link
        else:
            return ''

    def get_link(self):
        return utils.get_pane_link(self.context)
