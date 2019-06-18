from tkinter import *
from guizero import Box
from PIL import Image
from PIL import ImageTk
import pkg_resources 

import random

''' source AutoScrollbar : http://effbot.org/zone/tkinter-autoscrollbar.htm '''
class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
        
class Table(Box):
    def __init__(self, parent=None, **kwargs):
        # startup parameters
        self._data       = kwargs.pop('data',[()])
        self._command    = kwargs.pop('command',None)
        self._rowid      = kwargs.pop('rowid',False)
        self._justify    = kwargs.pop('justify','w')
        text_size        = kwargs.pop('text_size',12)
        font             = kwargs.pop('font','TkDefaultFont')
        color            = kwargs.pop('color','grey20')
        
        curdir           = pkg_resources.resource_filename('enisegui','.')
        self._edit       = self._icon(curdir+'/edit.png')
        self._new        = self._icon(curdir+'/new.png')
        self._label_padx = 5
        self._label_pady = 3
        Box.__init__(self, parent, **kwargs)
        self._text_size  = text_size
        self._font       = font
        self._color      = color
        self._bgcolor    = {0:'grey91',1:'grey95'}
        self._hbgcolor     = 'grey80'
        self._hcolor     = color
        self._draw()
        self.set_border(1, 'grey80')
    
    def _icon(self, filename):
        img  = Image.open(filename)
        img  = img.resize((18,18),Image.LANCZOS)
        return ImageTk.PhotoImage(img)
            
    def _draw(self):
        try:
            self._frame.destroy()
        except:
            pass      
        rootframe  = Frame(self.tk)
        self._frame = rootframe
        rootframe.grid_rowconfigure(0, weight=1)
        rootframe.grid_columnconfigure(0, weight=1)
        canvas = Canvas(rootframe, highlightthickness=0)
        self._canvas = canvas
        hbar = AutoScrollbar(rootframe, orient='horizontal', 
                                    command=canvas.xview)
        vbar = AutoScrollbar(rootframe, orient='vertical', 
                                    command=canvas.yview)
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        hbar.grid(row=1, column=0, sticky='ew')
        vbar.grid(row=0, column=1, sticky='ns')
        canvas.grid(column=0,row=0)
        # binding de la molette de la souris
        canvas.bind_all("<Button-4>", self._on_mousewheel_up)
        canvas.bind_all("<Button-5>", self._on_mousewheel_down)
        self._table_draw()
        rootframe.pack()
        
    def _on_mousewheel_up(self, event):
        if event.widget.master==self._table:
            shift = event.state & 0x1
            if shift:
                # horizontal
                self._canvas.xview_scroll(-5, "units")
            else:
                # vertical
                self._canvas.yview_scroll(-5, "units")
        
    def _on_mousewheel_down(self, event):
        if event.widget.master==self._table:
            shift = event.state & 0x1
            if shift:
                # horizontal
                self._canvas.xview_scroll(5, "units")
            else:
                # vertical
                self._canvas.yview_scroll(5, "units")
    
    def _table_draw(self):  
        self._type    = type(self._data[0]).__name__ # 'list' or 'dict'
        self._cells   = []
        self._rowids  = []
        try:
            self._canvas.delete('all')
            self._table.destroy()
        except:
            pass
        canvas = self._canvas
        frame  = Frame(canvas)
        self._table = frame
        self._type  = type(self._data[0]).__name__ # 'list' or 'dict'
        self._headers()
        self._content()
        canvas.create_window(0, 0, window=frame, anchor='nw')
        canvas.update()
        canvas.config(width=frame.winfo_width(), height=frame.winfo_height())
        canvas.config(scrollregion=canvas.bbox('all'))
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)
        
    def _headers(self):
        # en-têtes
        if self._type=='dict': # liste de dictionnaires
            head = self._data[0].keys()
            col  = len(head)
            c = 0
            for k in head:
                if k!='rowid':
                    if type(self.justify)==str:
                        anchor = self.justify
                    else:
                        anchor = self.justify[c]
                    cell = Label(self._table, text=k.capitalize(), anchor=anchor,
                                    bg=self._hbgcolor, fg=self._hcolor,
                                    font=(self._font, self._text_size, 'bold'),
                                    padx=self._label_padx, 
                                    pady=self._label_pady, borderwidth=1,
                                    relief="sunken")
                    cell.grid(row=0, column=c, sticky="wens")
                    c += 1
            if self._command and self._data[0]:
                btn = Button(self._table, image=self._new, 
                                bg=self._hbgcolor, fg=self._hcolor,
                                command=lambda num=None: self._command(num),
                                padx=self._label_padx, 
                                pady=self._label_pady, relief="ridge")
                btn.grid(row=0, column=c, sticky="wens")
        else: # liste de tuples
            head = self._data[0]
            col  = len(head)
            if self._rowid: # la première colonne est le rowid
                start = 1
            else:
                start = 0
            for c in range(start,col):
                if type(self.justify)==str:
                    anchor = self.justify
                else:
                    anchor = self.justify[c-start]
                cell = Label(self._table, text=head[c].capitalize(), anchor=anchor,
                                bg=self._hbgcolor, fg=self._hcolor,
                                font=(self._font, self._text_size, 'bold'),
                                padx=self._label_padx, 
                                pady=self._label_pady, borderwidth=1,
                                relief="sunken")
                cell.grid(row=0, column=c-start, sticky="wens")
            if self._command and self._data[0]:
                btn = Button(self._table, image=self._new, 
                                bg=self._hbgcolor, fg=self._hcolor,
                                command=lambda num=None: self._command(num),
                                padx=self._label_padx, 
                                pady=self._label_pady, relief="ridge")
                btn.grid(row=0, column=c+1, sticky="wens")
            
    def _content(self):
        # contenu de la table
        if self._type=='dict': # liste de dictionnaires
            data = self._data
            for r in range(len(data)):
                c = 0
                for k in data[r]:
                    if k=='rowid':
                        self._rowids.append(data[r][k])
                    else:
                        if type(self.justify)==str:
                            anchor = self.justify
                        else:
                            anchor = self.justify[c]
                        cell  = Label(self._table, text=data[r][k], 
                                        anchor=anchor, bg=self._bgcolor[r%2], 
                                        fg=self._color,
                                        font=(self._font, self._text_size),
                                        padx=self._label_padx, 
                                        pady=self._label_pady, borderwidth=2, 
                                        relief="sunken")
                        cell.grid(row=r+1, column=c, sticky="wens")                    
                        self._cells.append(cell)
                        c += 1
                if self._command and data[r]:
                    if len(self._rowids)>0:
                        send = self._rowids[r]
                    else:
                        send = r
                    btn = Button(self._table, image=self._edit, 
                                    bg=self._bgcolor[r%2],
                                    command=lambda num=send: self._command(num),
                                    fg='black',padx=2, pady=2, relief="ridge")
                    btn.grid(row=r+1, column=c, sticky="wens")
                    
        else: # liste de tuples
            data = self._data
            if self._rowid: # la première colonne est le rowid
                start = 1
            else:
                start = 0
            for r in range(1,len(data)):
                for c in range(start,len(data[r])):
                    if type(self.justify)==str:
                        anchor = self.justify
                    else:
                        anchor = self.justify[c-start]
                    cell  = Label(self._table, text=data[r][c], 
                                    anchor=anchor, bg=self._bgcolor[r%2], 
                                    fg=self._color,
                                    font=(self._font, self._text_size),
                                    padx=self._label_padx, 
                                    pady=self._label_pady, borderwidth=2, 
                                    relief="sunken")
                    cell.grid(row=r+1, column=c-start, sticky="wens")                    
                    self._cells.append(cell)
                if self._command and data[r]:
                    if self._rowid:
                        send = data[r][0]
                    else:
                        send = r
                    btn = Button(self._table, image=self._edit, 
                                    bg=self._bgcolor[r%2],
                                    command=lambda num=send: self._command(num),
                                    fg='black',padx=2, pady=2, relief="ridge")
                    btn.grid(row=r+1, column=c+1, sticky="wens")
 
    def update_command(self, command):
        self._command = command
        self._table_draw()
                
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data
        self._table_draw()
                
    @property
    def rowid(self):
        return self._rowid
    
    @rowid.setter
    def rowid(self, rowid):
        self._rowid = rowid
        self._table_draw() 
                       
    @property
    def justify(self):
        return self._justify
    
    @justify.setter
    def justify(self, justify):
        self._justify = justify
        self._table_draw()
        
        
