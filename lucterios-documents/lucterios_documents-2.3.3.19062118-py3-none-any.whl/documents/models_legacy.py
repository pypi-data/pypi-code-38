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
from os.path import isfile, isdir, join
from zipfile import ZipFile
from lucterios.CORE.parameters import notfree_mode_connect
from datetime import datetime
from zipfile import BadZipFile

from django.db import models
from django.utils import six, timezone
from django.utils.translation import ugettext_lazy as _

from lucterios.framework.models import LucteriosModel
from lucterios.framework.filetools import get_user_path
from lucterios.CORE.models import LucteriosGroup, LucteriosUser


class Folder(LucteriosModel):
    name = models.CharField(_('name'), max_length=250, blank=False)
    description = models.TextField(_('description'), blank=False)
    parent = models.ForeignKey(
        'Folder', verbose_name=_('parent'), null=True, on_delete=models.CASCADE)
    viewer = models.ManyToManyField(
        LucteriosGroup, related_name="folder_viewer", verbose_name=_('viewer'), blank=True)
    modifier = models.ManyToManyField(
        LucteriosGroup, related_name="folder_modifier", verbose_name=_('modifier'), blank=True)

    viewer__titles = [_("Available group viewers"), _("Chosen group viewers")]
    modifier__titles = [
        _("Available group modifiers"), _("Chosen group modifiers")]

    @classmethod
    def get_show_fields(cls):
        return {_('001@Info'): ["name", "description", "parent"], _('001@Permission'): ["viewer", "modifier"]}

    @classmethod
    def get_edit_fields(cls):
        return {_('001@Info'): ["name", "description", "parent"], _('001@Permission'): ["viewer", "modifier"]}

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

    def delete(self):
        file_paths = []
        docs = self.document_set.all()
        for doc in docs:
            file_paths.append(
                get_user_path("documents", "document_%s" % six.text_type(doc.id)))
        LucteriosModel.delete(self)
        for file_path in file_paths:
            if isfile(file_path):
                unlink(file_path)

    def import_files(self, dir_to_import, viewers, modifiers, user):
        for filename in listdir(dir_to_import):
            complet_path = join(dir_to_import, filename)
            if isfile(complet_path):
                new_doc = Document(
                    name=filename, description=filename, folder_id=self.id)
                if user.is_authenticated:
                    new_doc.creator = LucteriosUser.objects.get(pk=user.id)
                    new_doc.modifier = new_doc.creator
                new_doc.date_modification = timezone.now()
                new_doc.date_creation = new_doc.date_modification
                new_doc.save()
                file_path = get_user_path(
                    "documents", "document_%s" % six.text_type(new_doc.id))
                with ZipFile(file_path, 'w') as zip_ref:
                    zip_ref.write(complet_path, arcname=filename)
            elif isdir(complet_path):
                new_folder = Folder.objects.create(
                    name=filename, description=filename, parent_id=self.id)
                new_folder.viewer = viewers
                new_folder.modifier = modifiers
                new_folder.save()
                new_folder.import_files(complet_path, viewers, modifiers, user)

    def extract_files(self, dir_to_extract):
        for doc in Document.objects.filter(folder_id=self.id):
            file_path = get_user_path(
                "documents", "document_%s" % six.text_type(doc.id))
            if isfile(file_path):
                try:
                    with ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(dir_to_extract)
                except BadZipFile:
                    pass
        for folder in Folder.objects.filter(parent_id=self.id):
            new_dir_to_extract = join(dir_to_extract, folder.name)
            if not isdir(new_dir_to_extract):
                makedirs(new_dir_to_extract)
            folder.extract_files(new_dir_to_extract)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name[:250]
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('folder')
        verbose_name_plural = _('folders')
        ordering = ['parent__name', 'name']


class Document(LucteriosModel):
    folder = models.ForeignKey(
        'Folder', verbose_name=_('folder'), null=True, on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=250, blank=False)
    description = models.TextField(_('description'), blank=False)
    modifier = models.ForeignKey(LucteriosUser, related_name="document_modifier", verbose_name=_(
        'modifier'), null=True, on_delete=models.CASCADE)
    date_modification = models.DateTimeField(
        verbose_name=_('date modification'), null=False)
    creator = models.ForeignKey(LucteriosUser, related_name="document_creator", verbose_name=_(
        'creator'), null=True, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(
        verbose_name=_('date creation'), null=False)
    sharekey = models.CharField('sharekey', max_length=100, null=True)

    @classmethod
    def get_show_fields(cls):
        return ["name", "folder", "description", ("modifier", "date_modification"), ("creator", "date_creation")]

    @classmethod
    def get_edit_fields(cls):
        return ["folder", "name", "description"]

    @classmethod
    def get_search_fields(cls):
        return ["name", "description", "folder.name", "date_modification", "date_creation"]

    @classmethod
    def get_default_fields(cls):
        return ["name", "description", "date_modification", "modifier"]

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.filter = models.Q()
        self.shared_link = None

    def __str__(self):
        return '[%s] %s' % (self.folder, self.name)

    def delete(self):
        file_path = get_user_path("documents", "document_%s" % six.text_type(self.id))
        LucteriosModel.delete(self)
        if isfile(file_path):
            unlink(file_path)

    def set_context(self, xfer):
        if notfree_mode_connect() and not isinstance(xfer, six.text_type) and not xfer.request.user.is_superuser:
            self.filter = models.Q(folder=None) | models.Q(folder__viewer__in=xfer.request.user.groups.all())
        if self.sharekey is not None:
            import urllib.parse
            if isinstance(xfer, six.text_type):
                root_url = xfer
            else:
                abs_url = xfer.request.META.get('HTTP_REFERER', xfer.request.build_absolute_uri()).split('/')
                root_url = '/'.join(abs_url[:-2])
            self.shared_link = "%s/%s?shared=%s&filename=%s" % (root_url, 'lucterios.documents/downloadFile', self.sharekey, urllib.parse.quote(self.name))
        else:
            self.shared_link = None

    @property
    def folder_query(self):
        return Folder.objects.filter(self.filter)

    @property
    def content(self):
        from _io import BytesIO
        file_path = get_user_path("documents", "document_%s" % six.text_type(self.id))
        if isfile(file_path):
            with ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                if len(file_list) > 0:
                    doc_file = zip_ref.open(file_list[0])
                    return BytesIO(doc_file.read())
        return BytesIO(b'')

    def change_sharekey(self, clear):
        if clear:
            self.sharekey = None
        else:
            from hashlib import md5
            phrase = "%s %s %s" % (self.name, self.date_creation, datetime.now())
            md5res = md5()
            md5res.update(phrase.encode())
            self.sharekey = md5res.hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name[:250]
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['folder__name', 'name']
