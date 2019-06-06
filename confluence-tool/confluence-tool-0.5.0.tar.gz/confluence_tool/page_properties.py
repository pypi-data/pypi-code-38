import logging, urllib
logger = logging.getLogger("confluence.page.props")

from os.path import dirname
#logger.setLevel(logging.DEBUG)

from .storage_editor import edit

from pyquery import PyQuery
from pystache import Renderer
from pprint import pprint
from datetime import datetime, date

import re

DISPLAY_URL = re.compile(r'/display/([\w-]*)/(.*)')

def extract_data(elem, need_data=False):
    """Extracts data from confluence html page properties value <td>.

    Returns either a simple value in wiki represention or a complex data type
    with extraction of all containing data.
    """
    data = {}
    data['users'] = users = []
    data['refs']  = refs  = []
    data['links'] = links = []
    data['dates'] = dates = []
    data['mailAddresses'] = mailAddresses = []

    # if is list
    if elem.children().eq(0).is_('div.content-wrapper > ul, ul'):
        value = [ extract_data(PyQuery(e)) for e in elem.find('li') ]
        logger.debug("list value: %s", value)

    # if is dictionary-like table
    elif elem.children().eq(0).is_('div.table-wrapper, table'):
        value = {}
        for e in elem.find('table th'):
            if e.next_all().not_('td'):
                continue

            value[e.text().strip()] = extract_data(e.next_all())

    else:
        # transform usernames, refs and external links to wiki code
        d = PyQuery("<div>"+elem.html()+"</div>")

        for a in d('a'):
            _a = d(a)
            if _a.hasClass('confluence-userlink'):
                username = _a.attr('data-username')
                users.append(dict(username=username))
                _a.html("[~%s]" % username)

            elif _a.attr('href').startswith('mailto:'):
                address = _a.attr('href')[7:]
                mailAddresses.append(address)
                _a.html(address)

            elif _a.hasClass('external-link'):
                href = _a.attr('href')
                caption = _a.text()
                if caption != href:
                    _a.html("[%s|%s]" % (caption, href))
                    links.append(dict(caption=caption, href=href))
                else:
                    _a.html("[%s]" % href)
                    links.append(dict(href=href))
            else:
                #print _a.attr('href')
                m = DISPLAY_URL.search(_a.attr('href'))
                if m:
                    (space, title) = m.groups()
                    title = urllib.unquote(title).decode('utf8').replace(u"+", u" ")
                    _a.html("[{}:{}]".format(space, title))
                    refs.append(dict(space=space, title=title))

        for t in d('time'):
            _t = d(t)
            _time = _t.attr('datetime')
            dates.append(_time)
            _t.html(_time)

        value = d(':root').text().strip()

        logger.info("value: %s", value)
    if need_data:
        return dict(
            value=value, html=d.show(), users=users,
            refs=refs, links=links, mailAddresses=mailAddresses,
        )
    else:
        return value


def get_page_properties(html, need_html=False, need_data=False, properties=None, **kwargs):
    d = PyQuery(html)
    d('script').remove()
    th = d("div[data-macro-name=details] > div.table-wrap > table > tbody > tr > th")
    for elem in th:
        _th = PyQuery(elem)
        key = _th.text().strip()

        if properties is not None:
            if key not in properties:
                continue

        if not need_data and need_html:
            yield (key, _th.next().html())
        else:
            yield (key, extract_data(_th.next(), need_data=False))


