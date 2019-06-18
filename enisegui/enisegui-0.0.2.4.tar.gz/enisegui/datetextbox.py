from guizero   import Box
from tkinter   import StringVar
from .datepicker import Datepicker
import sys
        
class DateTextBox(Box):
    def __init__(self, parent=None, **kwargs):
        if sys.platform == 'linux':
            locale = 'fr_FR.UTF-8'
        else:
            locale = 'French_France.1252'
        # starting parameters
        length  = kwargs.pop('length', 10)
        text    = kwargs.pop('text', '')
        
        datevar = StringVar()
        datevar.set(text)
        
        super(DateTextBox,self).__init__(parent, **kwargs)
        self.entry = Datepicker(self.tk, datevar=datevar, 
                                locale=locale, entrywidth=length)
        self.entry.pack()   
              
    def focus(self):
        self.entry.focus()   
        
    @property
    def value(self):
        return self.entry.current_text
        
    @value.setter
    def value(self, value):
        self.entry.current_text=value

# test code
if __name__ == '__main__':
    from guizero import App,Box,Text,ButtonGroup
    
    app   = App() 
    box   = Box(app, width='fill')
    date  = DateTextBox(box, align='left')
    date.focus()
    app.display()
    