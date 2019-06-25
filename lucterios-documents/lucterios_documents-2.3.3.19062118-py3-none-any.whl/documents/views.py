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
from os.path import join, exists
from os import makedirs, walk
from shutil import rmtree
from zipfile import ZipFile
from logging import getLogger

from django.utils.translation import ugettext_lazy as _
from django.apps.registry import apps
from django.db.models import Q
from django.db.models.query import QuerySet

from lucterios.framework.xferadvance import XferListEditor, XferDelete, XferAddEditor, XferShowEditor,\
    TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_EDIT, TITLE_CANCEL, TITLE_OK,\
    TEXT_TOTAL_NUMBER, TITLE_CLOSE, TITLE_SAVE
from lucterios.framework.xfersearch import XferSearchEditor
from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, ActionsManage, \
    CLOSE_NO, FORMTYPE_REFRESH, SELECT_SINGLE, SELECT_NONE, \
    WrapAction, CLOSE_YES, SELECT_MULTI
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm, \
    XferCompImage, XferCompUpLoad, XferCompDownLoad, XferCompSelect
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_tmp_dir, get_user_dir
from lucterios.CORE.parameters import notfree_mode_connect
from lucterios.CORE.models import LucteriosGroup
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor

from lucterios.documents.models import FolderContainer, DocumentContainer, AbstractContainer
from lucterios.documents.doc_editors import DocEditor


MenuManage.add_sub("documents.conf", "core.extensions", "", _("Document"), "", 10)


@MenuManage.describ('documents.change_folder', FORMTYPE_NOMODAL, 'documents.conf', _("Management of document's folders"))
class FolderList(XferListEditor):
    caption = _("Folders")
    icon = "documentConf.png"
    model = FolderContainer
    field_id = 'folder'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('documents.add_folder')
class FolderAddModify(XferAddEditor):
    icon = "documentConf.png"
    model = FolderContainer
    field_id = 'folder'
    caption_add = _("Add folder")
    caption_modify = _("Modify folder")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('documents.delete_folder')
class FolderDel(XferDelete):
    caption = _("Delete folder")
    icon = "documentConf.png"
    model = FolderContainer
    field_id = 'folder'


