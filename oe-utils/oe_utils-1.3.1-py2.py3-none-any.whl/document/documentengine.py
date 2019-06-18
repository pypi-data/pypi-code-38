# -*- coding: utf-8 -*-
from zope.interface import Interface, implementer
import requests
import json


class IDocumentEngine(Interface):
    def create_documents(self, data, system_token, callback_url=None):
        '''create the documents with incoming data with optional callback_url'''

    def get_document(self, generation_id, system_token, accept='application/pdf'):
        '''get the document. Accept is either application/pdf (default) or either text/html'''


@implementer(IDocumentEngine)
class DocumentEngine(object):
    def __init__(self, baseurl, template_id):
        self.baseurl = baseurl
        self.template_id = template_id

    def create_documents(self, data, system_token, callback_url=None, callback_method=None, template_version=None):
        '''create the documents with incoming data with optional callback_url'''
        generation_data = {
            'template_id': self.template_id,
            'data': data
        }
        if template_version is not None:
            generation_data['template_version'] = template_version
        if callback_url is not None:
            generation_data['callback_method'] = callback_method if callback_method is not None else 'POST'
            generation_data['callback_url'] = callback_url
        headers = {
            'OpenAmSSOID': system_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        res = requests.post('{0}/generations'.format(self.baseurl), json=generation_data, headers=headers)
        res.raise_for_status()
        return json.loads(res.text)['id']

    def get_document(self, generation_id, system_token, accept='application/pdf'):
        '''get the document. Accept is either application/pdf (default) or either text/html'''
        headers = {
            'OpenAmSSOID': system_token,
            'Accept': accept
        }
        res = requests.get('{0}/generations/{1}/document'.format(self.baseurl, generation_id), headers=headers)
        res.raise_for_status()
        return res.content


