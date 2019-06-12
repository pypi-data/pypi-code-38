import cssutils
from xml.sax import saxutils
from lxml.html import tostring, fromstring, clean
from lxml import etree
import six

import logging

class Cleaner(clean.Cleaner):
    def clean_html(self, html):
        if not isinstance(html, six.text_type):
            raise ValueError('We only support cleaning unicode HTML fragments')

        #We wrap the content up in an extra div tag (otherwise lxml does wierd things to it - like adding in <p> tags and stuff)
        divnode = fromstring(six.text_type('<div>') + html + six.text_type('</div>'))
        self(divnode)

        # Strip all class attributes
        etree.strip_attributes(divnode, 'class')

        # Drop all xml:lang and lang attributes, and handle the
        # stripping of any bad css styles
        # Also drop id and class attributes - these are not useful in RichTextEditor
        for node in divnode.xpath("//*"):
            for key, value in node.attrib.items():
                if key.lower() in ('xml:lang', 'lang','id','class'):
                    node.attrib.pop(key, None)
                elif 'style' == key.lower():
                    try:
                        cssStyle = cssutils.parseStyle(value)
                    except Exception as e:
                        logging.info("Style %s failed to parse with error %s." % (value, e))
                        node.attrib.pop(key, None)
                        continue

                    # Set the line separator so that the style gets serialized
                    cssutils.ser.prefs.lineSeparator = ''
                    # Only allow valid style properties
                    cssutils.ser.prefs.validOnly = True

                    new_style = cssStyle.cssText
                    if not new_style.strip():
                        node.attrib.pop(key, None)
                    else:
                        node.attrib[key] = new_style
            # Drop all empty span tags
            if node.tag == 'span' and not list(node.keys()):
                node.drop_tag()

        #Now unwrap the divnode (i.e. just serialize the children of our extra div node)
        cleaned = saxutils.escape(divnode.text) if divnode.text else ''

        for n in divnode:
            cleaned += tostring(n, encoding = six.text_type, method = 'xml')
        return cleaned

# We need safe_attrs_only set to False, otherwise it strips out style attributes completely
cleaner = Cleaner(safe_attrs_only=False)
clean_html = cleaner.clean_html