class FolderImportExport(XferContainerAcknowledge):
    icon = "documentConf.png"
    model = FolderContainer
    field_id = 'folder'

    def add_components(self, dlg):
        pass

    def run_archive(self):
        pass

    def fillresponse(self):
        if self.getparam('SAVE') is None:
            dlg = self.create_custom()
            dlg.item = self.item
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 3)
            dlg.add_component(img)
            lbl = XferCompLabelForm('title')
            lbl.set_value_as_title(self.caption)
            lbl.set_location(1, 0, 6)
            dlg.add_component(lbl)

            dlg.fill_from_model(1, 1, False, desc_fields=['parent'])
            parent = dlg.get_components('parent')
            parent.colspan = 3

            self.add_components(dlg)
            dlg.add_action(self.get_action(TITLE_OK, "images/ok.png"), close=CLOSE_YES, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            if self.getparam("parent", 0) != 0:
                self.item = FolderContainer.objects.get(id=self.getparam("parent", 0))
            else:
                self.item = FolderContainer()
            self.run_archive()


@ActionsManage.affect_grid(_("Import"), "zip.png", unique=SELECT_NONE)
@MenuManage.describ('documents.add_folder')
class FolderImport(FolderImportExport):
    caption = _("Import")

    def add_components(self, dlg):
        dlg.fill_from_model(1, 2, False, desc_fields=['viewer', 'modifier'])
        zipfile = XferCompUpLoad('zipfile')
        zipfile.http_file = True
        zipfile.description = _('zip file')
        zipfile.maxsize = 1024 * 1024 * 1024  # 1Go
        zipfile.add_filter('.zip')
        zipfile.set_location(1, 15)
        dlg.add_component(zipfile)

    def run_archive(self):
        viewerids = self.getparam("viewer", ())
        modifierids = self.getparam("modifier", ())
        if 'zipfile' in self.request.FILES.keys():
            upload_file = self.request.FILES['zipfile']
            tmp_dir = join(get_tmp_dir(), 'zipfile')
            if exists(tmp_dir):
                rmtree(tmp_dir)
            makedirs(tmp_dir)
            try:
                with ZipFile(upload_file, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                viewers = LucteriosGroup.objects.filter(id__in=viewerids)
                modifiers = LucteriosGroup.objects.filter(id__in=modifierids)
                self.item.import_files(
                    tmp_dir, viewers, modifiers, self.request.user)
            finally:
                if exists(tmp_dir):
                    rmtree(tmp_dir)


@ActionsManage.affect_grid(_("Extract"), "zip.png", unique=SELECT_NONE)
@MenuManage.describ('documents.add_folder')
class FolderExtract(FolderImportExport):
    caption = _("Extract")

    def open_zipfile(self, filename):
        dlg = self.create_custom()
        dlg.item = self.item
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        dlg.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(self.caption)
        lbl.set_location(1, 0, 6)
        dlg.add_component(lbl)
        zipdown = XferCompDownLoad('filename')
        zipdown.compress = False
        zipdown.http_file = True
        zipdown.maxsize = 0
        zipdown.set_value(filename)
        zipdown.set_download(filename)
        zipdown.set_location(1, 15, 2)
        dlg.add_component(zipdown)

    def run_archive(self):
        tmp_dir = join(get_tmp_dir(), 'zipfile')
        download_file = join(get_user_dir(), 'extract.zip')
        if exists(tmp_dir):
            rmtree(tmp_dir)
        makedirs(tmp_dir)
        try:
            self.item.extract_files(tmp_dir)
            with ZipFile(download_file, 'w') as zip_ref:
                for (dirpath, _dirs, filenames) in walk(tmp_dir):
                    for filename in filenames:
                        zip_ref.write(
                            join(dirpath, filename), join(dirpath[len(tmp_dir):], filename))
        finally:
            if exists(tmp_dir):
                rmtree(tmp_dir)
        self.open_zipfile('extract.zip')


if not apps.is_installed("lucterios.contacts"):
    MenuManage.add_sub("office", None, "lucterios.documents/images/office.png", _("Office"), _("Office tools"), 70)

MenuManage.add_sub("documents.actions", "office", "lucterios.documents/images/document.png",
                   _("Documents"), _("Documents storage tools"), 80)


def docshow_modify_condition(xfer):
    if xfer.item.parent is not None and notfree_mode_connect() and not xfer.request.user.is_superuser:
        if xfer.item.parent.cannot_view(xfer.request.user):
            raise LucteriosException(IMPORTANT, _("No allow to view!"))
        if xfer.item.parent.is_readonly(xfer.request.user):
            return False
    return True


def folder_notreadonly_condition(xfer, gridname=''):
    if notfree_mode_connect() and not xfer.request.user.is_superuser:
        if xfer.current_folder > 0:
            folder = FolderContainer.objects.get(id=xfer.current_folder)
            if folder.cannot_view(xfer.request.user):
                raise LucteriosException(IMPORTANT, _("No allow to view!"))
            if folder.is_readonly(xfer.request.user):
                return False
    return True


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=docshow_modify_condition)
@MenuManage.describ('documents.add_document')
class DocumentAddModify(XferAddEditor):
    icon = "document.png"
    model = DocumentContainer
    field_id = 'document'
    caption_add = _("Add document")
    caption_modify = _("Modify document")

    def fillresponse(self):
        if not docshow_modify_condition(self):
            raise LucteriosException(IMPORTANT, _("No allow to write!"))
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('documents.change_document')
class DocumentShow(XferShowEditor):
    caption = _("Show document")
    icon = "document.png"
    model = DocumentContainer
    field_id = 'document'


@ActionsManage.affect_show(_('Editor'), "file.png", modal=FORMTYPE_NOMODAL,
                           close=CLOSE_YES, condition=lambda xfer: xfer.item.get_doc_editors() is not None)
@MenuManage.describ('documents.add_document')
class DocumentEditor(XferContainerAcknowledge):
    caption = _("Edit document")
    icon = "document.png"
    model = DocumentContainer
    field_id = 'document'

    def fillresponse(self):
        editor = self.item.get_doc_editors()
        if self.getparam('SAVE', '') == 'YES':
            editor.save_content()
        elif self.getparam('CLOSE', '') == 'YES':
            editor.close()
        else:
            editor.send_content()
            dlg = self.create_custom(self.model)
            dlg.item = self.item
            dlg.fill_from_model(0, 0, True, [('parent', 'name')])
            frame = XferCompLabelForm('frame')
            frame.set_value(editor.get_iframe())
            frame.set_location(0, 2, 2, 0)
            dlg.add_component(frame)
            dlg.add_action(self.get_action(TITLE_SAVE, 'images/save.png'), close=CLOSE_NO, params={'SAVE': 'YES'})
            dlg.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))
            dlg.set_close_action(self.get_action(), params={'CLOSE': 'YES'})


