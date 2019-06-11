import cv2, os, simplejson as json
from confapp import conf
from pythonvideoannotator_module_tracking.tracking_window import TrackingWindow


class Module(object):

    def __init__(self):
        """
        This implements the Path edition functionality
        """
        super(Module, self).__init__()
        self.tracking_window = TrackingWindow(self, project=self._project)

        self.mainmenu[1]['Modules'].append(
            {'Track objects': self.tracking_window.show, 'icon':conf.ANNOTATOR_ICON_PATH },         
        )

    ######################################################################################
    #### IO FUNCTIONS ####################################################################
    ######################################################################################
    
    def save(self, data, project_path=None):
        data = super(Module, self).save(data, project_path)

        modules_folder = os.path.join(project_path, 'modules')
        if not os.path.exists(modules_folder): os.makedirs(modules_folder)

        tracking_folder = os.path.join(modules_folder, 'tracking')
        if not os.path.exists(tracking_folder): os.makedirs(tracking_folder)

        trackingdata = self.tracking_window.save_form({}, tracking_folder)

        with open(os.path.join(tracking_folder, 'config.json'), 'w') as outfile:
            json.dump(trackingdata, outfile)

        return data

    def load(self, data, project_path=None):
        super(Module, self).load(data, project_path)
        
        tracking_folder = os.path.join(project_path, 'modules', 'tracking')
        configfile = os.path.join(tracking_folder, 'config.json')

        if os.path.exists(configfile):

            with open(configfile) as infile:
                trackingdata = json.load(infile)

            self.tracking_window.load_form(trackingdata, tracking_folder)

        