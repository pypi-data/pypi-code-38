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
from os import unlink, listdir, makedirs
from os.path import isfile, isdir, join, dirname
from zipfile import ZipFile
from lucterios.CORE.parameters import notfree_mode_connect
from datetime import datetime
from zipfile import BadZipFile

from django.db import models
from django.utils import six, timezone
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.models import LucteriosModel
from lucterios.framework.filetools import get_user_path, readimage_to_base64
from lucterios.framework.signal_and_lock import Signal

from lucterios.CORE.models import LucteriosGroup, LucteriosUser
from lucterios.documents.models_legacy import Folder, Document
from lucterios.documents.doc_editors import DocEditor


class AbstractContainer(LucteriosModel):

    parent = models.ForeignKey('FolderContainer', verbose_name=_('parent'), null=True, on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=250, blank=False)
    description = models.TextField(_('description'), blank=True)

    @classmethod
    def get_default_fields(cls):
        return [('', 'icon'), "name", "description", (_('modifier'), "modif"), (_('date modification'), "date_modif")]

    @property
    def icon(self):
        if isinstance(self.get_final_child(), FolderContainer):
            icon_name = "folder.png"
        else:
            icon_name = "file.png"
        img = readimage_to_base64(join(dirname(__file__), "static", 'lucterios.documents', "images", icon_name))
        return img.decode('ascii')

    @property
    def modif(self):
        final_container = self.get_final_child()
        if isinstance(final_container, DocumentContainer):
            return final_container.modifier
        return None

    @property
    def date_modif(self):
        final_container = self.get_final_child()
        if isinstance(final_container, DocumentContainer):
            return final_container.date_modification
        return None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name[:250]
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('container')
        verbose_name_plural = _('containers')
        default_permissions = []
        ordering = ['-foldercontainer__isnull', 'parent__name', 'name']


class FolderContainer(AbstractContainer):
    viewer = models.ManyToManyField(LucteriosGroup, related_name="foldercontainer_viewer", verbose_name=_('viewer'), blank=True)
    modifier = models.ManyToManyField(LucteriosGroup, related_name="foldercontainer_modifier", verbose_name=_('modifier'), blank=True)

    @classmethod
    def get_show_fields(cls):
        return {_('001@Info'): ["name", "description", "parent"],
                _('001@Permission'): ["viewer", "modifier"]}

    @classmethod
    def get_edit_fields(cls):
        return {_('001@Info'): ["name", "description", "parent"],
                _('001@Permission'): ["viewer", "modifier"]}

    @classmethod
    def get_search_fields(cls):
        return ["name", "description", "parent.name"]

    @classmethod
    def get_default_fields(cls):
        return ["name", "description", "parent"]

    def get_title(self, num=0):
        title = ">" + self.name
        if self.parent is not None:
            if num < 10:
                title = self.parent.get_title(num + 1) + title
            else:
                title = " !! "
        return title

    def __str__(self):
        return self.get_title()

    def is_readonly(self, user):
        readonly = True
        for modifier_item in self.modifier.all():
            if modifier_item in user.groups.all():
                readonly = False
        return readonly

    def cannot_view(self, user):
        cannotview = True
        for viewer_item in self.viewer.all():
            if viewer_item in user.groups.all():
                cannotview = False
        return cannotview

    def get_subfiles(self):
        file_paths = []
        for container in self.abstractcontainer_set.all():
            container = container.get_final_child()
            if isinstance(container, DocumentContainer):
                file_paths.append(container.file_path)
            else:
                file_paths.extend(container.get_subfiles())
        return file_paths

    def delete(self):
        file_paths = self.get_subfiles()
        LucteriosModel.delete(self)
        for file_path in file_paths:
            if isfile(file_path):
                unlink(file_path)

    def import_files(self, dir_to_import, viewers, modifiers, user):
        for filename in listdir(dir_to_import):
            complet_path = join(dir_to_import, filename)
            if isfile(complet_path):
                new_doc = DocumentContainer(name=filename, description=filename, parent_id=self.id)
                if user.is_authenticated:
                    new_doc.creator = LucteriosUser.objects.get(pk=user.id)
                    new_doc.modifier = new_doc.creator
                new_doc.date_modification = timezone.now()
                new_doc.date_creation = new_doc.date_modification
                new_doc.save()
                with open(complet_path, 'rb') as file_content:
                    new_doc.content = file_content.read()
            elif isdir(complet_path):
                new_folder = FolderContainer.objects.create(name=filename, description=filename, parent_id=self.id)
                new_folder.viewer = viewers
                new_folder.modifier = modifiers
                new_folder.save()
                new_folder.import_files(complet_path, viewers, modifiers, user)

    def extract_files(self, dir_to_extract):
        for doc in DocumentContainer.objects.filter(folder_id=self.id):
            if isfile(doc.file_path):
                try:
                    with ZipFile(doc.file_path, 'r') as zip_ref:
                        zip_ref.extractall(dir_to_extract)
                except BadZipFile:
                    pass
        for folder in FolderContainer.objects.filter(parent_id=self.id):
            new_dir_to_extract = join(dir_to_extract, folder.name)
            if not isdir(new_dir_to_extract):
                makedirs(new_dir_to_extract)
            folder.extract_files(new_dir_to_extract)

    class Meta(object):
        verbose_name = _('folder')
        verbose_name_plural = _('folders')
        default_permissions = []
        ordering = ['parent__name', 'name']


