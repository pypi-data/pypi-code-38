import pyforms
from confapp import conf
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress
from pyforms.controls import ControlImage

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.path import Path
from pythonvideoannotator_models_gui.models.video.objects.object2d.datasets.contours import Contours

import numpy as np, cv2




class PathMapWindow(BaseWidget):

    def __init__(self, parent=None):
        super(PathMapWindow, self).__init__('Path map', parent_win=parent)
        self.mainwindow = parent

        self.set_margin(5)
        
        self.setMinimumHeight(400)
        self.setMinimumWidth(800)



        self._datasets_panel= ControlEmptyWidget('Paths')
        self._progress      = ControlProgress('Progress')       
        self._apply         = ControlButton('Apply', checkable=True)
        self._image         = ControlImage('Image')

        self._radius    = ControlSlider('Radius', default=10, minimum=1, maximum=255)
    
            
        self._formset = [
            '_datasets_panel',
            '=',
            '_radius',
            '_image',
            '_apply',
            '_progress'
        ]

        self.load_order = ['_datasets_panel']

        self.datasets_dialog        = DatasetsDialog(self)
        self._datasets_panel.value = self.datasets_dialog
        self.datasets_dialog.datasets_filter = lambda x: isinstance(x, (Path, Contours))

        self._apply.value       = self.__apply_event
        self._apply.icon        = conf.ANNOTATOR_ICON_PATH

        self._progress.hide()



    ###########################################################################
    ### EVENTS ################################################################
    ###########################################################################



    ###########################################################################
    ### PROPERTIES ############################################################
    ###########################################################################

    @property
    def datasets(self): return self.datasets_dialog.datasets
    

    def __apply_event(self):

        if self._apply.checked:

            if len(self.datasets_dialog.datasets)==0:
                self.message('You have to select a Path or a Contour', 'Error', 'error')
                self._apply.checked=False
                return

            self._datasets_panel.enabled = False            
            self._apply.label           = 'Cancel'

            total_2_analyse  = 0
            for video, (begin, end), datasets in self.datasets_dialog.selected_data:
                total_2_analyse += (end-begin+1)*len(datasets)


            self._progress.min = 0
            self._progress.max = total_2_analyse
            self._progress.show()

            count = 0
            for video, (begin, end), datasets in self.datasets_dialog.selected_data:
                begin   = int(begin)
                end     = int(end)+1

                counter_img = np.zeros( (video.video_height, video.video_width), dtype=np.float32)

                for index in range(begin, end):
                    if not self._apply.checked: break
                    for dataset in datasets:
                        if not self._apply.checked: break

                        pos = dataset.get_position(index)
                        if pos is None: continue

                        pos = int(round(pos[0],0)), int(round(pos[1],0))

                        tmp = np.zeros_like(counter_img)

                        cv2.circle(tmp, pos, int(self._radius.value), 1, -1)
                        counter_img += tmp

                        if (index % 31) == 0:
                            tmp = cv2.convertScaleAbs(counter_img)
                            color = cv2.applyColorMap(tmp, cv2.COLORMAP_JET)
                            self._image.value = color

                        self._progress.value = count
                        count += 1

                tmp = cv2.convertScaleAbs(counter_img)
                color = cv2.applyColorMap(tmp, cv2.COLORMAP_JET)
                self._image.value = color

                image = video.create_image()
                image.name = 'pathmap-{0}'.format(len(list(video.images)))
                image.image = color

                

            self._datasets_panel.enabled = True 
            self._apply.label           = 'Apply'
            self._apply.checked         = False
            self._progress.hide()





    


if __name__ == '__main__': 
    pyforms.startApp(PathMapWindow)
