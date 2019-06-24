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

from settings import _


# main functions for loading vocabulary list
# shared by options popover and editor window

def load_vocabulary_list(parent_window):

    from settings import default_folder

    dialog = Gtk.FileChooserDialog(_("Load Vocabulary List"),
        parent_window, Gtk.FileChooserAction.OPEN,
        (_("Cancel"), Gtk.ResponseType.CANCEL, _("Open"), Gtk.ResponseType.ACCEPT))
    dialog.set_current_folder(default_folder)
    filter_csv = Gtk.FileFilter()
    filter_csv.set_name('CSV')
    filter_csv.add_mime_type('text/csv')
    filter_csv.add_pattern('*.[Cc][Ss][Vv]')
    filter_txt = Gtk.FileFilter()
    filter_txt.set_name('Text')
    filter_txt.add_mime_type('text/plain')
    filter_txt.add_pattern('*.[Tt][Xx][Tt]')
    dialog.add_filter(filter_csv)
    dialog.add_filter(filter_txt)

    return dialog


def get_vocabulary(list_store, voc_file_path):

    voc_all = []
    voc_unit = ["" for n in range(100)]
    for n in range(1,100):
        voc_unit[n] = []
    list_store.clear()

    try:
        voc_file = open(voc_file_path)
    except IOError:
        secondary_text = _("The file could not be opened.")
        return secondary_text, voc_unit

    voc_rows = voc_file.read().split("\n")
    voc_file.close()

    for i in range(len(voc_rows)-1):
        voc_columns = voc_rows[i].replace(";",",").replace("\t",",").split(",")
        try:
            if voc_columns[0] and voc_columns[1]:
                voc_all.append(voc_columns)
        except IndexError:
            pass
    if not voc_all:
        secondary_text = _("The data has to be separated by comma, semicolon or tab.")
        return secondary_text, voc_unit

    for i in range(len(voc_all)):
        for n in range(1,100):
            try:
                if n == int(voc_all[i][0]):
                    voc_unit[n].append(voc_all[i][1])
            except ValueError:
                pass

    for n in range(1,100):
        if voc_unit[n]:
            unit_label = _("Unit {}").format(str(n))
            unit_data = (False, unit_label, n)
            list_store.append(unit_data)

    if len(list_store) == 0:
        secondary_text = _("The data structure has to be: [unit],[vocable].")
        return secondary_text, voc_unit

    secondary_text = ""
    return secondary_text, voc_unit


def get_vocabulary_error(voc_file_path, parent_window, secondary_text):

    path, file = os.path.split(voc_file_path)
    message_text = _("Vocabulary list '{}' could not be loaded!").format(file)
    error_dialog = Gtk.MessageDialog(parent_window, 0,
        Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, message_text)
    error_dialog.format_secondary_text(secondary_text)
    error_dialog.run()
    error_dialog.destroy()
