"""
Inspired by https://gist.github.com/uroshekic/11078820
who was himself inspired by 
http://code.activestate.com/recipes/578253-an-entry-with-autocompletion-for-the-tkinter-gui/
"""

from tkinter import Tk,Entry,StringVar,Listbox, Frame
from tkinter.constants import END, INSERT, ACTIVE
from tkinter import sys

class AutoEntry(Entry):
    def __init__(self, master, *args, **kwargs):
        # paramètres
        self._max       = kwargs.pop('max', 6)
        self._change    = kwargs.pop('change', None)
        self._command   = kwargs.pop('command', None)
        self._text      = kwargs.pop('textvariable')
        
        # réglage des couleurs de sélection pour la listbox
        if sys.platform == 'linux':
            self._highlight = { 'selectbackground':'medium blue',
                                'selectforeground':'white'}
        else:
            self._highlight = {}
        kwargs.update(self._highlight)
        
        # initialisation du champs de saisie
        super(AutoEntry,self).__init__(master,*args,
                                        textvariable=self._text,**kwargs)
        self.icursor(END)

        # la listbox de choix n'est pas visible
        self._listboxUp = False          
        
        # type de liste reçue : liste de tuples ou liste de valeurs
        if self._change and self._text.get():
            choices = self._change(self._text.get())
            if choices:
                if type(choices[0])!=tuple:
                    self._KV     = False
                    self._values = choices
                else:
                    self._KV = True
                    self._keys   = [str(t[1]) for t in choices]
                    self._values = [str(t[0]) for t in choices]
        else:
            choices = []
            self._KV = False
            
        # définition des callbacks
        # self._text.trace('w', self._on_change) 
        self.bind("<KeyRelease>", self._on_keyrelease)
        self.bind("<Right>", self.select)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)
        self.bind("<Escape>", self.hide)
        self.bind("<FocusOut>", self.focusout)
        # self.bind("<Control-Right>", self._show)
        self.bind_all("<Button-1>", self.click)
            
    def focusout(self, event):
        ''' disparition de la liste si le focus est perdu '''
        if self._listboxUp:
            self.hide(event)
        
    def click(self, event):
        ''' disparition de la liste si on clique à côté '''
        if self._listboxUp and event.widget!=self and event.widget!=self.listbox:
            self.hide(event)

    def mouse(self, event):
        ''' choix d'un item si on clique dans la liste '''
        if self.listbox.curselection():
            self.value = self.listbox.get(self.listbox.curselection()[0])
            self.icursor(END)
            self.hide(event)
        
    def select(self, event):
        ''' choix au clavier d'un item dans la liste '''
        if self._listboxUp:
            self.value = self.listbox.get(ACTIVE)
            self.icursor(END)
            self.hide(event)
        
    def hide(self, event):
        ''' disparition de la liste '''
        if self._listboxUp:
            self._listboxframe.destroy()
            self._listboxUp = False
                
    def _on_value(self):
        if self._command:
            if self._KV:
                self._command(self.key)
            else:
                self._command(self.value)
    
    def _show(self, event):
        self._on_keyrelease(event)
               
    def _on_keyrelease(self, event):
        ctrl = bool(event.state&0x0004)
        if (len(event.keysym)==1 
            or event.keysym=="Delete" or event.keysym=="BackSpace"
            or (event.keysym=="Right" and ctrl) ):
            if self.value == '':
                self.hide(event)
            elif self._change:
                choices = self._change(self._text.get())
                if choices:
                    if type(choices[0])!=tuple:
                        self._KV     = False
                        self._values = choices
                    else:
                        self._KV = True
                        self._keys   = [str(t[1]) for t in choices]
                        self._values = [str(t[0]) for t in choices]
    
                    if not self._listboxUp:        
                        self._listboxframe = Frame(self.winfo_toplevel())                   
                        self._listboxframe.place(in_=self, relx=0, rely=1)
                        self._listboxframe.lift()
                        self.listbox = Listbox(self._listboxframe, width=self["width"],
                                                height=self._max,
                                                **self._highlight)
                        self.listbox.pack()     
                        self.listbox.bind("<<ListboxSelect>>", self.mouse)
                        self._listboxUp = True
                    
                    self.listbox.delete(0, END)
                    for choice in self._values:
                        self.listbox.insert(END, choice)
                    self.listbox["height"] = min(len(choices), self._max)
                    self.goto(0)
                else:
                    self.hide(event)
                        
    def moveUp(self, event):
        if self._listboxUp:
            if self.index:                
                self.listbox.selection_clear(self.index)
                self.goto(self.index-1)

    def moveDown(self, event):
        if self._listboxUp:
            if self.index != self.listbox.size()-1:                        
                self.listbox.selection_clear(self.index)
                self.goto(self.index+1)
                
    def goto(self, index):
        self.index = index
        self.listbox.see(index)
        self.listbox.selection_set(index)
        self.listbox.activate(index)    
        
    @property
    def key(self):
        try:
            return self._keys[self._values.index(self.value)]
        except:
            return None 
            
    @key.setter
    def key(self, key):
        try:
            self.value = self._values[self._keys.index(key)]
        except:
            pass
        
    @property
    def value(self):
        return self._text.get()
        
    @value.setter
    def value(self, value):
        self._text.set( str(value) )
        self._on_value()
                          
    def update_command(self, command):
        self._command = command    
                              
    def update_change(self, change):
        self._change = change

# test code
if __name__ == '__main__':
    from tkinter import Frame
    
    def choicelist(pattern):
        return [w for w in autolist if pattern in w]
        
    def choicelistKV(pattern):
        return [autolistKV[i] for i in range(len(autolistKV))
                        if pattern in autolistKV[i][1]]
        
    with open('autolist.txt') as file:
        autolist = file.read()
    autolist   = autolist.split('\n')
    autolistKV = [(autolist[i],'key-'+str(i)) for i in range(len(autolist))]
    
    root = Tk()
    root.title = "AutoEntry"
    root.geometry("300x200")
    text = StringVar()
    textKV = StringVar()
    frame = Frame(root)
    entry = AutoEntry(frame, textvariable=text, 
                    change=choicelist, max=8, width=20)
    frame2 = Frame(root)
    entryKV = AutoEntry(frame2, textvariable=textKV, 
                    change=choicelistKV, max=8, width=20)
    entry.focus()
    entry.pack()
    entryKV.pack()
    frame.pack()    
    frame2.pack()
    root.mainloop()
