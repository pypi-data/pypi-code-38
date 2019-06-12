from ftw.contacts.utils import encode
from ftw.contacts.utils import generate_vcard
from Products.Five.browser import BrowserView


class DownloadVCardView(BrowserView):
    """Download vCard of contact
    """
    def __call__(self):
        response = self.request.response
        response.setHeader("Content-type", "text/vcard")
        filename = encode('%s.vcf' % self.context.Title())
        response.setHeader("Content-Disposition",
                           'inline; filename="%s"' % filename)
        return generate_vcard(self.context).getvalue()
