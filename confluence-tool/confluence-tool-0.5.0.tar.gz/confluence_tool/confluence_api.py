from urlparse import urlparse
from .page import Page
import re, json
import requests
from .storage_editor import StorageEditor
from .page_properties import PagePropertiesEditor

import json as JSON

import logging
logger = logging.getLogger('confluence.api')
#logger.setLevel(logging.DEBUG)

filter_func = filter

def is_string(s):
    # python 2.7
    return isinstance(s, basestring)

class ConfluenceError(StandardError):
    pass

class ConfluenceAPI:
    def __init__(self, config):
        self.config = config
        self.hostname = urlparse(config['baseurl']).hostname

    def set_args(self, args):
        self.args = args

    def get_args(self):
        return self.args

    def _getauth(self):
        '''return tuple (user, password) for accessing confluence'''
        import netrc

        if self.config.get('username'):

            if not self.config['password']:
                import keyring
                baseurl = self.config['baseurl']
                password = keyring.get_password(baseurl, self.config['username'])
                if password is None:
                    import getpass
                    password = getpass

            else:
                password = self.config.get('password')

            if password is not None:
                return (self.config['username'], password)

        logger.info('hostname: %s', self.hostname)
        (user, account, password) = netrc.netrc().authenticators(self.hostname)
        return (user, password)

    def __getattr__(self, name):
        if name == 'session':
            self.session = requests.Session()
            self.session.auth = self._getauth()
            return self.session

        raise AttributeError(name)

    def request(self, method, endpoint, params=None, stream=None, data=None, json=None, headers=None, **kwargs):
        url = self.config['baseurl'] + endpoint
        if params is None:
            params = {}

        if headers is not None:
            headers = dict(headers)
        else:
            headers = { 'X-Atlassian-Token': 'no-check' }

        if isinstance(params, dict):
            params.update(kwargs)

        try:

            if method == 'GET':
                response = self.session.get(url, params=params, headers=headers, json=json, stream=stream)

            elif data is not None:
                response = self.session.request(method, url, data=data, params=params, json=json, headers=headers)

            elif json is None and data is None:
                headers.update({'Content-Type': 'application/json', 'Accept':'application/json'})
                response = self.session.request(method, url, data=JSON.dumps(params), headers=headers)

            else:
                response = self.session.request(method, url, data=data, json=json, params=params, headers=headers)

        except StandardError as e:
            logger.info("error in request %s %s with params %s", method, endpoint, params)
            raise

        if response.status_code >= 400:
            self.session.close()
            del self.session

            error = ''
            logger.info("error: %s %s, %s: %s", method, url, params, response.text)

            raise ConfluenceError(response.text)

        if not stream:
            if response.text:
                return response.json()
        else:
            return response

        return {}

    def get(self, endpoint, params=None, **kwargs):
        return self.request('GET', endpoint, params, **kwargs)

    def put(self, endpoint, params=None, data=None, json=None, **kwargs):
        return self.request('PUT', endpoint, params, data=data, json=json, **kwargs)

    def post(self, endpoint, params=None, data=None, json=None, **kwargs):
        return self.request('POST', endpoint, params, data=data, json=json, **kwargs)

    def delete(self, endpoint, params=None, data=None, json=None, **kwargs):
        return self.request('DELETE', endpoint, params, data=data, json=json, **kwargs)

    def createSpace(self, key, name, description=''):
        return self.post( '/rest/api/space',
            key=key, name=name, type='global', description={
                'plain': {
                    'value': description,
                    'representation': 'plain'
                }
            })

    def copySpace(self, source_key, key, name, description=''):
        source_space = self.getSpace(source_key)

        # create new space
        space = self.createSpace(key, name, description)
        target_space = self.getSpace(key)
        #log.info("Created new ps")

        self.copyPage(source_space['_expandable']['homepage'], target_space['_expandable']['homepage'])

        # self.updatePage(target_page['id'], version=target_page['version']['number'], title=target_page['title'], storage=source_page['body']['storage']['value'])
        #
        # subpages = self.getChildren(source_page['id'], type='page')
        # # now create page tree from source page
        # for subpage in subpages:
        #     sp = self.getPage(subpage['id'], expand='body.storage')
        #     self.createPage(target_space['key'], subpage['title'], storage = sp['body']['storage']['value'], parent=target_page['id'])

    def getUser(self, username, expand=''):
        """get user information"""
        return self.get("/rest/api/user", username=username, expand=expand)

    def copyPage(self, source, target=None, recursive=True, parent=None, space=None, delete=False):
        '''copy source page as child of target and descend all children

        :param source:
           content url or a pageid
        :param recursive:
           (default True) copy children
        :param parent:
           parent for current target
        :param target:
           where to copy a page
        :param space:
           where to copy a page
        :param delete:
           delete children not present in source
        '''

        source_page = self.getPage(source, expand='body.storage,space')
        target_page = self.getPage(target, expand='version,space')

        if target_page is None:
            target_page = self.createPage(
                space   = space,
                title   = target,
                storage = source_page['body']['storage']['value'],
                parent  = parent
            )
            logger.info("Create Page: %s, %s", space, target)
        else:
            self.updatePage( target_page['id'],
                version = target_page['version']['number'],
                title   = target_page['title'],
                storage = source_page['body']['storage']['value']
            )
            logger.info("Update Page: %s, %s", space, target_page['title'])

        if recursive:
            source_subpages = sorted([ (p['title'], p) for p in self.getChildren(source_page['id'], type='page') ])
            target_subpages = sorted([ (p['title'], p) for p in self.getChildren(target_page['id'], type='page') ])

            # TODO: assert that there are no duplicate page titles

            source_subpage = dict(source_subpages)
            target_subpage = dict(target_subpages)

            assert len(source_subpage.keys()) == len(source_subpages)
            assert len(target_subpage.keys()) == len(target_subpages)

            for title, page in source_subpage.items():
                if title in target_subpage:
                    subpage = target_subpage[title]['id']
                else:
                    subpage = title

                self.copyPage(page['id'], target=subpage, recursive=recursive,
                    parent=target_page['id'], space=space)

            if delete:
                for title, page in target_subpage.items():
                   if title not in source_subpage:
                       self.deletePage(page['id'])

    def getSpace(self, space_key, expand='', label=None, status=None):
        return self.get( '/rest/api/space/%s' % space_key, expand=expand, label=label, status=status)

    def listSpaces(self, expand='', status=None, type=None, label=None):
        return self.iterate('get', '/rest/api/space', expand=expand, status=status, type=type, label=label)

    def getPage(self, page_id, expand='', status='current', version=None):
        if isinstance(expand, (list, set)):
            expand=",".join(expand)

        if not page_id.startswith('/rest'):
            if str(page_id).isdigit():
                page_id = '/rest/api/content/%s' % page_id
            else:
                pages = [p for p in self.getPages(page_id, expand=expand)]
                assert len(pages) == 1
                return pages[0]

        return Page(self, self.get( page_id, expand=expand, status=status, version=version), expand=expand)

    def movePage(self, page, parent):
        return self.get('/pages/movepage.action',
            pageId = page.id,
            spaceKey = parent['spacekey'],
            targetTitle = parent['title'],
            position = 'append'
            )

    def getPages(self, cql=None, expand=[], filter=None, state=None, pages=None, version=None):
        """
        state is comala workflow state here
        """
        logger.info("getPages cql=%s, expand=%s, filter=%s, state=%s", cql, expand, filter, state )
        if not expand:
            expand = []

        if pages is not None:
            cql = self.resolveCQL(pages)

        if state is not None:
            _cql = '(%s) and state = "%s"' % (cql, state)
            for page in self.getPages(_cql, expand, filter):
                yield page

            _cql = '(%s) and state != "%s"' % (cql, state)
            for page in self.getPages(_cql):
                result = self.get("/rest/adhocworkflows/1/workflow/%s/states" % page.id)

                logger.debug("result: %s", result)

                for _state in reversed(result['states']):

                    if _state[u'name'] != state:
                        continue

                    version = _state['contentVersion']
                    logger.debug("found state version: %s", version)

                    _expand = expand
                    if filter is not None:
                        _expand.append('body.view')

                    page = self.getPage(page.id, expand=_expand, status='historical', version=version)
                    logger.debug("page: %s", page)
                    for p in self.getPagesWithProperties(page, filter=filter):
                        yield p

                    break

        elif filter is not None:
            for page in self.getPagesWithProperties(cql, filter=filter, expand=expand, version=version):
                yield page

        else:
            for page in self.iterate('findPages', cql=cql, expand=expand):
                yield Page(self, page, expand)

    def getSpaceHomePage(self, space_key):
        logger.info("space_key: %s", space_key)
        homepage = self.getSpace(space_key, expand='homepage')['homepage']['id']
        return homepage

    def convertWikiToStorage(self, content):
        """convert wiki to storage representation

        Returns storage representation.
        """
        return self.post('/rest/api/contentbody/convert/storage',
            value=content, representation='wiki')['value']

    def getLabels(self, page_id):
        return self.get('/rest/api/content/%s/label' % page_id)

    def addLabels(self, page_id, labels):
        if not isinstance(labels, list):
            labels = [ labels ]
        if not isinstance(labels[0], dict):
            labels = [ dict(prefix="global", name=lbl) for lbl in labels ]

        logger.info("labels: %s", labels)
        return self.post('/rest/api/content/%s/label' % page_id, labels)

    def deleteLabels(self, page_id, labels):
        if not isinstance(labels, list):
            labels = [ labels ]
        result = []
        logger.info("remove labels: %s", labels)
        for label in labels:
            result.append(self.delete('/rest/api/content/%s/label/%s' % (page_id, label)))
        return result

    def updatePage(self, id, title, body=None, version=None, type='page', storage=None, wiki=None):
        if not isinstance(version, dict):
            version = {'number': int(version)}

        if storage is not None:
            body = {
                'storage': {
                    'value': storage,
                    'representation': 'storage'
                }
            }
        if wiki is not None:
            body = {
                'storage': {
                    'value': wiki,
                    'representation': 'wiki'
                }
            }

        return self.put('/rest/api/content/%s' % id,
            version = version,
            type    = type,
            title   = title,
            body    = body
        )

    def editPages(self, cql, editor, filter=None):
        """
        Editor works with mustache templates and jQuery assingments.

        editor: must be either a list (of actions) or must be a dictionary with following items:

            * `templates` - a dictionary of templates, which can be used in
              edit actions
            * `partials` - a dictionary of partials, which can be used in
              templates
            * `actions` - an array of editor actions, where each item is a
              dictionary with following items:

              * `select` - (required) a jQuery selector
              * `action` - a jQuery method how to apply content to selection
                (default: html)
              * `content` - content to be applied. If not present, `template`
                and `data` must be present
              * `type` - type of content.  May be either `storage` or `wiki`.
                Default is `storage`
              * `templates` - a local set of templates to be overridden
              * `template` - a template to which data is applied to, for
                generating content.
              * `data` - data to be applied to template
        """

        if not isinstance(editor, StorageEditor):
            editor = StorageEditor(self, **editor)

        for page in self.getPages(cql, filter=filter, expand=['body.storage', 'version']):
            yield page, editor.edit(page)


    def getPageVersion(self, page_id):
        data = self.get('/rest/api/content/%s' % page_id)
        return data['version']['number']

    def findPages(self, pageSpec='', expand='', limit='', start='', cql=''):
        '''pageSpec may be page_id, "space:path" or CQL (see https://developer.atlassian.com/confdev/confluence-server-rest-api/advanced-searching-using-cql)'''

        if pageSpec:
            cql = self.resolveCQL(pageSpec)
        if isinstance(expand, (list, set)):
            expand = ','.join(list(expand))
        return self.get('/rest/api/content/search', cql = cql, expand=expand, limit=limit, start=start)

    def iterate(self, method, *args, **kwargs):
        if 'start' not in kwargs:
            kwargs['start'] = 0
        if 'limit' not in kwargs:
            kwargs['limit'] = -1

        start = kwargs['start']
        limit = 25 # confluence max
        done = False
        maxResults = kwargs['limit']
        if maxResults < 0:
            maxResults = 10000000000

        while True:
            kwargs['start'] = start
            kwargs['limit'] = limit
            result = getattr(self, method)(*args, **kwargs)

            for item in result['results']:
                logger.info("item_id: %s", item['id'])
                yield item
                maxResults -= 1
                if maxResults <= 0:
                    break

            if maxResults <= 0:
                break

            start += limit
            if result['size'] < result['limit']:
                break

            logger.info("next round: start=%s, limit=%s, size=%s, result_limit=%s", start, limit, result['size'], result['limit'])

    SPACE_PAGE_REF = re.compile(r'^([A-Z]*):(.*)$')
    PAGE_REF = re.compile(r'^:(.*)$')
    PAGE_ID = re.compile(r'^(\d+)$')
    PAGE_URI = re.compile(r'api/content/(\d+)$')
    PARENT = re.compile(r'(.*)>$')
    ANCESTOR = re.compile(r'(.*)>>$')

    def resolveCQL(self, ref):
        """resolve some string to CQL query

        :param ref:
            resolve this reverence to a valid CQL

            * ``SPACE:page title`` -> ``space = SPACE and title = "page title"``
            * ``SPACE:page title>`` -> `` parent = <id of specified page>
            * ``SPACE:page title>>`` -> `` ancestor = <id of specified page>
            * ``:page title`` ->  ``title = "page title"``
            * ``12345`` -> ``ID = 12345``
            * ends with ``api/content/12345`` -> ``ID = 12345``
            * else assume ``ref`` is already CQL

        :return:
            CQL
        """
        def match(RE):
            m = RE.search(ref)
            if m:
                self.mob = m.groups()
                return True
            else:
                return False

        if not is_string(ref):
            ref = str(ref)

        ref = ref.strip()
        logger.debug("ref = %r", ref)

        if match(self.ANCESTOR):
            query = self.resolveCQL(*self.mob)
            queries = []
            for p in self.getPages(query):
                queries.append(u"ancestor = {}".format(p.id))

            result = "("+" OR ".join(queries)+")"
            logger.debug("ancestor CQL: %r", result)
            return result
            #return #u"ancestor = {}".format(p.id)

        if match(self.PARENT):
            query = self.resolveCQL(*self.mob)
            logger.debug("query = %r", query)
            #p = self.getPage(query)
            queries = []
            for p in self.getPages(query):
                queries.append(u"parent = {}".format(p.id))

            result = "("+" OR ".join(queries)+")"
            logger.debug("parent CQL: %r", result)
            return result

            #return u"parent = {}".format(p.id)

        if match(self.SPACE_PAGE_REF):
            if not self.mob[1]:
                return u"space = {}".format(*self.mob)
            else:
                return u"space = {} AND title  = \"{}\"".format(*self.mob)

        if match(self.PAGE_REF):
            return u"title  = \"{}\"".format(*self.mob)

        if match(self.PAGE_ID):
            return u"ID  = {}".format(*self.mob)

        if match(self.PAGE_URI):
            return u"ID  = {}".format(*self.mob)

        return ref

    def cwInfo(self, page, expand=[]):
        """return comala workflow information about current page"""

        if isinstance(expand, list):
            expand = ','.join(expand)
        return self.get('/rest/cw/1/content/%s/status' % page.id, expand=expand)

    def cwApprove(self, page, name, note=None):
        """approve a page"""
        return self.post(
            '/rest/adhocworkflows/latest/approval/%s/approve' % page.id,
            name = name,
            note = note)

    def cwReject(self, page, name, note=None):
        """reject a page"""
        return self.post(
            '/rest/adhocworkflows/latest/approval/%s/reject' % page.id,
            name = name,
            note = note)


    def setPageProperties(self, document):
        pages = document.pop('pages', None)

        if pages is not None:
            for page in pages:
                _doc = document.copy()
                _doc.update(page)
                for p in self.setPageProperties(_doc):
                    yield p

        cql = None
        if 'page' in document:
            cql = self.resolveCQL(document['page'])
        elif 'cql' in document:
            cql = document['cql']

        if cql is not None:
            editor = PagePropertiesEditor(confluence=self, **document)

            found = False
            for page in self.getPagesWithProperties(cql, expand=['body.storage', 'version']):
                new_content = editor.edit(page)
                found = True
                old_content = page.content.replace(" />", "/>")
                logger.debug("old: %r", old_content)
                logger.debug("new: %r", new_content)

                if new_content != old_content:
                    logger.debug("content has changed")
                    result  = self.updatePage(
                        id = page['id'],
                        version = int(page['version']['number'])+1,
                        title   = page['title'],
                        storage = new_content)
                else:
                    logger.debug("content has not changed")
                    result = page

            if not found:
                new_content = editor.edit()
                (space, title) = document['page'].split(':', 1)
                yield dict(
                    page    = dict(
                        spacekey = space,
                        title    = title,
                        ),
                    content = new_content,
                    result  = self.createPage(
                        space = space,
                        title = title,
                        storage = new_content,
                        parent = document.get('parent', None)
                    ))

    PAGE_PROP_FILTER = re.compile(r'^(?:(.*?)([!=])=(.*)|!(.*)|(.*)\?)$')
    def getPagesWithProperties(self, cql, filter=None, expand=[], state=None, **options):
        """Either pass CQL or a page having body.view expanded.
        """
        page_prop_filters = []

        logger.info("cql: '%s', filter: %s", cql, filter)

        if isinstance(cql, Page):
            pages = [ cql ]
        else:
            cql = self.resolveCQL(cql)
            pages = self.getPages(cql, state=state, expand=expand + ['body.view'])

        if filter is not None:
            if not isinstance(filter, list):
                filter = [ filter ]

            for item in filter:
                if is_string(item):
                    m = self.PAGE_PROP_FILTER.search(item)
                    if m:
                        (name, cmp, value, not_exists, present) = m.groups()
                        page_prop_filters.append(dict(name=name, cmp=cmp, value=value, not_exists=not_exists, present=present))
                else:
                    page_prop_filters.append(item)

        def page_prop_filterer(page):
            if not len(page_prop_filters):
                return True

            result = True
            for f in page_prop_filters:
                value = page.getPageProperty(f['name'])
                cmp = f['cmp']
                not_exists = f['not_exists']
                present = f['present']

                logger.info("filter: %s, value = %s", f, value)

                if cmp == '=':
                    if isinstance(value, list):
                        result = result and f['value'] in value
                    else:
                        result = result and value == f['value']
                elif not_exists:
                    value = page.getPageProperty(f['not_exists'])
                    result = result and value is None

                elif present:
                    value = page.getPageProperty(f['present'])
                    result = result and value is not None

                else:
                    if isinstance(value, list):
                        result = result and f['value'] not in value
                    else:
                        result = result and value != f['value']

            logger.info("filterer result = %s", result)
            return result


        for page in filter_func(page_prop_filterer, pages):
            yield page

    def getContentId(self, page):
        (space, title, id) = self.extractPage(page)
        return id

    def extractPage(self, pageSpec):
        results = self.findPages(pageSpec, expand='space')

        if results is None:
            return None

        assert results['size'] == 1, "Ambigious search: %s" % pageSpec

        page = results['results'][0]
        return page['space']['key'], page['title'], page['id']

    def createPage(self, space, title, storage, parent=None, representation='storage', type='page'):
        data = dict(
            title = title,
            type  = type,
            space = {'key': space},
            body  = {'storage': {'value': storage, 'representation': representation}}
        )

        if parent is not None:
            data['ancestors'] = [{'id': self.getContentId(parent)}]

        return self.post('/rest/api/content', **data)

    def getChildren(self, page_id, type=None, expand=''):
        if not page_id.startswith('/rest'):
            page_id = '/rest/api/content/%s' % page_id
        if type is None:
            url = page_id +"/child"
        else:
            url = page_id + "/child/"+type
        return self.get(url, expand=expand)['results']
