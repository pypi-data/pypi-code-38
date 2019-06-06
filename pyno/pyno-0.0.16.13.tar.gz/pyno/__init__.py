from pyno.html_tags_autocomplete import HTMLTagList
from pyno.tree_model import HTML, html, TreeNode, TreeSub, Namespace
from pyno.custom_tags import Require, CDATA, Import, Include

from pyno.browser_preview import browser_preview
from pyno.stylesheets import Style

# Set default settings for void elements
void_elements = 'br hr img input link meta area base col command embed keygen param source track wbr'.split(' ')
for tag in void_elements:
    HTML.defaults[tag] = {'_void_element': True}




# todo consider adding some magic to add default parameters from construct as parameters on the object during initialization. (*It's funky but nice in practice*)

from werkzeug.serving import run_simple

def serve_example(page):
    run_simple('localhost', 5000, page, use_reloader=True)

__version__ = "0.0.16.13"
