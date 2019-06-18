from guizero   import Box
from tkinter   import StringVar
from .autoentry import AutoEntry
        
class AutoTextBoxKV(Box):
    def __init__(self, parent=None, autolist=[], **kwargs):
        # starting parameters
        text    = kwargs.pop('text', '')
        change  = kwargs.pop('change', None)
        command = kwargs.pop('command', None)
        max     = kwargs.pop('max', 8)
        length  = kwargs.pop('length', 10)
        # initialize guizero box
        super(AutoTextBoxKV,self).__init__(parent, **kwargs)
        # attach tkinter widget inside self.tk Frame
        textvariable = StringVar()
        textvariable.set(text)
        self._entry = AutoEntry(self.tk, autolist, textvariable=textvariable,
                            change=change, command=command, max=max, width=length)
        self._entry.pack()
        
    def focus(self):
        # set focus to entry widget
        self._entry.focus()    
        
    def update_command(self, command):
        # update command callback
        self._entry.update_command(command)
        
    def update_change(self, change):
        # update change callback
        self._entry.update_change(change)
        
    @property
    def key(self):
        # get key
        return self._entry.key
        
    @property
    def value(self):
        # get value
        return self._entry.value

    @value.setter
    def value(self, value):
        # set value
        self._entry.value = value
        
       
# test code
if __name__ == '__main__':
    from guizero import App,Box,Text
            
    # autocomplete callbacks   
    def choicelist(pattern):
        return [w for w in autolist if pattern in w]
        
    def choicelistKV(pattern):
        return [autolistKV[i] for i in range(len(autolistKV))
                        if pattern in autolistKV[i][0]]
    def auto_get(key):
        if key:
            autoval.value = key
        else:
            autoval.value = 'None'
 
    with open('autolist.txt') as file:
        autolist = file.read()
    autolist   = autolist.split('\n')
    autolistKV = [(autolist[i],'key-'+str(i)) for i in range(len(autolist))]

    app    = App(height=100) 
    autobox = Box(app, width='fill')
    Box(autobox, height='fill', width=4, align='left')
    autotext = Text(autobox, text='AutoTextBoxKV', width=18, align='left')
    autotext.tk.config(font='Helvetica 12 bold')
    autotext.tk.config(anchor='w')
    auto   = AutoTextBoxKV(autobox, width=20, max=6, text='Holmes Scott',
                            change=choicelistKV, command=auto_get, align='left')
    Box(autobox, width=4, height='fill', align='left')
    Text(autobox, text=' Key : ', align='left')
    autoval = Text(autobox, text='--', bg='green', color='white', align='left')
    auto.focus()
    
    app.display()

  
        