@ActionsManage.affect_grid(_('Folder'), "images/add.png")
@MenuManage.describ('documents.add_folder')
class ContainerAddFolder(XferContainerAcknowledge):
    caption = _("Add folder")
    icon = "document.png"
    model = AbstractContainer
    field_id = 'container'

    def fillresponse(self, current_folder=0):
        self.redirect_action(FolderAddModify.get_action(), close=CLOSE_YES, params={'parent': current_folder})


def file_createnew_condition(xfer, gridname=''):
    if folder_notreadonly_condition(xfer, gridname):
        return (len(DocEditor.get_all_extension_supported()) > 0)
    else:
        return False


@ActionsManage.affect_grid(_('File'), "images/add.png", condition=file_createnew_condition)
@MenuManage.describ('documents.add_document')
class ContainerAddFile(XferContainerAcknowledge):
    caption = _("Create document")
    icon = "document.png"
    model = AbstractContainer
    field_id = 'container'

    def _initialize(self, request, *_, **kwargs):
        self.model = DocumentContainer
        self.field_id = 'document'
        XferContainerAcknowledge._initialize(self, request, *_, **kwargs)

    def fillresponse(self, current_folder=0, docext=""):
        if current_folder == 0:
            self.item.parent_id = None
        else:
            self.item.parent_id = current_folder
        if self.getparam('CONFIRME', '') == 'YES':
            self.params = {}
            filename_spited = self.item.name.split('.')
            if len(filename_spited) > 1:
                filename_spited = filename_spited[:-1]
            self.item.name = "%s.%s" % (".".join(filename_spited), docext)
            self.item.editor.before_save(self)
            self.item.save()
            self.item.content = ""
            self.redirect_action(DocumentEditor.get_action(), modal=FORMTYPE_NOMODAL, close=CLOSE_YES, params={'document': self.item.id})
        else:
            dlg = self.create_custom(self.model)
            max_row = dlg.get_max_row() + 1
            img = XferCompImage('img')
            img.set_value(self.icon_path())
            img.set_location(0, 0, 1, 6)
            dlg.add_component(img)
            dlg.fill_from_model(1, max_row, True, ['parent'])
            dlg.fill_from_model(1, max_row + 1, False, ['name', 'description'])

            max_row = dlg.get_max_row() + 1
            select = XferCompSelect('docext')
            select.set_select([(item, item) for item in DocEditor.get_all_extension_supported()])
            select.set_value(select.select_list[0][1])
            select.set_location(1, max_row)
            select.description = _('document type')
            dlg.add_component(select)
            dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), close=CLOSE_YES, params={'CONFIRME': 'YES'})
            dlg.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=folder_notreadonly_condition)
@MenuManage.describ('documents.delete_document')
class ContainerDel(XferDelete):
    caption = _("Delete document")
    icon = "document.png"
    model = AbstractContainer
    field_id = 'container'

    def fillresponse(self):
        parent = None
        if len(self.items) > 0:
            parent = self.items[0].parent
        if not WrapAction.is_permission(self.request, 'documents.delete_folder'):
            for item in self.items:
                if isinstance(item.get_final_child(), FolderContainer):
                    raise LucteriosException(IMPORTANT, _("No allow to delete folder!"))
        if parent is not None and notfree_mode_connect() and not self.request.user.is_superuser:
            if parent.cannot_view(self.request.user):
                raise LucteriosException(IMPORTANT, _("No allow to view!"))
            if parent.is_readonly(self.request.user):
                raise LucteriosException(IMPORTANT, _("No allow to write!"))
        XferDelete.fillresponse(self)


