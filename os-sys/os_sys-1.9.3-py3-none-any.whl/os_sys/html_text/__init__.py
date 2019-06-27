try:
    from ._converters import *
except:
    from os_sys.html_text._converters import *
import os
__all__ = ['text', 'write_html', 'get_links', 'links',
           'text2html', 'html2text']
html2text = text
def write_html(text, file, path=os.path.abspath('')):
    data = text2html(text)
    filepath = os.path.join(path, file)
    with open(filepath, 'w+') as w:
        w.write(data)
    return

    
