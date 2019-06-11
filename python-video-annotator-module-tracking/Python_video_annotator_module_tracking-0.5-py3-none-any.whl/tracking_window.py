from confapp import conf

"""class Settings(object):
    PYFORMS_MODE = 'TERMINAL'
    SETTINGS_PRIORITY = 0
conf += Settings
"""
import pyforms, math, cv2, sys, os, json
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlNumber
from pyforms.controls import ControlList
from pyforms.controls import ControlCombo
from pyforms.controls import ControlToolBox
from pyforms.controls import ControlButton
from pyforms.controls import ControlCheckBox
from pyforms.controls import ControlCheckBoxList
from pyforms.controls import ControlEmptyWidget
from pyforms.controls import ControlProgress

from pythonvideoannotator_models.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path

from pythonvideoannotator_module_tracking.module_mcvgui.dialogs.tracking_filter import TrackingFilter
from pythonvideoannotator_models.models.video.objects.object2d import Object2D


from pythonvideoannotator_models_gui.dialogs import DatasetsDialog

import simplejson as json


class TrackingWindow(BaseWidget):

    def __init__(self, *args, **kwargs):
        super(TrackingWindow, self).__init__('Tracking window', **kwargs)
        self.project = kwargs.get('project', None)

        if conf.PYFORMS_MODE=='GUI':
            self.set_margin(5)
            self.setMinimumHeight(800)
            self.setMinimumWidth(1100)
        
        self._toggle_btn    = ControlButton('Hide datasets list', checkable=True)
        self._input         = ControlEmptyWidget('Videos to process')
        
        self._filter_panel  = ControlEmptyWidget('Tracking filter')
        self._progress      = ControlProgress('Progress')
        self._apply         = ControlButton('Apply', checkable=True)

        
        self.formset = [
            '_toggle_btn',
            '_input',
            '_filter_panel',
            '_apply',
            '_progress',
        ]

        # configure the dialog with the datasets to update
        self.input_dialog = DatasetsDialog(self)
        self.input_dialog.objects_filter  = lambda x: isinstance(x, Object2D)
        self.input_dialog.datasets_filter = lambda x: isinstance(x, (Contours,Path) )
        self.input_dialog.video_selection_changed_event = self.__video_selection_changed_event
        self.input_dialog.project = self.project
        self._input.value = self.input_dialog

        self.load_order = ['_input','_filter_panel']

        self._filter                = TrackingFilter(parent=self)
        self._filter_panel.value    = self._filter
        self._apply.value           = self.__apply_event
        try:
            self._apply.icon        = conf.ANNOTATOR_ICON_PATH
        except AttributeError:
            pass

        self._toggle_btn.value   = self.__toggle_btn_click_event
        self._toggle_btn.checked = True

        self._progress.hide()

    
    ###################

    ########################################################
    ### EVENTS ################################################################
    ###########################################################################



    def __toggle_btn_click_event(self):
        if self._input.visible:
            self._toggle_btn.label = 'Show datasets list'
            self._input.hide()
        else:
            self._toggle_btn.label = 'Hide datasets list'
            self._input.show()

    def __video_selection_changed_event(self):
        video = self.input_dialog.selected_video
        self.player.stop()          
        self._filter.clear()
        self._filter.video = video
        self._filter.clear()
        self.player.call_next_frame()

    ###########################################################################
    ### PROPERTIES ############################################################
    ###########################################################################

    @property
    def videos(self): return self.input_dialog.videos
    
    @property
    def player(self): return self._filter._player

    def process(self):
        self._apply.checked = True
        self.__apply_event()
    
    def __apply_event(self):

        if self._apply.checked:
            self._input.enabled         = False
            self._filter_panel.enabled  = False
            self._apply.label           = 'Cancel'
            self.player.stop()
            
            # calculate the total number of frames to analyse
            total_2_analyse  = 0
            for video, (begin, end), datasets_list in self.input_dialog.selected_data:
                total_2_analyse += end-begin+1

            self._progress.label = 'Analysing videos'
            self._progress.min = 0
            self._progress.max = total_2_analyse
            self._progress.show()

            # process each selected video
            count = 0
            for video, (begin, end), datasets_list in self.input_dialog.selected_data:
                print('Open video', video.filepath)
                capture = cv2.VideoCapture(video.filepath)
                capture.set(cv2.CAP_PROP_POS_FRAMES, begin)

                self._filter.video = video
                self._filter.clear()
                
                begin, end = int(begin), int(end)+1

                #set the video in the one frame before and read the frame.
                #I use this technique because for some formats of videos opencv does not jump immediately to the requested frame
                blobs_paths     = None
                firstblob_index = begin
                setfirstblob_index = True

                # process the frames of the video
                for index in range(begin, end):
                    res, frame = capture.read()
                    
                    if not res: 
                        end = index
                        break
                    if not self._apply.checked: break

                    blobs_paths = self._filter.processflow(frame, frame_index=index)

                    if setfirstblob_index and len(blobs_paths)>0:
                        setfirstblob_index = False
                        firstblob_index = index

                    self._progress.value = count
                    count += 1

                if self._apply.checked:
                    self._filter.end(
                        blobs_paths, 
                        progress_control=self._progress,
                        out_datasets=datasets_list,
                        firstblob_index=firstblob_index,
                        begin=begin,
                        end=end
                    )

            self._input.enabled         = True
            self._filter_panel.enabled  = True
            self._apply.label           = 'Apply'
            self._apply.checked         = False
            self._progress.hide()





    


if __name__ == '__main__':
    from pythonvideoannotator_models.models import Project
    from pythonvideoannotator_models_gui.dialogs import Dialog
    
    proj = Project()
    proj.load({}, '/home/ricardo/Downloads/cecilia_movies/movies/20170526/video37_2017-05-26T10_23_51/video-annotator-prj')
    Dialog.project = proj
    
    pyforms.start_app(TrackingWindow, app_args={'project':proj})
    proj.save()
