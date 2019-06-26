"""
Copied from elyself.portlets.image
the image portlet is not working proper under plone 3.0.6
"""
from Acquisition import aq_inner
from plone.namedfile.file import FileChunk
from zope.publisher.browser import BrowserView


class ImageView(BrowserView):
    '''
    View the image field of the image portlet. We steal header details
    from zope.app.file.browser.file and adapt it to use the dublin
    core implementation that the Image object here has.
    '''

    def __call__(self):
        context = aq_inner(self.context)
        image = context.image

        data = image.data
        if isinstance(image.data, FileChunk):
            data = str(data)

        # cache for one day.
        self.request.response.setHeader('Cache-Control', 'max-age=86400')
        self.request.response.setHeader('Content-Type', image.contentType)
        self.request.response.write(data)
