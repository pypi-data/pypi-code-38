from guizero   import Combo
from inspect   import getargspec as getfullargspec  # py3
        
class ComboKV(Combo):
    def __init__(self, parent=None, **kwargs):
        # starting parameters
        self._options   = kwargs.pop('options', [])
        
        if not self._options or type(self._options[0])!=tuple:
            self._KV = False
            super(ComboKV,self).__init__(parent, options=self._options,
                                **kwargs)
        else:
            self._KV = True
            self._keys   = [str(t[1]) for t in self._options]
            self._values = [str(t[0]) for t in self._options]
            super(ComboKV,self).__init__(parent, options=self._values,
                                **kwargs)
        
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
    
    def _command_callback(self, value):
        if self._KV:
            value = self._keys[self._values.index(value)]
        if self._command:
            args_expected = self._no_args_expected(self._command)
            if args_expected == 0:
                self._command()
            elif args_expected == 1:
                self._command(value)
            else:
                print(""""Combo command function must accept either 0 or 1 arguments.\n
                The current command has {} arguments.""".format(args_expected))
        
    @property
    def key(self):
        '''' key that matches value'''
        return self._keys[self._values.index(self.value)]

    @key.setter
    def key(self, key):
        '''' changes value to match key '''
        self.value = self._values[self._keys.index(key)]
    
    def selectkey(self, key):
        self.value = self._values[self._keys.index(key)]
        self._command_callback(self.value)
            
    def selectvalue(self, value):
        self.value = value
        self._command_callback(self.value)
        
    def append(self, option):
        if self._KV:
            self._keys.append(str(option[1]))
            self._values.append(str(option[0]))
            super(ComboKV,self).append(str(option[0]))
        else:
            super(ComboKV,self).append(str(option))
          
    def insert(self, index, option):
        if self._KV:
            self._keys.insert(index, str(option[1]))
            self._values.insert(index, str(option[0]))
            super(ComboKV,self).insert(index, str(option[0]))
        else:
            super(ComboKV,self).insert(index, str(option))
        
    def remove(self, option):
        if self._KV:
            self._keys.remove(str(option[1]))
            self._values.remove(str(option[0]))
            super(ComboKV,self).remove(str(option[0]))
        else:
            super(ComboKV,self).remove(str(option))

    def clear(self):
        if self._KV:
            self._keys = []
            self._values = []
        super(ComboKV,self).clear()
        
    @property
    def options(self):
        """ Returns a list of options in the ListBox """
        return self._options
    
    @options.setter
    def options(self, options):
        self.clear()
        for i in range(len(options)):
            self.insert(i,options[i])
        
        
# test code
if __name__ == '__main__':
    from guizero import App,Box,Text,PushButton
    
    # ComboKV
    def combo_get(key):
        combo_label.value  = key
        combo2.value = key
        
    def combo_set():
        combo.key = combo2.value
        
    def combo_options():
        print(combo.options)
        combo.options  = [('Red', 89),('Green', 52),('Orange', 32)]
        combo2.options = [89,52,32]

    app    = App(height=100,width=600) 
    box    = Box(app,width='fill')
    Box(box, height='fill', width=4, align='left')
    autotext = Text(box, text='ComboKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    combo  = ComboKV(box, align='left', width=5,
                        options=[('Green', 12),('Yellow', 25),('Blue', 5)], 
                        command=combo_get)
    Text(box, align='left', text=' Key get ')
    combo_label  = Text(box, align='left', text='--', width=2, bg='green', color='white')
    Text(box, align='left', text=' Key set ')    
    combo2 = ComboKV(box,align='left', width=2, options=[12,25,5], command=combo_set)
    button = PushButton(box,align='left',text='Set combo',command=combo_options)
    app.display()
    