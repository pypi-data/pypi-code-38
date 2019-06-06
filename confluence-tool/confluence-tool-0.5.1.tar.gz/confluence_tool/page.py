from HTMLParser import HTMLParser
htmlparser = HTMLParser()

from lxml.etree import XMLSyntaxError


import logging
log = logging.getLogger('confluence-tool.page')

class Page(object):
    def __init__(self, api, data, expand=None):
        self.api = api
        self.data = data

        if 'body' in self.data:
            body = self.data['body']

            if 'storage' in body:
                body = body['storage']

                log.debug("body: %s", body['value'])
                body['value'] = htmlparser.unescape(body['value'])
                log.debug("unescaped body: %s", body['value'])

            elif 'view' in body:
                body = body['view']
                log.debug("unescaped body")
                body['value'] = htmlparser.unescape(body['value'])


        if hasattr(expand, 'split'):
            self.expand = set([ s.strip() for s in expand.split(',') ])
        else:
            self.expand = set(expand)

    def update(self):
        self.api.getPage(self.data['id'], expand=self.expand)

    def __getattr__(self, name):
        if name == 'pageProperties':
            self.pageProperties = [item for item in self.loadPageProperties() ]
            return self.pageProperties

        if name == 'pageProperty':
            self.pageProperty = self.data['pageProperties'] = dict(self.pageProperties)
            return self.pageProperty

        if name == 'labels':
            result = self.api.getLabels(self.data['id'])
            self.labels = [ l['name'] for l in result['results']]
            return self.labels

        if name == 'spacekey':
            return self['spacekey']

        if name == 'content':
            return self['body']['storage']['value']

        if name in self.data:
            return self.data[name]

        raise AttributeError(name)

    def __getitem__(self, name):
        if name == 'pageProperties':
            return self.pageProperty
        if name == 'labels':
            return self.labels

        if name == 'spacekey':
            return self.data['_expandable']['space'].split("/")[-1]
        else:
            return self.data[name]

        raise KeyError(name)

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def dict(self, *keys):
        '''compose new dictionary from given keys'''
        if not len(keys):
            return self.data

        result = {}
        for key in keys:
            result[key] = self[key]

        return result

    def getPageProperty(self, name, default=None):
        return self.pageProperty.get(name, default)

    def getPageProperties(self, *names):
        for k,v in self.pageProperties:
            if len(names):
                if k in names:
                    yield (k,v)
            else:
                yield (k,v)

    def loadPageProperties(self, need_html=False, need_data=False, properties=None, **opts):
        from .page_properties import get_page_properties
        if 'body.view' not in self.expand:
            self.expand.add('body.view')
            self.update()
        html = self.data['body']['view']['value']
        return get_page_properties(html, need_html=need_html, need_data=need_data, properties=properties)
        #self.data['pageProperties'] = dict(get_page_properties(self.data['body']['view']['value']))
