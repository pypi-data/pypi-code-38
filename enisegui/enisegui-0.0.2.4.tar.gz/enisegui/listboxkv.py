from guizero   import ListBox
from inspect   import getargspec as getfullargspec  # py3
import sys
        
class ListBoxKV(ListBox):
    def __init__(self, parent=None, **kwargs):
        # starting parameters
        items       = kwargs.pop('items', [])
        
        if not items or type(items[0])!=tuple:
            self._KV = False
            super(ListBoxKV,self).__init__(parent, 
                                items=[str(item) for item in items],
                                **kwargs)
        else:
            self._KV = True
            self._keys   = [str(t[1]) for t in items]
            self._values = [str(t[0]) for t in items]
            super(ListBoxKV,self).__init__(parent, items=self._values,
                                **kwargs)
        
        # selection color depending of platform
        if sys.platform == 'linux':
            self._highlight = { 'selectbackground':'medium blue',
                                'selectforeground':'white'}
        else:
            self._highlight = {}
        self._listbox.tk.config(**self._highlight)
                                
        # hack to update callback on "<<ListboxSelect>>" event
        self._listbox.events.remove_event("<ListBox.ListboxSelect>")
        self._listbox.events.set_event("<ListBox.ListboxSelect>", 
                            "<<ListboxSelect>>", self._command_callback)
        
    # Gets the number of args a function expects
    def _no_args_expected(self, func_name):
        args = getfullargspec(func_name).args
        if len(args) > 0:
            # if someone names the first arg of a class function to something
            # other than self, this will fail! or if they name the first argument
            # of a non class function to self this will fail!
            if args[0] == "self":
                return len(args) - 1
            else:
                return len(args)
        else:
            return 0
    
    def _command_callback(self):
        if self._KV:
            value = self.key
        else:
            value = self.value
        if self._listbox._command:
            args_expected = self._no_args_expected(self._listbox._command)
            if args_expected == 0:
                self._listbox._command()
            elif args_expected == 1:
                self._listbox._command(value)
            else:
                print(""""ListBox command function must accept either 0 or 1 arguments.\n
                The current command has {} arguments.""".format(args_expected))
                
    @property
    def key(self):
        if self._listbox._multiselect:
            return [self._keys[self._values.index(val)] for val in self.value]
        else:
            return self._keys[self._values.index(self.value)]

    @key.setter
    def key(self, key):
        try:
            if self._listbox._multiselect:
                self.value = [self._values[self._keys.index(k)] for k in key]
            else:
                self.value = self._values[self._keys.index(key)]
        except:
            pass
    
    def selectkey(self, key):
        ''' sets key and calls command '''
        try:
            if self._listbox._multiselect:
                self.value = [self._values[self._keys.index(k)] for k in key]
            else:
                self.value = self._values[self._keys.index(key)]
            self._command_callback()
        except:
            try:
                self.value = self._values[0]
                self._command_callback()
            except:
                pass
            
    def selectvalue(self, value):
        ''' sets value and calls command '''
        self.value = value
        self._command_callback()
        
    def append(self, item):
        if self._KV:
            self._keys.append(str(item[1]))
            self._values.append(str(item[0]))
            super(ListBoxKV,self).append(str(item[0]))
        else:
            super(ListBoxKV,self).append(str(item))
          
    def insert(self, index, item):
        if self._KV:
            self._keys.insert(index, str(item[1]))
            self._values.insert(index, str(item[0]))
            super(ListBoxKV,self).insert(index, str(item[0]))
        else:
            super(ListBoxKV,self).insert(index, str(item))
        
    def remove(self, item):
        if self._KV:
            self._keys.remove(str(item[1]))
            self._values.remove(str(item[0]))
            super(ListBoxKV,self).remove(str(item[0]))
        else:
            super(ListBoxKV,self).remove(str(item))

    def clear(self):
        if self._KV:
            self._keys = []
            self._values = []
        super(ListBoxKV,self).clear()

    @property
    def items(self):
        """ Returns a list of items in the ListBox """
        return self._listbox.items
    
    @items.setter
    def items(self, items):
        self.clear()
        for i in range(len(items)):
            self.insert(i,items[i])
        
# test code
if __name__ == '__main__':
    from guizero import App,Box,Text,PushButton,TextBox
    
    # ListBoxKV
    def listbox_get(key):
        listbox_label.value  = key
        listbox2.value = key
        
    def listbox_set(value):
        listbox.key = value
    
    app = App(height=100)
    box    = Box(app,width='fill')
    Box(box, height='fill', width=4, align='left')
    autotext = Text(box, text='ListBoxKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    listbox  = ListBoxKV(box, align='left', width=100, height=60,
                        items=[('Green', 12),('Yellow', 25),('Blue', 5)], 
                        command=listbox_get)
    Text(box, align='left', text=' Key get ')
    listbox_label  = Text(box, align='left', text='--', width=2, bg='green', color='white')
    Text(box, align='left', text=' Key set ')    
    listbox2 = ListBoxKV(box, align='left', width=100, height=60,
                    items=[12, 25, 5], command=listbox_set)
    
    app.display()
    