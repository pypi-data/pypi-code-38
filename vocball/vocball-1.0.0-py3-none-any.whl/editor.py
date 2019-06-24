#!/usr/bin/env python3
#
# This file is part of Vocabulary Football (VocBall).
#
# Copyright (C) 2017-2019 - Thomas Dähnrich <develop@tdaehnrich.de>
#
# VocBall is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# VocBall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VocBall. If not, see <http://www.gnu.org/licenses/>.

import gi
import os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from copy import deepcopy
from settings import _


# define global variables

units = []
voc_file_path = ''
voc_unit = ["" for i in range(100)]
voc_unit_orig = ["" for i in range(100)]


# main functions of editor

def open_existing_vocabulary_list(self):

    from list import load_vocabulary_list, get_vocabulary, get_vocabulary_error
    global units, voc_file_path, voc_unit, voc_unit_orig

    file_accessible = False
    dialog = load_vocabulary_list(self.winEditor)

    response = dialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        voc_file_path = dialog.get_filename()
        secondary_text, voc_unit = get_vocabulary(self.listEditorUnits, voc_file_path)
        if secondary_text:
            get_vocabulary_error(voc_file_path, self.winEditor, secondary_text)
            reset_editor(self)
        else:
            file_accessible = True
    dialog.destroy()

    if file_accessible:
        path, file = os.path.split(voc_file_path)
        self.lblEditorFileName.set_text(file)
        self.treeEditorUnits.set_cursor(Gtk.TreePath(0), self.treecolEditorUnits, False)
        treeiter, unit_selected = get_selected_editor_unit(self)
        update_editor_values(self, unit_selected)

        units = []
        for i in range(len(self.listEditorUnits)):
            units.append(self.listEditorUnits[i][2])
        voc_unit_orig = deepcopy(voc_unit)

        if len(self.listEditorUnits) > 98:
            self.btnEditorUnitAdd.set_sensitive(False)
            self.btnEditorUnitRemove.set_sensitive(True)
        else:
            self.btnEditorUnitAdd.set_sensitive(True)
            self.btnEditorUnitRemove.set_sensitive(True)


def check_vocabulary_list_changed(self):

    voc_changed = False
    if voc_unit != voc_unit_orig:
        voc_changed = True
    return voc_changed


def save_new_vocabulary_list(self):

    from settings import default_folder
    global voc_file_path

    if voc_file_path:
        voc_file_path_backup = voc_file_path
    else:
        voc_file_path_backup = ''

    dialog = Gtk.FileChooserDialog(_("Save Vocabulary List"),
        self.winEditor, Gtk.FileChooserAction.SAVE,
        (_("Cancel"), Gtk.ResponseType.CANCEL, _("Save"), Gtk.ResponseType.ACCEPT))
    dialog.set_current_folder(default_folder)
    dialog.set_do_overwrite_confirmation(True)
    filter_csv = Gtk.FileFilter()
    filter_csv.set_name('CSV')
    filter_csv.add_mime_type('text/csv')
    filter_csv.add_pattern('*.[Cc][Ss][Vv]')
    dialog.add_filter(filter_csv)

    response = dialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        voc_file_path = dialog.get_filename()
        if not voc_file_path[-4:].lower() == '.csv':
            voc_file_path = voc_file_path + '.csv'
        message_text = write_vocabulary(self, voc_file_path)
        if message_text:
            if voc_file_path_backup:
                voc_file_path = voc_file_path_backup
            else:
                voc_file_path = ''
            error_dialog = Gtk.MessageDialog(self.winEditor, 0,
                Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message_text)
            error_dialog.run()
            error_dialog.destroy()
        else:
            path, file = os.path.split(voc_file_path)
            self.lblEditorFileName.set_text(file)
    dialog.destroy()


def write_vocabulary(self, voc_file_path):

    global voc_unit_orig

    message_text = ""

    try:
        voc_file = open(voc_file_path + '~', 'w')
    except (OSError, PermissionError):
        message_text = _("Could not save vocabulary list: No write permissions.")
        return message_text

    line = ""
    for i in range(1, 100):
        if voc_unit[i]:
            for n in range(len(voc_unit[i])):
                line = str(i) + "," + voc_unit[i][n] + "\n"
                voc_file.write(line)
    voc_file.close()

    if not line:
        message_text = _("Could not save vocabulary list: List is empty.")
        os.remove(voc_file_path + '~')
    else:
        voc_unit_orig = deepcopy(voc_unit)
        os.replace(voc_file_path + '~', voc_file_path)

    return message_text


