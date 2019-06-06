import contextlib, re
from pystache import Renderer
from os.path import dirname
from .myquery import MyQuery
from .util import get_list_data
from .page import Page
from lxml import etree

from lxml.etree import XMLSyntaxError

import logging
log = logging.getLogger('confluence-tool.storage_editor')

class StorageEditor:

    def __init__(self, confluence=None, templates=None, partials=None, actions=None):
        self.templates = templates
        self.partials = partials

        self.actions = get_list_data(actions)
        self.confluence = confluence
        self.renderer = Renderer(
            search_dirs = "{}/templates".format(dirname(__file__)),
            file_extension = "mustache",
            )


    def edit(self, content):
        if isinstance(content, Page):
            page = content
        else:
            page = None

        if isinstance(content, (dict, Page)):
            if content.get('body'):
                content = content['body']['storage']['value']
            else:
                content = ''

        try:
            Q = self.begin_edit(content)

        except XMLSyntaxError as e:
            if page is None: raise

            log.debug("error: %s", e)

            if re.match(r"Entity '.*?' not defined", str(e)):
                log.debug('matched')
                raise StandardError("There are double-escaped HTML entities in page %(spacekey)s:%(title)s" % page)
            else:
                raise

        for action in self.actions:
            if 'data' in action:
                if 'template' in action:
                    content = self.renderer.render_name(action['template'], action['data'])
                else:
                    content = self.renderer.render(action['content'], action['data'])
            else:
                content = action.get('content')

            if content is not None and 'type' in content:
                if content['type'] == 'wiki':
                    content = self.confluence.convertWikiToStorage(content)

            method = action.get('action', 'html')

            log.debug("content for %s: %s", method, content)

            if action.get('select'):
                selection = Q(action['select'])
            else:
                selection = Q

            log.debug("selection: %s", selection)

            #import rpdb2 ; rpdb2.start_embedded_debugger('foo')

            if content is None:
                getattr(selection, method)()
            else:
                getattr(selection, method)(content)

            log.debug("edited: %s", str(Q))

        return self.end_edit()


    def begin_edit(self, content=None):
        if content is None:
            content = self.content

        self.pyquery = storage_query(content)

        return self.pyquery


    FIRST_OPENING_TAG = re.compile(r'^<root[^>]*>')
    LAST_CLOSING_TAG  = re.compile(r'</root>$')

    def end_edit(self, pyquery=None):
        if pyquery is None:
            pyquery = self.pyquery

        #import rpdb2 ; rpdb2.start_embedded_debugger('foo')

        root = pyquery.root.getroot()

        data = str(pyquery.__class__([x for x in root]))
        return data


def edit(content):
    storage_editor = StorageEditor()
    pyquery = storage_editor.begin_edit(content)

    def end_edit(*args):
        return storage_editor.end_edit()

    pyquery.end_edit = end_edit
    return pyquery


def storage_query(content):
    namespaces = {
        'ac': 'http://www.atlassian.com/schema/confluence/4/ac',
        'ri': 'http://www.atlassian.com/schema/confluence/4/ri',
    }

    return MyQuery(content, parser='xml', namespaces=namespaces)