# test code
if __name__ == '__main__':
    from guizero import App,Box,Text,ButtonGroup
    app = App()
    
    # tables
    data1 = [                               # liste de tuples
        ('id','name','price'),
        (251,'Orange',12.5),
        (6852,'Potatoe',1220),
        (31,'Fruit',858.5)
    ]
    
    data2 = [                 # liste de dictionnaires sans rowid
        {'id':75,'name':'Kiwi','price':3.5,'family':'fruit'},
        {'id':542,'name':'Tomatoe','price':7.50,'family':'vegetable'},
        {'id':12,'name':'Fuji','price':4.0,'family':'apple'}
    ]        
    
    data3 = [                 # liste de dictionnaires avec rowid
        {'rowid':75,'name':'Kiwi','price':3.5,'family':'fruit'},
        {'rowid':542,'name':'Tomatoe','price':7.50,'family':'vegetable'},
        {'rowid':12,'name':'Fuji','price':4.0,'family':'apple'}
    ]      
    
    def to_rowid(list):
        for i in range(len(list)):
            dict = list[i]
            if 'id' in dict:
                rowid = dict['id']
                del dict['id']
                dict['rowid'] = rowid
        return list
            
    def to_id(list):
        for i in range(len(list)):
            dict = list[i]
            if 'rowid' in dict:
                id = dict['rowid']
                del dict['rowid']
                dict['id'] = id
        return list
    
    # callbacks
    def table_action(num):
        label.value = str(num)
        
    def table_fill():
        command = {"1":None,  "2":table_action}
        rowid   = {"1":False, "2":True}
        if choose_data.value=="1":
            data = data1
        elif (choose_data.value, choose_rowid.value)==("2","1"):
            data = to_id(data2)
        elif (choose_data.value, choose_rowid.value)==("2","2"):
            data = to_rowid(data2)
        table.rowid = rowid[choose_rowid.value]
        table.data  = data
        table.update_command(command[choose_command.value])
        label.value   = "--"
    # panneau de contrôle
    panneau        = Box(app, width='fill')
    topbox         = Box(panneau, width='fill')
    tabletext = Text(topbox, text='Table', align='left')
    tabletext.tk.config(font='Helvetica 12 bold')
    mainbox        = Box(panneau, width='fill')
    choose_data    = ButtonGroup(mainbox, 
                            options=[["tuples", "1"],["dicts", "2"]],
                            selected="1", 
                            command=table_fill, align='left')
    choose_rowid   = ButtonGroup(mainbox, 
                            options=[["no rowid", "1"],["rowid", "2"]],
                            selected="2", 
                            command=table_fill, align='left')
    choose_command = ButtonGroup(mainbox, 
                            options=[["no command", "1"],["command", "2"]],
                            selected="1", 
                            command=table_fill, align='left')
    Text(mainbox, text='Line # : ', align='left')
    label  = Text(mainbox, text='--', bg='green', color='white', align='left')
    
    # zone d'affichage pour la table
    affichage   = Box(app, width='fill')
    topbox      = Box(affichage, width='fill', height=10)
    mainbox     = Box(affichage, width='fill')
    Box(mainbox, align='left', height='fill', width=10)
    table       = Table(mainbox, data=data1, align='left', rowid=True)
    
    app.display() 
