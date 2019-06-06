'''
Created on Aug 17, 2018

@author: reynolds
'''

from PyQt5.QtWidgets import QComboBox, QWidget, QLabel, QPushButton, QLineEdit, QGridLayout, QFrame

class SoftwareLED(QWidget):
    ''' a class for a software LED '''
    
    def __init__(self,parent=None,text=''):
        ''' constructor '''
        QWidget.__init__(self,parent)
        self.label = QLabel(text)
        self.label.setFrameShape(QFrame.Panel)
        self.label.setFrameShadow(QFrame.Raised)
        self.label.setLineWidth(2)
        l = QGridLayout()
        l.addWidget(self.label)
        self.setLayout(l)
        
    def setGood(self):
        ''' sets a good status '''
        self.label.setStyleSheet('background-color:green')
        
    def setWarning(self):
        ''' sets a warning status '''
        self.label.setStyleSheet('background-color:orange')
        
    def setBad(self):
        ''' sets a bad status '''
        self.label.setStyleSheet('background-color:red')
        
    def reset(self):
        ''' resets the led to the original state of transparent '''
        self.label.setStyleSheet('')

class InputWidget(QWidget):
    ''' generic input widget with a label '''
    
    def __init__(self,parent=None,text=[],widget=[],spacing=10,row=[0,0],col=[0,1]):
        ''' constructor default layout is horizontal '''
        QWidget.__init__(self,parent)

        # set the text and input widgets
        self.text = text
        #self.text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.widget = widget
        #self.widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # layout the widget
        l = QGridLayout()
        l.setSpacing(spacing)
        l.addWidget(self.text,row[0],row[0],1,1)
        l.addWidget(self.widget,row[1],col[1],1,1)
        self.setLayout(l)
    
    def setLabelAlignment(self,alignment):
        ''' sets the label alignment '''
        self.text.setAlignment(alignment)
        
    def setWidgetAlignment(self,alignment):
        ''' sets the widget alignment '''
        self.widget.setAlignment(alignment)
        
    def setLabelFont(self,font):
        ''' sets the label font '''
        self.text.setFont(font)
        
    def setWidgetFont(self,font):
        ''' sets the widget font '''
        self.widget.setFont(font)
        
    def setAlignment(self,alignment):
        ''' sets the alignment '''
        self.setLabelAlignment(alignment)
        self.setLabelAlignment(alignment)
        
    def setFont(self,font):
        ''' sets the label font '''
        self.setLabelFont(font)
        self.setWidgetFont(font)
    
    def setEnabled(self,enabled=False):
        ''' sets the ui input enabled state '''
        self.widget.setEnabled(enabled)
        
    def setReadOnly(self,readOnly):
        ''' sets read only '''
        self.widget.setReadOnly(readOnly)

class LabelledInputWidget(InputWidget):
    ''' labelled input widget. Abstract '''
    
    def __init__(self,parent=None,label='',default='',spacing=10,row=[0,0],col=[0,1]):
        ''' constructor '''
        l = QLabel(label)
        t = QLineEdit(default)
        super().__init__(parent,l,t,spacing,row,col)

    
    def getLabel(self):
        ''' returns the labelled text '''
        pass
    
    def setLabel(self,label=''):
        ''' sets the label text '''
        pass

    def getText(self):
        ''' returns the line edit text '''
        return self.widget.text()

    def setText(self,text=''):
        ''' sets the line edit text '''
        self.widget.setText(text)
        
    def setInputColor(self,color='white'):
        ''' sets the color of the widget '''
        self.widget.setStyleSheet('background-color: ' + color)
        
    def setStyleSheet(self,style):
        ''' sets the style of the widget '''
        self.text.setStyleSheet(style)
        self.widget.setStyleSheet(style)
        
    def setReadOnly(self,readonly):
        ''' sets the read only status of the widget '''
        self.widget.setReadOnly(readonly)

