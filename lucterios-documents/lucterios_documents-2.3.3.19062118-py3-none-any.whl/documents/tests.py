# -*- coding: utf-8 -*-
'''
lucterios.contacts package

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
from os.path import join, dirname, exists
from shutil import rmtree
import json

from django.utils import formats, six
from django.contrib.auth.models import Permission
from django.conf import settings

from lucterios.framework.test import LucteriosTest, find_free_port
from lucterios.framework.filetools import get_user_path, get_user_dir

from lucterios.CORE.models import LucteriosGroup, LucteriosUser

from lucterios.documents.models import FolderContainer, DocumentContainer
from lucterios.documents.views import FolderList, FolderAddModify, FolderDel, \
    ContainerList, DocumentAddModify, DocumentShow, ContainerDel, DocumentSearch,\
    DocumentChangeShared, DownloadFile, ContainerAddFile, DocumentEditor
from lucterios.documents.test_tools import default_groups, default_folders,\
    create_doc, TestHTTPServer, TestMoke


class FolderTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        default_groups()

    def test_list(self):
        self.factory.xfer = FolderList()
        self.calljson('/lucterios.documents/folderList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'folderList')
        self.assertEqual(self.json_meta['title'], 'Dossiers')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal(self.json_actions[0], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 3)
        self.assert_coordcomp_equal('folder', (0, 1, 2, 1))
        self.assert_grid_equal('folder', {"name": "nom", "description": "description", "parent": "parent"}, 0)

    def test_add(self):
        self.factory.xfer = FolderAddModify()
        self.calljson('/lucterios.documents/folderAddModify', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'folderAddModify')
        self.assertEqual(self.json_meta['title'], 'Ajouter un dossier')
        self.assert_count_equal('', 8)
        self.assert_comp_equal(('EDIT', 'name'), '', (0, 0, 1, 1, 1))
        self.assert_comp_equal(('MEMO', 'description'), '', (0, 1, 1, 1, 1))
        self.assert_comp_equal(('SELECT', 'parent'), '0', (0, 2, 1, 1, 1))
        self.assert_select_equal('parent', 1)  # nb=1
        self.assert_coordcomp_equal('viewer', (0, 0, 3, 1, 2))
        self.assert_coordcomp_equal('modifier', (0, 1, 3, 1, 2))

    def test_addsave(self):

        folder = FolderContainer.objects.all()
        self.assertEqual(len(folder), 0)

        self.factory.xfer = FolderAddModify()
        self.calljson('/lucterios.documents/folderAddModify', {'SAVE': 'YES', 'name': 'newcat', 'description': 'new folder',
                                                               'parent': '0', 'viewer': '1;2', 'modifier': '2'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'folderAddModify')
        self.assertEqual(len(self.json_context), 5)

        folder = FolderContainer.objects.all()
        self.assertEqual(len(folder), 1)
        self.assertEqual(folder[0].id, 1)
        self.assertEqual(folder[0].name, "newcat")
        self.assertEqual(folder[0].description, "new folder")
        self.assertEqual(folder[0].parent, None)
        grp = folder[0].viewer.all().order_by('id')
        self.assertEqual(len(grp), 2)
        self.assertEqual(grp[0].id, 1)
        self.assertEqual(grp[1].id, 2)
        grp = folder[0].modifier.all().order_by('id')
        self.assertEqual(len(grp), 1)
        self.assertEqual(grp[0].id, 2)

        self.factory.xfer = FolderList()
        self.calljson('/lucterios.documents/folderList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'folderList')
        self.assert_count_equal('folder', 1)

    def test_delete(self):
        folder = FolderContainer.objects.create(name='truc', description='blabla')
        folder.viewer.set(LucteriosGroup.objects.filter(id__in=[1, 2]))
        folder.modifier.set(LucteriosGroup.objects.filter(id__in=[2]))
        folder.save()

        self.factory.xfer = FolderList()
        self.calljson('/lucterios.documents/folderList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'folderList')
        self.assert_count_equal('folder', 1)

        self.factory.xfer = FolderDel()
        self.calljson('/lucterios.documents/folderDel', {'folder': folder.id, "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'folderDel')

        self.factory.xfer = FolderList()
        self.calljson('/lucterios.documents/folderList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'folderList')
        self.assert_count_equal('folder', 0)


class DocumentTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        if hasattr(settings, "ETHERPAD"):
            settings.ETHERPAD = {}
        if hasattr(settings, "ETHERCALC"):
            settings.ETHERCALC = {}

        rmtree(get_user_dir(), True)
        default_groups()
        default_folders()
        self.factory.user = LucteriosUser.objects.get(username='empty')
        self.factory.user.groups.set(LucteriosGroup.objects.filter(id__in=[2]))
        self.factory.user.user_permissions.set(Permission.objects.all())
        self.factory.user.save()

    def test_list(self):
        folder = FolderContainer.objects.all()
        self.assertEqual(len(folder), 4)

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assertEqual(self.json_meta['title'], 'Documents')
        self.assertEqual(len(self.json_context), 0)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_action_equal(self.json_actions[0], ('Fermer', 'images/close.png'))
        self.assert_count_equal('', 10)
        self.assert_coordcomp_equal('container', (0, 3, 2, 1))
        self.assert_grid_equal('container', {'icon': '', "name": "nom", "description": "description", "date_modif": "date de modification", "modif": "modificateur"}, 2)
        self.assert_count_equal("#container/actions", 3)

        self.assert_json_equal('LABELFORM', 'title_folder', ">")
        self.assert_json_equal('LABELFORM', 'desc_folder', '{[center]}{[i]}{[/i]}{[/center]}')

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {"container": "1"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('container', 0)
        self.assert_json_equal('LABELFORM', 'title_folder', ">truc1")
        self.assert_json_equal('LABELFORM', 'desc_folder', "{[center]}{[i]}blabla{[/i]}{[/center]}")
        self.assert_count_equal("#container/actions", 2)

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {"container": "2"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('', 12)
        self.assert_count_equal('container', 1)
        self.assert_count_equal("#container/actions", 3)
        self.assert_json_equal('LABELFORM', 'title_folder', ">truc2")
        self.assert_json_equal('LABELFORM', 'desc_folder', "{[center]}{[i]}bouuuuu!{[/i]}{[/center]}")

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {"container": "3"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('container', 0)
        self.assert_json_equal('LABELFORM', 'title_folder', ">truc2>truc3")
        self.assert_json_equal('LABELFORM', 'desc_folder', "{[center]}{[i]}----{[/i]}{[/center]}")
        self.assert_count_equal("#container/actions", 2)

    def test_add(self):
        self.factory.xfer = DocumentAddModify()
        self.calljson('/lucterios.documents/documentAddModify', {"parent": "2"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentAddModify')
        self.assertEqual(self.json_meta['title'], 'Ajouter un document')
        self.assert_count_equal('', 4)
        self.assert_comp_equal(('SELECT', 'parent'), "2", (1, 0, 1, 1))
        self.assert_comp_equal(('UPLOAD', 'filename'), '', (1, 1, 1, 1))
        self.assert_comp_equal(('MEMO', 'description'), '', (1, 2, 1, 1))

    def test_addsave(self):
        self.factory.user = LucteriosUser.objects.get(username='empty')

        self.assertFalse(exists(get_user_path('documents', 'container_5')))
        file_path = join(dirname(__file__), 'static', 'lucterios.documents', 'images', 'documentFind.png')

        docs = DocumentContainer.objects.all()
        self.assertEqual(len(docs), 0)

        self.factory.xfer = DocumentAddModify()
        with open(file_path, 'rb') as file_to_load:
            self.calljson('/lucterios.documents/documentAddModify', {"parent": "2", 'SAVE': 'YES', 'description': 'new doc',
                                                                     'filename_FILENAME': 'doc.png', 'filename': file_to_load}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentAddModify')
        self.assertEqual(len(self.json_context), 3)

        docs = DocumentContainer.objects.all()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].parent.id, 2)
        self.assertEqual(docs[0].name, 'doc.png')
        self.assertEqual(docs[0].description, "new doc")
        self.assertEqual(docs[0].creator.username, "empty")
        self.assertEqual(docs[0].modifier.username, "empty")
        self.assertEqual(docs[0].date_creation, docs[0].date_modification)
        self.assertTrue(exists(get_user_path('documents', 'container_5')))

    def test_saveagain(self):
        current_date = create_doc(self.factory.user)

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "5"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentShow')
        self.assertEqual(self.json_meta['title'], "Afficher le document")
        self.assert_count_equal('', 9)
        self.assert_comp_equal(('LABELFORM', 'name'), "doc1.png", (1, 0, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'parent'), ">truc2", (1, 1, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'description'), "doc 1", (1, 2, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'modifier'), '---', (1, 3, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'date_modification'), formats.date_format(current_date, "DATETIME_FORMAT"), (2, 3, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'creator'), "empty", (1, 4, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'date_creation'), formats.date_format(current_date, "DATETIME_FORMAT"), (2, 4, 1, 1))
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = DocumentAddModify()
        self.calljson('/lucterios.documents/documentAddModify', {'SAVE': 'YES', "document": "5", 'description': 'old doc', 'parent': 3}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentAddModify')
        docs = DocumentContainer.objects.all().order_by('id')
        self.assertEqual(len(docs), 3)
        self.assertEqual(docs[0].id, 5)
        self.assertEqual(docs[0].parent.id, 3)
        self.assertEqual(docs[0].name, 'doc1.png')
        self.assertEqual(docs[0].description, "old doc")
        self.assertEqual(docs[0].creator.username, "empty")
        self.assertEqual(docs[0].modifier.username, "empty")
        self.assertNotEqual(docs[0].date_creation, docs[0].date_modification)

    def test_create_pad(self):
        port = find_free_port()
        settings.ETHERPAD = {'url': 'http://localhost:%d' % port, 'apikey': 'abc123'}

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('', 10)
        self.assert_count_equal('container', 2)
        self.assert_count_equal("#container/actions", 3)

        TestMoke.content_type = "application/json"
        httpd = TestHTTPServer(('localhost', port))
        httpd.start()
        try:
            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}'])
            self.factory.xfer = ContainerList()
            self.calljson('/lucterios.documents/containerList', {}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
            self.assert_count_equal('container', 2)
            self.assert_count_equal("#container/actions", 4)
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 1)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))

            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}'])
            self.factory.xfer = ContainerAddFile()
            self.calljson('/lucterios.documents/containerAddFile', {}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'containerAddFile')
            self.assert_count_equal('', 5)
            self.assert_select_equal('docext', {'txt': 'txt', 'html': 'html'})  # nb=2
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 1)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))

            self.factory.xfer = ContainerAddFile()
            self.calljson('/lucterios.documents/containerAddFile', {'name': 'aa.bb.cc', 'docext': 'txt', 'description': 'blablabla', 'CONFIRME': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'containerAddFile')
            self.assertEqual(self.response_json['action']['id'], "lucterios.documents/documentEditor")
            self.assertEqual(len(self.response_json['action']['params']), 1)
            self.assertEqual(self.response_json['action']['params']['document'], 5)

            TestMoke.initial(['{"code":4,"message":"no or wrong API Key","data":null}'])
            self.factory.xfer = ContainerList()
            self.calljson('/lucterios.documents/containerList', {}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
            self.assert_count_equal('container', 3)
            self.assert_count_equal("#container/actions", 3)
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 1)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))

            new_doc = DocumentContainer.objects.get(id=5)
            self.assertEqual(new_doc.parent_id, None)
            self.assertEqual(new_doc.name, 'aa.bb.txt')
            self.assertEqual(new_doc.description, "blablabla")
            self.assertTrue(exists(get_user_path('documents', 'container_5')))

            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}',
                              '{"code": 0, "message":"ok", "data": null}'])
            editor = new_doc.get_doc_editors()
            editor.root_url = 'http://testserver'
            self.assertEqual(editor.docid, 'edb6edba72798a8d49e95bf2f107ea10-5')
            json_test = editor.load_export('txt').decode('utf-8')
            self.assertEqual(json_test, '{"code": 0, "message":"ok", "data": null}')
            self.assertEqual(json.loads(json_test), {'code': 0, 'message': "ok", 'data': None})
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 2)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[1], '/p/edb6edba72798a8d49e95bf2f107ea10-5/export/txt')

            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}',
                              '{"code": 0, "message":"ok", "data": {"padIDs":[]}}',
                              '{"code": 0, "message":"ok", "data": null}'])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 3)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[1], ('/api/1.2.13/listAllPads', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[2], ('/api/1.2.13/createPad', {'apikey': ['abc123'],
                                                                              'padName': ['aa.bb.txt'],
                                                                              'padID': ['edb6edba72798a8d49e95bf2f107ea10-5']}))

            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}',
                              '{"code": 0, "message":"ok", "data": {"text":"blablabla"}}'])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5, 'SAVE': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 2)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[1], ('/api/1.2.13/getText', {'apikey': ['abc123'],
                                                                            'padID': ['edb6edba72798a8d49e95bf2f107ea10-5']}))

            TestMoke.initial(['{"code": 0, "message":"ok", "data": null}',
                              '{"code": 0, "message":"ok", "data": {"padIDs":["edb6edba72798a8d49e95bf2f107ea10-5"]}}',
                              '{"code": 0, "message":"ok", "data": null}'])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5, 'CLOSE': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 3)
            self.assertEqual(TestMoke.requests[0], ('/api/1.2.13/checkToken', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[1], ('/api/1.2.13/listAllPads', {'apikey': ['abc123']}))
            self.assertEqual(TestMoke.requests[2], ('/api/1.2.13/deletePad', {'apikey': ['abc123'],
                                                                              'padID': ['edb6edba72798a8d49e95bf2f107ea10-5']}))
        finally:
            httpd.shutdown()

    def test_create_calc(self):
        port = find_free_port()
        settings.ETHERCALC = {'url': 'http://localhost:%d' % port}

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('', 10)
        self.assert_count_equal('container', 2)
        self.assert_count_equal("#container/actions", 3)

        TestMoke.content_type = "application/json"
        httpd = TestHTTPServer(('localhost', port))
        httpd.start()
        try:
            TestMoke.initial([''])
            self.factory.xfer = ContainerList()
            self.calljson('/lucterios.documents/containerList', {}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
            self.assert_count_equal('container', 2)
            self.assert_count_equal("#container/actions", 4)
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 1)
            self.assertEqual(TestMoke.requests[0], '/')

            TestMoke.initial([''])
            self.factory.xfer = ContainerAddFile()
            self.calljson('/lucterios.documents/containerAddFile', {}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'containerAddFile')
            self.assert_count_equal('', 5)
            self.assert_select_equal('docext', {'csv': 'csv', 'xlsx': 'xlsx', 'ods': 'ods'})  # nb=3
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 1)
            self.assertEqual(TestMoke.requests[0], '/')

            self.factory.xfer = ContainerAddFile()
            self.calljson('/lucterios.documents/containerAddFile', {'name': 'aa.bb.cc', 'docext': 'csv', 'description': 'blablabla', 'CONFIRME': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'containerAddFile')
            self.assertEqual(self.response_json['action']['id'], "lucterios.documents/documentEditor")
            self.assertEqual(len(self.response_json['action']['params']), 1)
            self.assertEqual(self.response_json['action']['params']['document'], 5)

            new_doc = DocumentContainer.objects.get(id=5)
            self.assertEqual(new_doc.parent_id, None)
            self.assertEqual(new_doc.name, 'aa.bb.csv')
            self.assertEqual(new_doc.description, "blablabla")
            self.assertTrue(exists(get_user_path('documents', 'container_5')))

            TestMoke.initial(['', 'false', ''])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5}, False)
            self.assert_observer('core.custom', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 3)
            self.assertEqual(TestMoke.requests[0], '/')
            self.assertEqual(TestMoke.requests[1], '/_exists/edb6edba72798a8d49e95bf2f107ea10-5')
            self.assertEqual(TestMoke.requests[2], ('PUT', '/_/edb6edba72798a8d49e95bf2f107ea10-5', {}))

            TestMoke.initial(['', 'true', ''])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5, 'SAVE': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 3)
            self.assertEqual(TestMoke.requests[0], '/')
            self.assertEqual(TestMoke.requests[1], '/_exists/edb6edba72798a8d49e95bf2f107ea10-5')
            self.assertEqual(TestMoke.requests[2], '/edb6edba72798a8d49e95bf2f107ea10-5.csv')

            TestMoke.initial(['', 'true', ''])
            self.factory.xfer = DocumentEditor()
            self.calljson('/lucterios.documents/documentEditor', {'document': 5, 'CLOSE': 'YES'}, False)
            self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentEditor')
            self.assertEqual(TestMoke.results, [])
            self.assertEqual(len(TestMoke.requests), 3)
            self.assertEqual(TestMoke.requests[0], '/')
            self.assertEqual(TestMoke.requests[1], '/_exists/edb6edba72798a8d49e95bf2f107ea10-5')
            self.assertEqual(TestMoke.requests[2], ('DELETE', '/_/edb6edba72798a8d49e95bf2f107ea10-5'))
        finally:
            httpd.shutdown()

    def test_delete(self):
        current_date = create_doc(self.factory.user)

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {"current_folder": "2"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'containerList')
        self.assert_count_equal('container', 2)
        self.assert_json_equal('', "container/@0/id", "3")
        self.assert_json_equal('', "container/@0/name", "truc3")
        self.assert_json_equal('', "container/@0/description", "----")
        self.assert_json_equal('', "container/@0/date_modif", "---")
        self.assert_json_equal('', "container/@0/modif", "---")
        self.assert_json_equal('', "container/@1/id", "5")
        self.assert_json_equal('', "container/@1/name", "doc1.png")
        self.assert_json_equal('', "container/@1/description", "doc 1")
        self.assert_json_equal('', "container/@1/date_modif", six.text_type(current_date))
        self.assert_json_equal('', "container/@1/modif", "---")

        self.assertTrue(exists(get_user_path('documents', 'container_5')))

        self.factory.xfer = ContainerDel()
        self.calljson('/lucterios.documents/containerDel', {"container": "5", "CONFIRME": 'YES'}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'containerDel')

        self.factory.xfer = ContainerList()
        self.calljson('/lucterios.documents/containerList', {"current_folder": "2"}, False)
        self.assert_count_equal('container', 1)
        self.assert_json_equal('', "container/@0/id", "3")
        self.assertFalse(exists(get_user_path('documents', 'container_5')))

    def test_readonly(self):
        current_date = create_doc(self.factory.user)

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "6"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentShow')
        self.assertEqual(self.json_meta['title'], "Afficher le document")
        self.assert_count_equal('', 9)
        self.assert_comp_equal(('LABELFORM', 'name'), "doc2.png", (1, 0, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'parent'), ">truc1", (1, 1, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'description'), "doc 2", (1, 2, 2, 1))
        self.assert_comp_equal(('LABELFORM', 'modifier'), '---', (1, 3, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'date_modification'), formats.date_format(current_date, "DATETIME_FORMAT"), (2, 3, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'creator'), "empty", (1, 4, 1, 1))
        self.assert_comp_equal(('LABELFORM', 'date_creation'), formats.date_format(current_date, "DATETIME_FORMAT"), (2, 4, 1, 1))
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = DocumentAddModify()
        self.calljson('/lucterios.documents/documentAddModify', {"document": "6"}, False)
        self.assert_observer('core.exception', 'lucterios.documents', 'documentAddModify')
        self.assert_json_equal('', 'message', "Écriture non autorisée !")

        self.factory.xfer = ContainerDel()
        self.calljson('/lucterios.documents/containerDel', {"container": "6"}, False)
        self.assert_observer('core.exception', 'lucterios.documents', 'containerDel')
        self.assert_json_equal('', 'message', "Écriture non autorisée !")

    def test_cannot_view(self):
        create_doc(self.factory.user)

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "7"}, False)
        self.assert_observer('core.exception', 'lucterios.documents', 'documentShow')
        self.assert_json_equal('', 'message', "Visualisation non autorisée !")

        self.factory.xfer = DocumentAddModify()
        self.calljson('/lucterios.documents/documentAddModify', {"document": "7"}, False)
        self.assert_observer('core.exception', 'lucterios.documents', 'documentAddModify')
        self.assert_json_equal('', 'message', "Visualisation non autorisée !")

        self.factory.xfer = ContainerDel()
        self.calljson('/lucterios.documents/containerDel', {"container": "7"}, False)
        self.assert_observer('core.exception', 'lucterios.documents', 'containerDel')
        self.assert_json_equal('', 'message', "Visualisation non autorisée !")

    def test_search(self):
        create_doc(self.factory.user)

        docs = DocumentContainer.objects.filter(name__endswith='.png')
        self.assertEqual(len(docs), 3)

        self.factory.xfer = DocumentSearch()
        self.calljson('/lucterios.documents/documentSearch', {'CRITERIA': 'name||7||.png'}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentSearch')
        self.assert_count_equal('document', 2)

    def test_shared(self):
        create_doc(self.factory.user)

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "5"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentShow')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', 'name', "doc1.png")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = DocumentChangeShared()
        self.calljson('/lucterios.documents/documentChangeShared', {"document": "5"}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentChangeShared')

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "5"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentShow')
        self.assert_count_equal('', 10)
        self.assert_json_equal('LABELFORM', 'name', "doc1.png")
        self.assert_json_equal('EDIT', 'shared_link', "http://testserver/lucterios.documents/downloadFile?", True)
        self.assertEqual(len(self.json_actions), 3)

        shared_link = self.get_json_path('shared_link').split('?')[-1].split('&')
        self.assertEqual(len(shared_link), 2)
        self.assertEqual(shared_link[0][:7], 'shared=')
        shared_key = shared_link[0][7:]
        self.assertEqual(shared_link[1], 'filename=doc1.png')

        self.factory.xfer = DownloadFile()
        self.call_ex('/lucterios.documents/downloadFile', {"shared": shared_key, "filename": "doc1.png"}, False)
        file_content = self.response.getvalue()
        self.assertEqual(file_content[:4], b'\x89PNG')

        self.factory.xfer = DocumentChangeShared()
        self.calljson('/lucterios.documents/documentChangeShared', {"document": "5"}, False)
        self.assert_observer('core.acknowledge', 'lucterios.documents', 'documentChangeShared')

        self.factory.xfer = DocumentShow()
        self.calljson('/lucterios.documents/documentShow', {"document": "5"}, False)
        self.assert_observer('core.custom', 'lucterios.documents', 'documentShow')
        self.assert_count_equal('', 9)
        self.assert_json_equal('LABELFORM', 'name', "doc1.png")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = DownloadFile()
        self.call_ex('/lucterios.documents/downloadFile', {"shared": shared_key, "filename": "doc1.png"}, False)
        file_content = self.response.getvalue().decode()
        self.assertEqual(file_content, 'Fichier non trouvé !')
