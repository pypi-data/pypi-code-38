# -*- coding: utf-8 -*-
'''
lucterios.documents package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from hashlib import md5
from urllib.error import URLError
from urllib import request
from requests.exceptions import ConnectionError
from logging import getLogger

from django.conf import settings

from etherpad_lite import EtherpadLiteClient, EtherpadException
from lucterios.documents.ethercalc import EtherCalc


class DocEditor(object):

    SETTING_NAME = "XXX"

    def __init__(self, root_url, doccontainer):
        self.root_url = root_url
        self.doccontainer = doccontainer
        self._client = None
        if hasattr(settings, self.SETTING_NAME):
            self.params = getattr(settings, self.SETTING_NAME)
        else:
            self.params = None

    @classmethod
    def get_all_editor(cls):
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union([subclass_item for class_item in cls.__subclasses__() for subclass_item in all_subclasses(class_item)])
        return all_subclasses(cls)

    @classmethod
    def get_all_extension_supported(cls):
        res = ()
        for cls in cls.get_all_editor():
            if hasattr(settings, cls.SETTING_NAME):
                res += cls.extension_supported()
        return set(res)

    @classmethod
    def extension_supported(cls):
        return ()

    @property
    def docid(self):
        md5res = md5()
        md5res.update(self.root_url.encode())
        return '%s-%d' % (md5res.hexdigest(), self.doccontainer.id)

    def is_manage(self):
        if hasattr(settings, self.SETTING_NAME):
            for ext_item in self.extension_supported():
                if self.doccontainer.name.endswith('.' + ext_item):
                    return True
        return False

    @property
    def client(self):
        return self._client

    def get_iframe(self):
        return "{[iframe]}{[/iframe]}"

    def send_content(self):
        pass

    def save_content(self):
        pass

    def close(self):
        pass


def disabled_ssl():
    def decorator(fn):
        def wrapper(*args, **kw):
            request._opener = EtherPadEditor.OPENER
            try:
                return fn(*args, **kw)
            finally:
                request._opener = None
        return wrapper
    return decorator


class EtherPadEditor(DocEditor):

    SETTING_NAME = "ETHERPAD"

    OPENER = None

    @classmethod
    def init_no_ssl(cls):
        from ssl import create_default_context
        from _ssl import CERT_NONE
        no_check_ssl = create_default_context()
        no_check_ssl.check_hostname = False
        no_check_ssl.verify_mode = CERT_NONE
        EtherPadEditor.OPENER = request.build_opener(request.HTTPSHandler(context=no_check_ssl))

    @classmethod
    def extension_supported(cls):
        if ('url' in settings.ETHERPAD) and ('apikey' in settings.ETHERPAD):
            try:
                cls('', None).check_token()
                return ('txt', 'html')
            except (URLError, EtherpadException) as con_err:
                getLogger('lucterios.documents').debug('extension_supported error=%s', con_err)
        return ()

    @property
    def client(self):
        if self._client is None:
            self._client = EtherpadLiteClient(base_url='%s/api' % self.params['url'], api_version='1.2.13',
                                              base_params={'apikey': self.params['apikey']})
        return self._client

    def get_iframe(self):
        return '{[iframe name="embed_readwrite" src="%s/p/%s" width="100%%" height="450"]}{[/iframe]}' % (self.params['url'], self.docid)

    @disabled_ssl()
    def check_token(self):
        return self.client.checkToken()

    @disabled_ssl()
    def close(self):
        if self.docid in self.client.listAllPads()['padIDs']:
            self.client.deletePad(padID=self.docid)

    @disabled_ssl()
    def send_content(self):
        pad_ids = self.client.listAllPads()['padIDs']
        if not (self.docid in pad_ids):
            self.client.createPad(padID=self.docid, padName=self.doccontainer.name)
        file_ext = self.doccontainer.name.split('.')[-1]

        content = self.doccontainer.content.read()
        if content != b'':
            if file_ext == 'html':
                self.client.setHTML(padID=self.docid, html=content.decode())
            else:
                self.client.setText(padID=self.docid, text=content.decode())

    @disabled_ssl()
    def load_export(self, export_type):
        url = "%s/p/%s/export/%s" % (self.params['url'], self.docid, export_type)
        return request.urlopen(url, timeout=self.client.timeout).read()

    @disabled_ssl()
    def save_content(self):
        file_ext = self.doccontainer.name.split('.')[-1]
        if file_ext == 'etherpad':
            self.doccontainer.content = self.load_export('etherpad')
        elif file_ext == 'html':
            self.doccontainer.content = self.client.getHTML(padID=self.docid)['html']
        else:  # text
            self.doccontainer.content = self.client.getText(padID=self.docid)['text']


if EtherPadEditor.OPENER is None:
    EtherPadEditor.init_no_ssl()


class EtherCalcEditor(DocEditor):

    SETTING_NAME = "ETHERCALC"

    @classmethod
    def extension_supported(cls):
        if hasattr(settings, 'ETHERCALC') and ('url' in settings.ETHERCALC):
            try:
                cls('', None).client.get('')
                return ('csv', 'xlsx', 'ods')
            except ConnectionError as con_err:
                getLogger('lucterios.documents').debug('extension_supported error=%s', con_err)
        return ()

    @property
    def client(self):
        if self._client is None:
            self._client = EtherCalc(url_root='%s' % self.params['url'])
        return self._client

    def get_iframe(self):
        return '{[iframe name="embed_readwrite" src="%s/%s" width="100%%" height="450"]}{[/iframe]}' % (self.params['url'], self.docid)

    def send_content(self):
        file_ext = self.doccontainer.name.split('.')[-1]
        if not self.client.is_exist(self.docid):
            self.client.new(self.docid)
        content = self.doccontainer.content.read()
        if content != b'':
            self.client.update(content, file_ext, self.docid)

    def close(self):
        if self.client.is_exist(self.docid):
            self.client.delete(self.docid)

    def save_content(self):
        if self.client.is_exist(self.docid):
            file_ext = self.doccontainer.name.split('.')[-1]
            self.doccontainer.content = self.client.export(self.docid, file_ext)
