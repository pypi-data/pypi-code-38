'''
This file is part of the EdTech library project at Full Sail University.

    Foobar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

    Copyright © 2015 Full Sail University.
'''

import ttk

from Tkinter import *
from itertools import repeat

# http://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
def TkCenter(win):
    """
    centers a tkinter window
    :param win: the root or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def TextGet(text): return text.get("1.0", "end")
def TextSet(text, str):
    text.delete("1.0", "end")
    text.insert("1.0", str)
def TextAdd(text, str): text.insert("end", str)

class TkModeless(object):
    """A popup."""
    def __init__(self, root, title, message):
        self.window = Toplevel(root)
        self.window.title(title)
        lbl = ttk.Label(self.window, text = message)
        lbl.update_idletasks()
        lbl.pack()
        TkCenter(self.window)
        self.window.state("normal")
        self.window.update_idletasks()

    def Close(self): self.window.destroy()

# http://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-grid-of-widgets-in-tkinter
class FrameWithScrollbar(object):
    """A Frame with attached Scrollbar."""
    def __init__(self, root, width, height):
        self.root = root

        self.canvas = Canvas(self.root, borderwidth = 0, width = width, height = height)
        self.frame = ttk.Frame(self.canvas)

    def AddScrollbar(self):
        vsb = ttk.Scrollbar(self.root, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = vsb.set)
        self.frame.pack()
        self.canvas.create_window((0, 0), window = self.frame, anchor = "nw")
        vsb.pack(side = "right", fill = "y")
        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.frame.bind("<Configure>", lambda event, canvas = self.canvas: self.canvas.configure(scrollregion = self.canvas.bbox("all")))

class Table(object):
    """A matrix of (editable) strings."""
    def __init__(self, root, width, height, col, row, columnspan, headers = None):
        self.headers = headers
        self.rows = row

        self.stringVars = []
        self.entries = []

        canvas = Canvas(root, relief = GROOVE, borderwidth = 2, width = width, height = height)
        self.frame = ttk.Frame(canvas)
        self.frame.bind("<Configure>", lambda event, canvas = canvas: canvas.configure(scrollregion = canvas.bbox("all")))
        if self.headers != None: self.Add([self.headers], True)

        canvas.create_window((0, 0), window = self.frame, anchor = "nw")
        canvas.grid(column = col, row = row, columnspan = columnspan)
        HSB = ttk.Scrollbar(root, orient = "horizontal", command = canvas.xview)
        VSB = ttk.Scrollbar(root, orient = "vertical", command = canvas.yview)
        canvas.configure(xscrollcommand = HSB.set, yscrollcommand = VSB.set)
        VSB.grid(column = col + columnspan, row = row, sticky = "ns")
        row += 1
        HSB.grid(column = col, row = row, columnspan = columnspan, sticky = "ew")
        row += 1

        self.rows = row - self.rows

    def Reset(self):
        num = len(self.stringVars)
        if self.headers != None: num -= 1
        for i in range(num):
            self.stringVars.pop()
            for e in self.entries.pop(): e.destroy()

    def Add(self, rows, readonly = False):
        row = len(self.stringVars)
        for r in rows:
            stringVars = []
            entries = []
            col = 0
            for c in r:
                sv = StringVar(value = c)
                stringVars.append(sv)
                e = ttk.Entry(self.frame, textvariable = sv, font = ("Consolas"))
                if readonly: e.config(state = "readonly")
                e.grid(row = row, column = col)
                entries.append(e)
                col += 1
            row += 1
            self.stringVars.append(stringVars)
            self.entries.append(entries)
        self.ResizeColumns()

    def Rows(self): return self.rows

    def ResizeColumns(self):
        if len(self.stringVars) == 0 or len(self.stringVars[0]) == 0: return

        widths = list(repeat(0, len(self.stringVars[0])))
        for row in self.stringVars:
            for col in range(len(row)):
                widths[col] = max(widths[col], len(row[col].get()))

        for row in self.entries:
            for i in range(len(row)):
                row[i].config(width = widths[i])

    def GetStrings(self):
        rows = []
        for row in self.stringVars:
            cols = []
            for col in row: cols.append(col.get())
            rows.append(cols)
        return rows
