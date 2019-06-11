import cv2
from confapp import conf
from pythonvideoannotator_module_pathmap.pathmap_window import PathMapWindow


class Module(object):

    def __init__(self):
        """
        This implements the Path edition functionality
        """
        super(Module, self).__init__()
        self.pathmap_window = PathMapWindow(self)

        self.mainmenu[1]['Modules'].append(
            {'Path map': self.pathmap_window.show, 'icon':conf.ANNOTATOR_ICON_PATHMAP },            
        )