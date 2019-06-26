from plone.namedfile.browser import Download as Base
from plone.rfc822.interfaces import IPrimaryFieldInfo
from zope.publisher.interfaces import NotFound


class Download(Base):
    def _getFile(self):
        if not self.fieldname:
            info = IPrimaryFieldInfo(self.context, None)
            if info is None:
                # Ensure that we have at least a filedname
                raise NotFound(self, '', self.request)
            self.fieldname = info.fieldname
            file = info.value
        else:
            context = getattr(self.context, 'aq_explicit', self.context)
            file = getattr(context, self.fieldname, None)

        if file is None:
            raise NotFound(self, self.fieldname, self.request)

        return file