class LabelledComboWidget(InputWidget):
    ''' Labelled combo widget '''
    
    def __init__(self,parent=None,label='',items=[],spacing=10,row=[0,0],col=[0,1]):
        ''' constructor '''
        c = QComboBox()
        c.addItems(items)
        l = QLabel(label)
        super().__init__(parent,l,c,spacing,row,col)

    def setItems(self,items=[]):
        ''' sets the items '''
        for s in items:
            self.widget.addItem(s)

    def getSelected(self):
        ''' returns the selected items '''
        return str(self.widget.currentText())

class ButtonInputWidget(InputWidget):
    ''' button input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10,row=[0,0],col=[0,1]):
        ''' constructor '''
        b = QPushButton(label)
        t = QLineEdit(default)
        super().__init__(parent,t,b,spacing,row,col)

    def getText(self):
        ''' returns the text from the line edit '''
        return self.text.text()

    def setButtonColor(self,color):
        ''' sets the button color '''
        self.widget.setStyleSheet("background-color: " + color)

    def setButtonText(self,text=''):
        ''' sets the text of the button '''
        self.widget.setText(text)
        
    def setReadOnly(self,readonly):
        ''' sets the line edit read only status '''
        self.text.setReadOnly(readonly)

class FHLabelledInputWidget(LabelledInputWidget):
    ''' Forward horizontal input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,0],[0,1])

class RHLabelledInputWidget(LabelledInputWidget):
    ''' reverse horizontal labelled input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,0],[1,0])

class FVLabelledInputWidget(LabelledInputWidget):
    ''' Forward versitcal labelled input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,1],[0,0])

class RVLabelledInputWidget(LabelledInputWidget):
    ''' Reverse vertical labelled input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[1,0],[0,0])

class FHButtonInputWidget(ButtonInputWidget):
    ''' Forward horizontal button input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,0],[0,1])

class RHButtonInputWidget(ButtonInputWidget):
    ''' Reverse horizontal button input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,0],[1,0])

class FVButtonInputWidget(ButtonInputWidget):
    ''' Fowrard horizontal button input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[0,1],[0,0])

class RVButtonInputWidget(ButtonInputWidget):
    ''' Reverse vertical input widget '''
    
    def __init__(self,parent=None,label='',default='',spacing=10):
        ''' constructor '''
        super().__init__(parent,label,default,spacing,[1,0],[0,0])

class FHLabelledComboWidget(LabelledComboWidget):
    ''' Forward horizontal labelled combo widget '''
    
    def __init__(self,parent=None,label='',items=[],spacing=10):
        ''' constructor '''
        super().__init__(parent,label,items,spacing,[0,0],[0,1])

class RHLabelledComboWidget(LabelledComboWidget):
    '''Reverse horizontal labelled combo widget '''
    
    def __init__(self,parent=None,label='',items=[],spacing=10):
        ''' constructor '''
        super().__init__(parent,label,items,spacing,[0,0],[1,0])

class FVLabelledComboWidget(LabelledComboWidget):
    ''' Forward vertical labelled combo widget '''
    
    def __init__(self,parent=None,label='',items=[],spacing=10):
        ''' constructor '''
        super().__init__(parent,label,items,spacing,[0,1],[0,0])

class RVLabelledComboWidget(LabelledComboWidget):
    ''' a rear vertical combo widget '''
    
    def __init__(self,parent=None,label='',items=[],spacing=10):
        ''' constructor '''
        super().__init__(parent,label,items,spacing,[1,0],[0,0])
        
class TwoStateTextWidget(QWidget):
    ''' A text box that indicates state by color '''
    
    def __init__(self,parent=None,gstate=None,text='',readonly=True):
        ''' constructs the state box'''
        QWidget.__init__(self,parent)
        
        self._text = QLineEdit(text)
        self._text.setReadOnly(readonly)
        self._good = gstate
        self._state = False
        
    def update(self,state):
        ''' updates the state of the box '''
        if state == self._state: return
        if state == self._good:
            self._text.setStyleSheet("background-color: green")
            self._text.setText(str(state))
        else:
            self._text.setStyleSheet("background-color: red")
            self._text.setText(str(state))
        self._state = state == self._good