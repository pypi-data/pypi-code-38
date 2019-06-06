import pyquery, sys, re
from pyquery.pyquery import fromstring, no_default

PY3k = sys.version_info >= (3,)

if PY3k:
    from urllib.parse import urlencode
    from urllib.parse import urljoin
    basestring = (str, bytes)
    unicode = str
else:
    from urllib import urlencode  # NOQA
    from urlparse import urljoin  # NOQA


class MyQuery(pyquery.PyQuery):

    def __init__(self, *args, **kwargs):
        namespaces = kwargs.get('namespaces')
#        if namespaces:
        if 1:
            kwargs['parser'] = 'xml'

            length = len(args)
            if length == 1:
                selector, context = None, args[0]
            elif length == 2:
                selector, context = args

            if isinstance(context, basestring):
                root = fromstring(
                    self._wrap_root(context, namespaces),
                    kwargs.get('parser')
                    )[0]

                if selector is not None:
                    args = (selector, root.getchildren())
                else:
                    args = (root.getchildren(),)

        super(MyQuery,self).__init__(*args, **kwargs)


    def _wrap_root(self, context, namespaces=None):
        if namespaces is None:
            if hasattr(self, 'namespaces'):
                namespaces = self.namespaces
            else:
                namespaces = {}

        attrs = " ".join([ 'xmlns:%s="%s"' % (k,v) for (k,v) in namespaces.items() ])

        result = unicode("<root %s>" % attrs)+context+unicode('</root>')
        #print result

        return result


    def _get_root(self, value):
        """In case of creating the value from string, namespace has to be passed
        """
        if isinstance(value, basestring):
            root = fromstring(self._wrap_root(value), self.parser)[0]
            # TODO: warn if root has more than one child?
            value = root.getchildren()[0]

        return super(MyQuery, self)._get_root(value)


    def _copy(self, *args, **kwargs):
        """must also set parser"""
        kwargs.setdefault('parser', self.parser)
        return super(MyQuery,self)._copy(*args,**kwargs)

    HTML_TAG = re.compile(r'(<!--.*?-->|<[^>]*>)', re.DOTALL)
    XMLNS = re.compile(r'\sxmlns:[\w\-]+="[^"]*"')
    def strip_namespaces(self, html):
        if not isinstance(html, basestring):
            return html

        html_items = self.HTML_TAG.split(html)
        #print "html_items: %s" % html_items
        for i,part in enumerate(html_items):
#            print part
            if part.startswith('<'):
                if 'xmlns:' in part:
                    html_items[i] = x = self.XMLNS.sub('', part)

        return html.__class__('').join(html_items)

    def __unicode__(self):
        return self.strip_namespaces(super(MyQuery,self).__unicode__())

    def __str__(self):
        return self.strip_namespaces(super(MyQuery,self).__str__())

    def html(self, value=no_default, **kwargs):
        """This cannot be wrapped and needs (almost) full override.
        """
        if value is no_default:
            html = super(MyQuery,self).html(value, **kwargs)
            return self.strip_namespaces(html)

        else:
            if isinstance(value, self.__class__):
                new_html = unicode(value)
            elif isinstance(value, basestring):
                new_html = value
            elif not value:
                new_html = ''
            else:
                raise ValueError(type(value))

            for tag in self:
                for child in tag.getchildren():
                    tag.remove(child)
                root = fromstring(
                    self._wrap_root(new_html),
                    self.parser)[0]
                children = root.getchildren()
                if children:
                    tag.extend(children)
                tag.text = root.text
                tag.tail = root.tail

        return self