@ActionsManage.affect_grid(TITLE_EDIT, "images/edit.png", close=CLOSE_NO, modal=FORMTYPE_REFRESH, unique=SELECT_SINGLE)
@MenuManage.describ('documents.change_document', FORMTYPE_NOMODAL, 'documents.actions', _("Management of documents"))
class ContainerList(XferListEditor):
    caption = _("Documents")
    icon = "document.png"
    model = AbstractContainer
    field_id = 'container'

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        if notfree_mode_connect() and not self.request.user.is_superuser:
            new_items = []
            for item in items:
                item = item.get_final_child()
                if isinstance(item, DocumentContainer) or not item.cannot_view(self.request.user):
                    new_items.append(item)
            items = QuerySet(model=AbstractContainer)
            items._result_cache = new_items
        return items

    def fillresponse_header(self):
        if 'container' in self.params:
            del self.params['container']
        if (self.item is not None) and (self.item.id is not None) and isinstance(self.item, FolderContainer):
            self.params['current_folder'] = self.item.id
        self.current_folder = self.getparam('current_folder', 0)
        if self.current_folder > 0:
            self.filter = Q(parent=self.current_folder)
        else:
            self.filter = Q(parent=None)

    def fill_current_folder(self, new_col, new_row):
        lbl = XferCompLabelForm('title_folder')
        if self.current_folder > 0:
            folder_obj = FolderContainer.objects.get(id=self.current_folder)
            lbl.set_value(folder_obj.get_title())
            folder_description = folder_obj.description
        else:
            folder_obj = None
            lbl.set_value('>')
            folder_description = ""
        lbl.set_location(new_col, new_row)
        lbl.description = _("current folder:")
        self.add_component(lbl)

        lbl = XferCompLabelForm('desc_folder')
        lbl.set_value_as_header(folder_description)
        lbl.set_location(new_col, new_row + 1)
        self.add_component(lbl)

        if self.current_folder > 0:
            btn_return = XferCompButton('return')
            btn_return.set_location(new_col + 1, new_row)
            btn_return.set_is_mini(True)
            btn_return.set_action(self.request, self.get_action('', 'images/left.png'), params={'current_folder': self.item.parent_id if self.item.parent_id is not None else 0},
                                  modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            self.add_component(btn_return)

            btn_edit = XferCompButton('edit')
            btn_edit.set_location(new_col + 1, new_row + 1)
            btn_edit.set_is_mini(True)
            btn_edit.set_action(self.request, FolderAddModify.get_action('', 'images/edit.png'),
                                params={'folder': self.current_folder}, close=CLOSE_NO)
            self.add_component(btn_edit)
        return folder_obj

    def add_document(self):
        old_item = self.item
        self.model = DocumentContainer
        self.item = DocumentContainer()
        last_row = self.get_max_row() + 5
        lbl = XferCompLabelForm('sep1')
        lbl.set_location(0, last_row, 6)
        lbl.set_value("{[center]}{[hr/]}{[/center]}")
        self.add_component(lbl)
        lbl = XferCompLabelForm('sep2')
        lbl.set_location(0, last_row + 1, 2)
        lbl.set_value_as_infocenter(_("Add document"))
        self.add_component(lbl)

        self.fill_from_model(0, last_row + 3, False)
        self.remove_component('parent')

        btn_doc = XferCompButton('adddoc')
        btn_doc.set_location(1, last_row + 4)
        btn_doc.set_action(self.request, DocumentAddModify.get_action(TITLE_ADD, 'images/add.png'),
                           params={'parent': self.current_folder, 'SAVE': 'YES'}, close=CLOSE_NO)
        self.add_component(btn_doc)

        self.model = AbstractContainer
        self.item = old_item

    def fillresponse_body(self):
        containerorder = self.getparam('GRID_ORDER%container', ())
        self.params['GRID_ORDER%container'] = ','.join([item.replace('icon', 'foldercontainer__isnull') for item in containerorder])
        XferListEditor.fillresponse_body(self)
        grid = self.get_components('container')
        grid.get_header('icon').orderable = 1
        grid.order_list = list(set(containerorder))
        self.params['GRID_ORDER%container'] = ','.join(grid.order_list)
        if self.params['GRID_ORDER%container'] == '':
            del self.params['GRID_ORDER%container']

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        obj_doc = self.get_components('container')
        new_col = obj_doc.col
        new_row = obj_doc.row
        obj_doc.colspan = 2
        obj_doc.change_type_header('date_modif', 'datetime')
        self.move_components('container', 0, 2)
        self.fill_current_folder(new_col, new_row)

        if isinstance(self.item, DocumentContainer):
            btn_doc = XferCompButton('doc')
            btn_doc.set_location(new_col, new_row + 4)
            btn_doc.set_is_mini(True)
            btn_doc.set_action(self.request, DocumentShow.get_action('', ''),
                               params={'document': self.item.id}, close=CLOSE_NO)
            btn_doc.java_script = "current.actionPerformed();"
            self.add_component(btn_doc)
        elif folder_notreadonly_condition(self):
            self.add_document()


@MenuManage.describ('documents.change_document', FORMTYPE_NOMODAL, 'documents.actions', _('To find a document following a set of criteria.'))
class DocumentSearch(XferSavedCriteriaSearchEditor):
    caption = _("Document search")
    icon = "documentFind.png"
    model = DocumentContainer
    field_id = 'document'
    mode_select = SELECT_SINGLE
    select_class = None

    def get_text_search(self):
        criteria_desc = XferSavedCriteriaSearchEditor.get_text_search(self)
        if notfree_mode_connect() and not self.request.user.is_superuser:
            if self.filter is None:
                self.filter = Q()
            self.filter = self.filter & (Q(parent=None) | Q(parent__viewer__in=self.request.user.groups.all()))
        return criteria_desc

    def fillresponse(self):
        XferSearchEditor.fillresponse(self)
        if self.select_class is not None:
            grid = self.get_components(self.field_id)
            grid.add_action(self.request, self.select_class.get_action(_("Select"), "images/ok.png"),
                            close=CLOSE_YES, unique=self.mode_select, pos_act=0)


@ActionsManage.affect_show(_('delete shared link'), "images/permissions.png", condition=lambda xfer: xfer.item.sharekey is not None)
@ActionsManage.affect_show(_('create shared link'), "images/permissions.png", condition=lambda xfer: xfer.item.sharekey is None)
@MenuManage.describ('documents.add_document')
class DocumentChangeShared(XferContainerAcknowledge):
    icon = "document.png"
    model = DocumentContainer
    field_id = 'document'

    def fillresponse(self):
        self.item.change_sharekey(self.item.sharekey is not None)
        self.item.save()


@MenuManage.describ('')
class DownloadFile(XferContainerAcknowledge):
    icon = "document.png"
    model = DocumentContainer
    field_id = 'document'
    caption = _("Download document")

    def get_post(self, request, *args, **kwargs):
        from django.http.response import StreamingHttpResponse, HttpResponse
        getLogger("lucterios.documents.DownloadFile").debug(">> get %s [%s]", request.path, request.user)
        try:
            self._initialize(request, *args, **kwargs)
            shared = self.getparam('shared', '')
            filename = self.getparam('filename', '')
            try:
                doc = DocumentContainer.objects.get(name=filename, sharekey=shared)
                response = StreamingHttpResponse(doc.content, content_type='application/octet-stream')
                response['Content-Disposition'] = 'attachment; filename=%s' % doc.name
            except DocumentContainer.DoesNotExist:
                response = HttpResponse(_("File not found !"))
            return response
        finally:
            getLogger("lucterios.documents.DownloadFile").debug("<< get %s [%s]", request.path, request.user)


@signal_and_lock.Signal.decorate('summary')
def summary_documents(xfer):
    if not hasattr(xfer, 'add_component'):
        return WrapAction.is_permission(xfer, 'documents.change_document')
    elif WrapAction.is_permission(xfer.request, 'documents.change_document'):
        row = xfer.get_max_row() + 1
        lab = XferCompLabelForm('documenttitle')
        lab.set_value_as_infocenter(_('Document management'))
        lab.set_location(0, row, 4)
        xfer.add_component(lab)
        filter_result = Q()
        if notfree_mode_connect():
            filter_result = filter_result & (Q(parent=None) | Q(parent__viewer__in=xfer.request.user.groups.all() if xfer.request.user.id is not None else []))
        nb_doc = len(DocumentContainer.objects.filter(*[filter_result]))
        lbl_doc = XferCompLabelForm('lbl_nbdocument')
        lbl_doc.set_location(0, row + 1, 4)
        if nb_doc == 0:
            lbl_doc.set_value_center(_("no file currently available"))
        elif nb_doc == 1:
            lbl_doc.set_value_center(_("one file currently available"))
        else:
            lbl_doc.set_value_center(_("%d files currently available") % nb_doc)
        xfer.add_component(lbl_doc)
        lab = XferCompLabelForm('documentend')
        lab.set_value_center('{[hr/]}')
        lab.set_location(0, row + 2, 4)
        xfer.add_component(lab)
        return True
    else:
        return False


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_document(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("document_params", 55))
    elif (xfer is not None) and (wizard_ident == "document_params"):
        xfer.add_title(_("Lucterios documents"), _("Parameters"))
        lbl = XferCompLabelForm("nb_folder")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': FolderContainer._meta.verbose_name_plural, 'count': len(FolderContainer.objects.all())})
        xfer.add_component(lbl)
        lbl = XferCompLabelForm("nb_doc")
        lbl.set_location(1, xfer.get_max_row() + 1)
        lbl.set_value(TEXT_TOTAL_NUMBER % {'name': DocumentContainer._meta.verbose_name_plural, 'count': len(DocumentContainer.objects.all())})
        xfer.add_component(lbl)
        btn = XferCompButton("btnconf")
        btn.set_location(4, xfer.get_max_row() - 1, 1, 2)
        btn.set_action(xfer.request, FolderList.get_action(TITLE_MODIFY, "images/edit.png"), close=CLOSE_NO)
        xfer.add_component(btn)