def get_selected_editor_unit(self):

    global unit_selected

    model, treeiter = self.treeEditorUnits.get_selection().get_selected()
    unit_selected = model[treeiter][2]
    return treeiter, unit_selected


def add_editor_unit(self, unit_number):

    global units

    units.append(unit_number)
    units.sort()
    position = units.index(unit_number)
    treeiter = self.listEditorUnits.insert(position)
    unit_label = _("Unit {}").format(unit_number)
    self.listEditorUnits.set(treeiter, 0, False, 1, unit_label, 2, unit_number)
    self.treeEditorUnits.set_cursor(Gtk.TreePath(position), self.treecolEditorUnits, False)


def update_editor_values(self, unit_number):

    buffer = Gtk.TextBuffer.new()
    try:
        text = "\n".join(voc_unit[unit_number])
    except TypeError:
        text = ""
    buffer.set_text(text)
    self.textEditorVocabulary.set_buffer(buffer)
    self.spnbtnEditorUnitNumber.set_text(str(unit_number))


def reset_editor(self):

    global units, voc_file_path, voc_unit, voc_unit_orig

    self.listEditorUnits.clear()
    unit_label = _("Unit {}").format(1)
    self.listEditorUnits.append((False, unit_label, 1))
    units = [1]
    for n in range(1,100):
        voc_unit[n] = []
    voc_unit_orig = deepcopy(voc_unit)

    self.treeEditorUnits.set_cursor(Gtk.TreePath(0), self.treecolEditorUnits, False)
    get_selected_editor_unit(self)
    self.textEditorVocabulary.set_buffer(Gtk.TextBuffer.new())
    self.btnEditorUnitRemove.set_sensitive(False)
    self.spnbtnEditorUnitNumber.set_text("1")
    self.lblEditorFileName.set_text(_("Untitled List"))
    voc_file_path = ''


# initialize editor window and manage widgets

