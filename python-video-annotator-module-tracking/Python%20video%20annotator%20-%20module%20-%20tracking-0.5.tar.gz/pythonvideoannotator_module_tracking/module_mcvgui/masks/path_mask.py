from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlSlider
from pyforms.controls import ControlButton
from pyforms.controls import ControlEmptyWidget
from pythonvideoannotator_module_tracking.module_mcvapi.masks.path_mask import PathMask as Class

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog
from pythonvideoannotator_models.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path


class PathMask(Class, BaseWidget):
    
    def __init__(self, **kwargs):
        BaseWidget.__init__(self, 'Path mask')
        Class.__init__(self, **kwargs)

        try:
            self.layout().setContentsMargins(10, 5, 10, 5)
            self.setMinimumHeight(170)
        except:
            pass

        self._control_pathmask_radius       = ControlSlider('Mask radius', default=30,  minimum=1, maximum=600)
        self._panel                         = ControlEmptyWidget('Panel', default=DatasetsDialog() )
        self._panel.value.interval_visible  = False
        self._panel.value.datasets_filter   = lambda x: isinstance(x, (Contours,Path) )

        self._panel.value.datasets_changed_event = self.__update_paths

        self._formset = [ 
            '_panel',
            '_control_pathmask_radius',         
        ]

        self._control_pathmask_radius.changed_event = self.__control_pathmask_radius_changed_event


    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################
    
    
    #####################################################################
    ### EVENTS ##########################################################
    #####################################################################

    def __control_pathmask_radius_changed_event(self):
        self._param_pathmask_radius = self._control_pathmask_radius.value


    def destroy(self, destroyWindow = True, destroySubWindows = True):
        self._panel.value.destroy(destroyWindow, destroySubWindows)
        super(PathMask, self).destroy(destroyWindow, destroySubWindows)

    def __update_paths(self):
        for video, (begin,end), paths in self._panel.value.selected_data:
            if video.video_capture==self._video:            
                self._param_pathmask_paths = paths
                break

    @property
    def datasets(self): return None

    @property
    def video(self): return None
    @video.setter 
    def video(self, value): 
        self._video = value
        self.__update_paths()
    
    