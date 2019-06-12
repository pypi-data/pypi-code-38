"""
Collection of html generating functions for building out the profile html pages
"""
import contextlib
import os.path

from pygments.formatters import HtmlFormatter


def box(width, cwidth, max_width, pix_width=100.):
    """
    Generate html for a colored box. The box is used to represent execution times, both self and total time.
    The box has a total width of `max_width` (arbitrary units) and will color the first part of the box of
    (width/max_width) a light color blue and the second part of (cwidth/max_width) a darker color blue

    :param width: width of the light colored box (same arbitrary units as max_width)
    :param cwidth: width of the dark colored box (same arbitrary units as max_width)
    :param max_width: maximum width (arbitrary units) of the box
    :keyword pix_width: width in pixels corresponding to max_width

    :return: HTML
    """
    cw = int(pix_width * cwidth / max_width) if cwidth > 0 else 0
    w = int(pix_width * width / max_width) if width > 0 else 0
    b1 = '<div style="margin-top:-8px;margin-bottom:-8px;display:inline-block;height:12px;width:{0}px;background-color:#0000ff";></div>'.format(w)
    b2 = '<div style="margin-top:-8px;margin-bottom:-8px;display:inline-block;height:12px;width:{0}px;background-color:#aaaaff";></div>'.format(cw - w)

    return b2+b1


def column_spec(name, func, width, padding_right=5, padding_left=5, align='right', vertical_align='middle'):
    """
    Returns a function html_table_cell(item, header=False) that generates HTML for table cells
    <td> for header == False and <th> for header == True according to the specification defined
    by the input arguments, see below for more detail.

    :param name: name of the column, this will be the string displayed in a header cell, in case header == True
    :param func: callable. The value returned by func(item) will be displayed in a table cell, in case header == False
    :param width: width of the column in pixels
    :param padding_right: right padding, in pixels of the table cell; default is 5 pixels
    :param padding_left: left padding, in pixels of the table cell; default is 5 pixels
    :param align: alignment of the table cell; default is 'right'

    :return: function
    """
    def html_table_cell(item, header=False):

        if header:
            return '<th align={0} vertical-align={5} style="spacing:0;padding-left:{1}px;padding-right:{2}px;" width={3}>{4}</td>'.\
                   format(align, padding_left, padding_right, width, name, vertical_align)
        else:
            return '<td align={0} vertical-align={4} style="spacing:0;padding-left:{1}px;padding-right:{2}px;">{3}</td>'.\
                   format(align, padding_left, padding_right, func(item), vertical_align)

    return html_table_cell


def strip_pointy(string):
    """
    Remove leading '<' and trailing '>' from `str`

    :param string: string
    :return: cleaned up string
    """
    return string.lstrip('<').rstrip('>')


def get_html_filename(root, py_filename):
    """
    Given root directory and a file name as displayed in the pprofile output generate
    the full path to the html file for py_filename

    :param root: root directory
    :param py_filename: file path

    :return: uri
    """
    if py_filename.startswith('<'):
        html_name = strip_pointy(py_filename)
    else:
        # get the last couple of directories, we don't need the whole thing
        dirname = '.'.join(os.path.dirname(py_filename).split('/')[-3:])
        # get the filename
        basename = os.path.basename(py_filename)
        # join dirname and basename, strip any leading dots, and replace all
        # other dots with underscore
        html_name = (dirname + '_' + basename).lstrip('.').replace('.', '_')

    return os.path.join(root, html_name + '.html')


def href(destination, text):
    """
    HTML href tag: <a href="destination">text</a>

    :param destination: url of the destination html page
    :param text: text
    """
    return '<a href="{0}">{1}</a>'.format(destination, text)


def hrule():
    """
    HTML horizontal rule tag: <hr>
    """
    return '<hr>'


def div(item):
    """
    HTML <pre> tag
    """
    return '<div style="margin-top:-8px;margin-bottom:-8px;">{0}</div>'.format(item)


def pre(item):
    """
    HTML <pre> tag
    """
    return '<pre>{0}</pre>'.format(item)


class html(object):

    def __init__(self):
        self.buffer = list()

    def add(self, string_or_list):
        """
        Adds a string or a list of strings to self.buffer

        :param string_or_list: stuff
        """
        if isinstance(string_or_list, list):
            self.buffer += string_or_list
        else:
            self.buffer.append(string_or_list)

    @contextlib.contextmanager
    def preamble(self, **kwargs):
        """
        Returns the html header including the opening <body> tag

        :keyword kwargs: set of optional args:
                         title: title of the HTML page; default: 'pprofile - python line profile'
                         font_size: size of the font within <body>; default: 'small'
                         background_color: background color within <body>; default: '#eeeeee'
                         border: border style for <table>; default: '1px solid #e0e0e0'
                         font_family: font for <body>, <pre>, <th>, <td>, <hX>; default: 'courier'
                         font_color: font color for <body>, <pre>, <th>, <td>, <hX>; default: '#000000'
        """
        self.add('<html>')
        self.add('<head>')
        self.add('<title>{0}</title>'.format(kwargs.get('title', 'pprofile - python line profile')))
        self.add('<style type="text/css">')
        self.add('body, pre, th, td {{font-size:{0};}}'.format(kwargs.get('font_size', 'small')))
        self.add('body {{background-color:{0};}}'.format(kwargs.get('background_color', '#eeeeee')))
        self.add('table, th, td {{border: {0};}}'.format(kwargs.get('border', '1px solid #e0e0e0')))
        self.add('body, pre, th, td, h1, h2, h3, h4 {{font-family:{0};color:{1}}}'
                 .format(kwargs.get('font_family', 'courier'), kwargs.get('color', '#000000')))
        self.add(HtmlFormatter().get_style_defs('.highlight'))
        self.add('</style>')
        self.add('</head>')
        self.add('<body>')
        yield
        self.add('</body>')
        self.add('</html>')

    @contextlib.contextmanager
    def title(self, level=2):
        """
        HTML title tag

        :keyword level: number indicating the type of title, default is 2, which results in a <h2> tag
        """
        self.add('<h{0}>'.format(level))
        yield
        self.add('</h{0}>'.format(level))

    @contextlib.contextmanager
    def table(self, cellspacing=0):
        """
        HTML table start and end tag (<table>

        :keyword cellspacing: cellspacing for the table
        """
        self.add('<table cellspacing={0}>'.format(cellspacing))
        yield
        self.add('</table>')

    @contextlib.contextmanager
    def table_row(self):
        """
        HTML table row start and end tag (<tr>)
        """
        self.add('<tr>')
        yield
        self.add('</tr>')