class Editor(Gtk.Window):

    def __init__(self, winGame):

        from settings import UI_DIR

        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(UI_DIR, 'editor.ui'))
        self.builder.connect_signals(self)

        for obj in self.builder.get_objects():
            if issubclass(type(obj), Gtk.Buildable):
                name = Gtk.Buildable.get_name(obj)
                setattr(self, name, obj)

        self.winEditor.set_transient_for(winGame)
        self.winEditor.show()


    def on_winEditor_show(self, widget):

        reset_editor(self)


    def on_btnEditorOpen_clicked(self, widget):

        voc_changed = check_vocabulary_list_changed(self)

        if voc_changed:
            self.dlgEditor.set_markup(_("Do you want to save the current vocabulary list before opening a new one?"))
            self.btnDialogEditorNoSave.set_image(self.imgOpenDialog)
            self.btnDialogEditorNoSave.set_label(_("Open"))
            self.dlgEditor.show()
        else:
            open_existing_vocabulary_list(self)


    def on_btnEditorNew_clicked(self, widget):

        voc_changed = check_vocabulary_list_changed(self)

        if voc_changed:
            self.dlgEditor.set_markup(_("Do you want to save the current vocabulary list before creating a new one?"))
            self.btnDialogEditorNoSave.set_image(self.imgNewDialog)
            self.btnDialogEditorNoSave.set_label(_("New"))
            self.dlgEditor.show()
        else:
            reset_editor(self)


    def on_btnEditorSaveAs_clicked(self, widget):

        save_new_vocabulary_list(self)


    def on_btnEditorSave_clicked(self, widget):

        if voc_file_path == '':
            save_new_vocabulary_list(self)
        else:
            message_text = write_vocabulary(self, voc_file_path)
            if message_text:
                error_dialog = Gtk.MessageDialog(self.winEditor, 0,
                    Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message_text)
                error_dialog.run()
                error_dialog.destroy()


    def on_spnbtnEditorUnitNumber_changed(self, widget):

        if widget.get_text():
            unit_number = int(widget.get_text())
            treeiter, unit_selected = get_selected_editor_unit(self)
            if unit_number == unit_selected or unit_number == 0:
                icon_name = ""
                icon_activate = False
                icon_tooltip = ""
            else:
                if unit_number in units:
                    icon_name = "gtk-dialog-error"
                    icon_activate = False
                    icon_tooltip = _("Unit already exists")
                else:
                    icon_name = "gtk-edit"
                    icon_activate = True
                    icon_tooltip = _("Rename unit")
        else:
            icon_name = ""
            icon_activate = False
            icon_tooltip = ""

        icon_position = Gtk.EntryIconPosition.PRIMARY
        widget.set_icon_from_icon_name(icon_position, icon_name)
        widget.set_icon_activatable(icon_position, icon_activate)
        widget.set_icon_tooltip_text(icon_position, icon_tooltip)


    def on_spnbtnEditorUnitNumber_icon_press(self, widget, GTK_ENTRY_ICON_PRIMARY, event):

        global units, voc_unit

        treeiter, unit_selected = get_selected_editor_unit(self)

        self.listEditorUnits.remove(treeiter)
        units.remove(unit_selected)
        voc_backup = voc_unit[unit_selected]
        voc_unit[unit_selected] = []

        unit_number = int(widget.get_text())
        voc_unit[unit_number] = voc_backup
        add_editor_unit(self, unit_number)
        update_editor_values(self, unit_number)

        icon_position = Gtk.EntryIconPosition.PRIMARY
        widget.set_icon_from_icon_name(icon_position, "")
        widget.set_icon_activatable(icon_position, False)
        widget.set_icon_tooltip_text(icon_position, "")


    def on_btnEditorUnitAdd_clicked(self, widget):

        global units

        position_found = False
        for unit_number in range(unit_selected+1, 100):
            if not unit_number in units:
                position_found = True
                break
        if not position_found:
            for unit_number in range(unit_selected-1, 0, -1):
                if not unit_number in units:
                    break

        add_editor_unit(self, unit_number)
        update_editor_values(self, unit_number)

        if len(self.listEditorUnits) > 98:
            widget.set_sensitive(False)
        else:
            self.btnEditorUnitRemove.set_sensitive(True)


    def on_btnEditorUnitRemove_clicked(self, widget):

        global units, voc_unit

        treeiter, unit_selected = get_selected_editor_unit(self)

        message_text = _("Do you want to delete unit {}?").format(unit_selected)
        dialog = Gtk.MessageDialog(self.winEditor, 0,
            Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message_text)

        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.listEditorUnits.remove(treeiter)
            units.remove(unit_selected)
            voc_unit[unit_selected] = []
        dialog.destroy()

        treeiter, unit_selected = get_selected_editor_unit(self)
        update_editor_values(self, unit_selected)

        if len(self.listEditorUnits) == 1:
            widget.set_sensitive(False)
        else:
            self.btnEditorUnitAdd.set_sensitive(True)


    def on_treeEditorUnits_row_activated(self, widget, path, column):

        treeiter, unit_selected = get_selected_editor_unit(self)
        update_editor_values(self, unit_selected)


    def on_textEditorVocabulary_focus_out_event(self, widget, event):

        global voc_unit

        buffer = widget.get_buffer()
        buffer_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        text = buffer_text.replace(",","").replace(";","").split("\n")
        voc_unit[unit_selected] = list(filter(None, text))


    def on_btnDialogEditorCancel_clicked(self, widget):

        self.dlgEditor.hide()


    def on_btnDialogEditorNoSave_clicked(self, widget):

        self.dlgEditor.hide()
        if widget.get_label() == _("Close"):
            self.winEditor.hide()
        if widget.get_label() == _("New"):
            reset_editor(self)
        if widget.get_label() == _("Open"):
            open_existing_vocabulary_list(self)


    def on_btnDialogEditorSave_clicked(self, widget):

        if voc_file_path == '':
            save_new_vocabulary_list(self)
            if voc_file_path != '':
                self.dlgEditor.hide()
        else:
            message_text = write_vocabulary(self, voc_file_path)
            if message_text:
                error_dialog = Gtk.MessageDialog(self.winEditor, 0,
                    Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message_text)
                error_dialog.run()
                error_dialog.destroy()
            else:
                self.dlgEditor.hide()
                if self.btnDialogEditorNoSave.get_label() == _("Close"):
                    self.winEditor.hide()


    def on_winEditor_delete_event(self, widget, event):

        self.on_textEditorVocabulary_focus_out_event(self.textEditorVocabulary, None)
        voc_changed = check_vocabulary_list_changed(self)

        if voc_changed:
            self.dlgEditor.set_markup(_("Do you want to save the current vocabulary list before closing?"))
            self.btnDialogEditorNoSave.set_image(self.imgCloseDialog)
            self.btnDialogEditorNoSave.set_label(_("Close"))
            self.dlgEditor.show()
        else:
            self.winEditor.hide()

        return True
