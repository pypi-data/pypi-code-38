from mcvgui.dialogs.simple_filter import SimpleFilter
import pyforms

from mcvgui.filters.adaptative_threshold    import AdaptativeThreshold

#from mcvgui.masks.polygons_mask            import PolygonsMask
#from mcvgui.masks.path_mask                import PathMask
from pythonvideoannotator_module_tracking.module_mcvgui.filters.background_subtract import BackgroundSubtract
from pythonvideoannotator_module_tracking.module_mcvgui.masks.polygons_mask         import PolygonsMask
from pythonvideoannotator_module_tracking.module_mcvgui.masks.path_mask             import PathMask

from mcvgui.blobs.find_blobs            import FindBlobs
from mcvgui.blobs.biggests_blobs        import BiggestsBlobs
from mcvgui.blobs.order_by_position     import OrderByPosition
from mcvgui.blobs.track_path            import TrackPath
from mcvgui.filters.morphologyex_open   import MorphologyExOpen
from mcvgui.filters.morphologyex_close  import MorphologyExClose
from pythonvideoannotator_module_tracking.module_mcvgui.blobs.sort_paths import SortPaths

from pythonvideoannotator_models_gui.dialogs import DatasetsDialog

from pythonvideoannotator_models.models.video.objects.object2d.datasets.contours import Contours
from pythonvideoannotator_models.models.video.objects.object2d.datasets.path import Path



class TrackingFilter(SimpleFilter):


    def __init__(self, parent=None, video=None):
        SimpleFilter.__init__(self,parent, video)

        self.paths_2_mask  = None
        self.video_capture = None
        self._video = None
        
        self.__load_blobs_filters()
        self.__load_images_filters()

    ########################################################################
    ### PRIVATE FUNCTION ###################################################
    ########################################################################

    def build_workflow_instance(self):
        # export the configured parameters
        data = {'project': self._video.project, 'load': True }
        for name, f in self._imgfilters.value: f.save(data)
        for name, f in self._blobsfilters.value: f.save(data)

        # create the workflow class and import the configured parameters
        instance = type('ProcessingPipeline', tuple(self.pipeline_classes()), {})(**data)
        return instance
        
    def __load_images_filters(self):
        # set the available filters for the images

        self.add_image_filters('Background subtract', [
            ('Background subtract', BackgroundSubtract  ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   )           
        ])

        self.add_image_filters('Background subtract + mask', [
            ('Background subtract', BackgroundSubtract  ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Mask',                PolygonsMask        )
        ])

        self.add_image_filters('Background subtract + path mask', [
            ('Background subtract', BackgroundSubtract  ),
            ('MorphologyEx open',   MorphologyExOpen    ),          
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Paths',               PathMask            )
        ])

        self.add_image_filters('Background subtract + mask + path mask', [
            ('Background subtract', BackgroundSubtract  ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Mask',                PolygonsMask        ),
            ('Paths',               PathMask            )
        ])


        #######################################################################

        self.add_image_filters('Adaptative threshold', [
            ('Threshold',           AdaptativeThreshold ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   ),
        ])

        self.add_image_filters('Adaptative threshold + mask', [
            ('Threshold',           AdaptativeThreshold ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Mask',                PolygonsMask        )
        ])
        
        self.add_image_filters('Adaptative threshold + path mask', [
            ('Threshold',           AdaptativeThreshold ),
            ('MorphologyEx open',   MorphologyExOpen    ),
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Paths',               PathMask            )
        ])

        self.add_image_filters('Adaptative threshold + mask + path mask', [
            ('Threshold',           AdaptativeThreshold ),
            ('MorphologyEx open',   MorphologyExOpen    ),          
            ('MorphologyEx close',  MorphologyExClose   ),
            ('Mask',                PolygonsMask        ),
            ('Paths',               PathMask            )
        ])

    def __load_blobs_filters(self):
        # set the available filters for the blobs
        self.add_blobs_filters('Find blobs + track path', [
            ('Find the blobs',      FindBlobs       ),
            ('Select the biggests', BiggestsBlobs   ),
            ('Sort blobs',          OrderByPosition ),
            ('Track paths',          TrackPath       ),
            ('Sort paths',          SortPaths       )
        ])

    ########################################################################
    ### PROPERTIES #########################################################
    ########################################################################

    @property
    def video(self): return self._video
    @video.setter
    def video(self, value):
        self._video         = value
        self.video_capture  = value.video_capture if value is not None else None


    @property
    def image_filters(self): return SimpleFilter.image_filters.fget(self)
    @image_filters.setter
    def image_filters(self, value): 
        SimpleFilter.image_filters.fset(self, value)
        self.video = self._video


    @property
    def blobs_filters(self): return SimpleFilter.blobs_filters.fget(self)
    @blobs_filters.setter
    def blobs_filters(self, value): 
        SimpleFilter.blobs_filters.fset(self, value)
        self.video = self._video

    



if __name__ == '__main__': 
    pyforms.start_app(TrackingFilter)