from trosnoth.gui.screenManager.screenManager import ScreenManager
from trosnoth.gui.errors import MultiWindowException

class WindowManager(ScreenManager):
    '''Handles all the dialog boxes and the main screen'''

    def __init__(self, app, element, size, settings, caption):
        super(WindowManager, self).__init__(app, size, settings, caption)
        self.boxes = []

    def createInterface(self, element):
        super(WindowManager,self).createInterface(element)
        self._fixElements()

    def showDialog(self, dialog):
        self.boxes.insert(len(self.elements)-1, dialog)
        self._fixElements()

    def closeDialog(self, dialog):
        if dialog not in self.boxes:
            raise MultiWindowException(
                    'Attempt to close a dialog that was not open')
        self.boxes.remove(dialog)
        self._fixElements()

    def dialogFocus(self, dialog):
        index = self.boxes.index(dialog)
        self.boxes = (self.boxes[:index] + self.boxes[index+1:] +
                [self.boxes[index]])
        self._fixElements()

    def _fixElements(self):
        self.elements = [self.interface]+ self.boxes
        if self.pointer is not None:
            self.elements.append(self.pointer)
        self.elements.append(self.terminator)