class PagePropertiesEditor:

    def __init__(self, pagePropertiesEditor, templates={}, confluence=None, pagePropertiesOrder=None, **kwargs):
        self.editor = pagePropertiesEditor
        self.templates = templates
        self.confluence = confluence

        self.order = None
        if 'order' in kwargs:
            self.order = kwargs['order']
        if pagePropertiesOrder is not None:
            self.order = pagePropertiesOrder

        self.renderer = Renderer(
            search_dirs = "{}/templates".format(dirname(__file__)),
            file_extension = "mustache",
            )

        for t in ['user', 'page', 'link', 'list', 'value']:
            self.renderer.load_template(t)

        self.userkeys = {}


    def userkey(self, name):
        "resolve username to userkey"

        if name not in self.userkeys:
            self.userkeys[name] = self.confluence.getUser(name)['userKey']
        return self.userkeys[name]

    ELEM = re.compile(r'''(?: \[ (
         ~(?P<user>[^\]]*?)
        | (?P<spacekey>\w+):(?P<title>[^\]]*?)
        | (?P<link>[^\]]*?)
        ) \]
        | (?P<datetime>\d\d\d\d-\d\d-\d\d(?:\s\d\d:\d\d(?::\d\d)?)?)
        )
        ''', re.VERBOSE)


    def get_storage(self, key, value, templates=None):
        "get storage representation for value using templates"

        def render(name, **context):
            # try first, if there is a name-specific template
            for _name in ["{}-{}".format(key, name), name]:
                # first try local templates
                if _name in templates:
                    return self.renderer.render(templates[_name], context)
                # try editor templates
                elif _name in self.templates:
                    return self.renderer.render(self.templates[_name], context)

            # finally return the default template
            return self.renderer.render_name(name, context)

        logger.debug("value (%s): %s", value.__class__.__name__, value)

        if isinstance(value, list):
            values = [ {'value': self.get_storage(key, v, templates).strip() } for v in value ]
            return render('list', list=values)

        if isinstance(value, date):
            value = value.isoformat()
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d')

        def replacer(m):
            d = m.groupdict()
            if d['user']:
                return render('user', userkey=self.userkey(d['user']))
            if d['spacekey']:
                return render('page', **d)
            if d['link']:
                if '|' in d['link']:
                    caption, href = d['link'].split('|')
                else:
                    caption, href = (d['link'],)*2
                return render('link', caption=caption, href=href)
            if d['datetime']:
                return render('datetime', datetime=d['datetime'])

        if not isinstance(value, basestring):
            value = str(value)
        value = self.ELEM.sub(replacer, value)

        return render('value', value=value.strip())


    def edit_prop(self, key, data, action):

        if not isinstance(action, dict):
            return self.get_storage(key, action, {})

        if 'replace' in action:
            data = action['replace']

        if 'remove' in action:
            values = action['remove']
            if not isinstance(values, list):
                values = [ values ]

            if not isinstance(data, list):
                if values[0] == data:
                    data = []
                else:
                    logger.debug("replace(%s): value %s not present", key, values[0])
            else:
                for val in values:
                    if val in data:
                        data.remove(val)

        if 'add' in action:
            values = action['add']
            if not isinstance(values, list):
                values = [ values ]
            if not isinstance(data, list):
                if not data:
                    data = []
                else:
                    data = [ data ]
            data += values

        return self.get_storage(key, data, action.get('templates', {}))


    def edit(self, page=None):
        updated_keys = []
        if page is not None:
            content = page['body']['storage']['value']
            pageProperties = page['pageProperties']
        else:
            with open(dirname(__file__)+'/templates/page-props.html', 'r') as f:
                content = f.read()
            pageProperties = {}

        editor = edit(content)
        s = "ac|structured-macro[ac|name=details] > ac|rich-text-body > table > tbody > tr"

        for row in editor(s):
            key = editor(row).find('th').text().strip()

            if key not in self.editor: continue

            updated_keys.append(key)

            action = self.editor[key]
            if action == 'delete':
                editor(row).remove()
                continue

            data = pageProperties.get(key, '')
            html_data = self.edit_prop(key, data, action)
            x = editor(row).find('td')
            #import rpdb2 ; rpdb2.start_embedded_debugger('foo')

            x.html(html_data)

        selector = "ac|structured-macro[ac|name=details] table tbody"
        order = self.order
        if order is None:
            order = self.editor.keys()

        for key in order:
            action = self.editor[key]

            if action == 'delete': continue
            if key not in updated_keys:
                html_data = self.edit_prop(key, '', action)
                tr = "<tr><th>{}</th><td>{}</td></tr>".format(key, html_data)
                editor(selector).append(tr)

        return editor.end_edit()