class DocumentContainer(AbstractContainer):
    modifier = models.ForeignKey(LucteriosUser, related_name="documentcontainer_modifier",
                                 verbose_name=_('modifier'), null=True, on_delete=models.CASCADE)
    date_modification = models.DateTimeField(verbose_name=_('date modification'), null=False)
    creator = models.ForeignKey(LucteriosUser, related_name="documentcontainer_creator",
                                verbose_name=_('creator'), null=True, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(verbose_name=_('date creation'), null=False)
    sharekey = models.CharField('sharekey', max_length=100, null=True)

    @classmethod
    def get_show_fields(cls):
        return ["name", "parent", "description", ("modifier", "date_modification"), ("creator", "date_creation")]

    @classmethod
    def get_edit_fields(cls):
        return ["parent", "name", "description"]

    @classmethod
    def get_search_fields(cls):
        return ["name", "description", "parent.name", "date_modification", "date_creation"]

    @classmethod
    def get_default_fields(cls):
        return ["name", "description", "date_modification", "modifier"]

    def __init__(self, *args, **kwargs):
        AbstractContainer.__init__(self, *args, **kwargs)
        self.filter = models.Q()
        self.shared_link = None
        self.root_url = None

    def __str__(self):
        return '[%s] %s' % (self.parent, self.name)

    @property
    def file_path(self):
        return get_user_path("documents", "container_%s" % six.text_type(self.id))

    def delete(self):
        file_path = self.file_path
        LucteriosModel.delete(self)
        if isfile(file_path):
            unlink(file_path)

    def set_context(self, xfer):
        if notfree_mode_connect() and not isinstance(xfer, six.text_type) and not xfer.request.user.is_superuser:
            self.filter = models.Q(parent=None) | models.Q(parent__viewer__in=xfer.request.user.groups.all())
        if isinstance(xfer, six.text_type):
            self.root_url = xfer
        else:
            abs_url = xfer.request.META.get('HTTP_REFERER', xfer.request.build_absolute_uri()).split('/')
            self.root_url = '/'.join(abs_url[:-2])
        if self.sharekey is not None:
            import urllib.parse
            self.shared_link = "%s/%s?shared=%s&filename=%s" % (self.root_url, 'lucterios.documents/downloadFile', self.sharekey, urllib.parse.quote(self.name))
        else:
            self.shared_link = None

    @property
    def folder_query(self):
        return FolderContainer.objects.filter(self.filter)

    @property
    def content(self):
        from _io import BytesIO
        if isfile(self.file_path):
            with ZipFile(self.file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if len(file_list) > 0:
                    doc_file = zip_ref.open(file_list[0])
                    return BytesIO(doc_file.read())
        return BytesIO(b'')

    @content.setter
    def content(self, content):
        from _io import BytesIO
        if not isinstance(content, BytesIO) and hasattr(content, 'read'):
            with open(self.file_path, "wb") as file_tmp:
                file_tmp.write(content.read())
        else:
            with ZipFile(self.file_path, 'w') as zip_ref:
                if isinstance(content, BytesIO):
                    content = content.read()
                if isinstance(content, six.text_type):
                    content = content.encode()
                if isinstance(content, six.binary_type):
                    zip_ref.writestr(zinfo_or_arcname=self.name, data=content)

    def change_sharekey(self, clear):
        if clear:
            self.sharekey = None
        else:
            from hashlib import md5
            phrase = "%s %s %s" % (self.name, self.date_creation, datetime.now())
            md5res = md5()
            md5res.update(phrase.encode())
            self.sharekey = md5res.hexdigest()

    def get_doc_editors(self):
        for editor_class in DocEditor.get_all_editor():
            editor_obj = editor_class(self.root_url, self)
            if editor_obj.is_manage():
                return editor_obj
        return None

    class Meta(object):
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        default_permissions = []
        ordering = ['parent__name', 'name']


def migrate_containers(old_parent, new_parent):
    nb_folder = 0
    nb_doc = 0
    for old_document in Document.objects.filter(folder=old_parent):
        new_doc = DocumentContainer(parent=new_parent, name=old_document.name, description=old_document.description)
        new_doc.modifier = old_document.modifier
        new_doc.date_modification = old_document.date_modification
        new_doc.creator = old_document.creator
        new_doc.date_creation = old_document.date_creation
        new_doc.save()
        new_doc.content = old_document.content
        nb_doc += 1

    for old_folder in Folder.objects.filter(parent=old_parent):
        new_folder = FolderContainer.objects.create(parent=new_parent, name=old_folder.name, description=old_folder.description)
        new_folder.viewer.set(old_folder.viewer.all())
        new_folder.modifier.set(old_folder.modifier.all())
        sub_nb_folder, sub_nb_doc = migrate_containers(old_folder, new_folder)
        old_folder.delete()
        nb_folder += sub_nb_folder
        nb_doc += sub_nb_doc
        nb_folder += 1
    if (old_parent is None) and (nb_folder > 0):
        six.print_('Convert containers: folder=%d - documents=%d' % (nb_folder, nb_doc))
    return nb_folder, nb_doc


@Signal.decorate('checkparam')
def documents_checkparam():
    migrate_containers(None, None)
