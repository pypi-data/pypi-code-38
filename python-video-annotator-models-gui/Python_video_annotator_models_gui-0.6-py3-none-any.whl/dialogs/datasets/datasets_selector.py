import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlCheckBoxList
from pythonvideoannotator_models.models.video import Video
from pythonvideoannotator_models.models.video.objects.object2d import Object2D
from pythonvideoannotator_models.models.video.objects.object2d.datasets.dataset import Dataset
from pythonvideoannotator_models_gui.dialogs.dialog import Dialog
from pythonvideoannotator_models_gui.dialogs.objects.objects import ObjectsDialog

class DatasetsSelectorDialog(ObjectsDialog):

    def __init__(self, parent_win=None):
        ObjectsDialog.__init__(self,parent_win=parent_win, title='Datasets selector',)

        self._datasets = ControlCheckBoxList('Datasets filter')

        self.formset = [('_videos','||','_objects','||','_datasets')]

        self._objects.changed_event  = self.__update_datasets
        self._datasets.changed_event = self.__datasets_changed_event

        self.load_order = ['_videos', '_objects', '_datasets']

        #for video in conf.PROJECT.videos: self += video

    #####################################################################
    ### PRIVATE FUNCTIONS ###############################################
    #####################################################################

    def __datasets_changed_event(self): self.datasets_changed_event()

    #####################################################################
    ### EVENTS ##########################################################
    #####################################################################

    def datasets_changed_event(self): pass

    #####################################################################
    ### FUNCTIONS #######################################################
    #####################################################################

    """
    def save_form(self, data={}, path=None):
        allparams = self.controls

        if hasattr(self, 'load_order'):
            for name in self.load_order:
                param = allparams[name]
                data[name] = {}
                param.save_form(data[name])
        else:
            for name, param in allparams.items():
                data[name] = {}
                param.save_form(data[name])
        return data
    """
  
    # used to update automaticly the name of the videos, objects and paths
    def refresh(self):
        ObjectsDialog.refresh(self)
        self._datasets.refresh()

    def clear(self):
        ObjectsDialog.clear(self)
        self._datasets.clear()
    
    def __add__(self, other):
        ObjectsDialog.__add__(self, other)
        if isinstance(other, Dataset):  self.__update_datasets()
        return self
        

    def __sub__(self, other):
        ObjectsDialog.__sub__(self, other)
        if isinstance(other, Dataset):  self.__update_datasets()
        return self
    

    def update_objects(self):
        """
        Update the objects in the list
        """
        ObjectsDialog.update_objects(self)
        self.__update_datasets()
    


    def __update_datasets(self):
        """
        Update the paths in the list
        """
        datasets = [elem for elem, checked in self._datasets.items]

        datasets_list = []
        for obj, checked in self._objects.items:
            if not isinstance(obj,Object2D): continue

            for dataset in obj.datasets:
                if hasattr(self, '_datasets_filter') and not self._datasets_filter(dataset): continue
                
                if dataset not in datasets_list: datasets_list.append(dataset)

                if not checked and dataset in datasets:
                    self._datasets -= dataset
                elif checked and dataset not in datasets:
                    self._datasets += (dataset, False)

        for dataset in datasets:
            if dataset not in datasets_list: self._datasets -= dataset

        

    

    #####################################################################
    ### PROPERTIES ######################################################
    #####################################################################

    @property
    def datasets(self): return self._datasets.value

    @property
    def selected_data(self):
        videos  = self._videos.value
        datasets= self._datasets.value

        res     = []
        for video in videos:
            datasets_list = []
            for obj in video.objects2D:
                for dataset in obj.datasets:
                    if dataset in datasets:
                        datasets_list.append(dataset)
            res.append( (video, datasets_list) )
        return res
        
    @property
    def datasets_filter(self): return self._datasets_filter
    @datasets_filter.setter
    def datasets_filter(self, value): self._datasets_filter = value

    
    
    
if __name__ == "__main__":   pyforms.startApp( DatasetsSelectorDialog )