from abc import abstractmethod

from Homevee.APIModule.ImageClassifierAPIModule import ImageClassifierAPIModule
from Homevee.Manager.ControlManager.ImageClassifierManager.ARControlManager import ARControlManager

ACTION_KEY_CLASSIFY_IMAGE = "arcontrol"
ACTION_KEY_GET_CLASS = "getarcontrolclasses"
ACTION_KEY_SAVE_CLASSES = "savearcontrolclasses"
ACTION_KEY_START_TRAINING = "startarcontroltraining"
ACTION_KEY_CHANGE_IMAGE_CLASS = "changearcontrolimageclass"
ACTION_KEY_GET_CLASS_IMAGES = "getarcontrolclassimages"
ACTION_KEY_GET_IMAGE = "getarcontrolimage"
ACTION_KEY_GET_PERFORMANCE_SETTINGS = "getarcontrolperformancesettings"
ACTION_KEY_SET_PERFORMANCE_SETTINGS = "setarcontrolperformancesettings"
ACTION_KEY_UPLOAD_IMAGES = "uploadarcontrolimages"
ACTION_KEY_DELETE_IMAGES = "deletearcontrolimages"

class ARControlAPIModule(ImageClassifierAPIModule):
    def __init__(self):
        manager = ARControlManager()
        super(ARControlAPIModule, self).__init__(manager)
        return

    @abstractmethod
    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_CLASSIFY_IMAGE: self.classify_image,
            ACTION_KEY_GET_CLASS: self.get_classes,
            ACTION_KEY_SAVE_CLASSES: self.save_class,
            ACTION_KEY_START_TRAINING: self.start_training,
            ACTION_KEY_CHANGE_IMAGE_CLASS: self.change_image_class,
            ACTION_KEY_GET_CLASS_IMAGES: self.get_class_images,
            ACTION_KEY_GET_IMAGE: self.get_image,
            ACTION_KEY_GET_PERFORMANCE_SETTINGS: self.get_performance_settings,
            ACTION_KEY_SET_PERFORMANCE_SETTINGS: self.set_performance_settings,
            ACTION_KEY_UPLOAD_IMAGES: self.upload_images,
            ACTION_KEY_DELETE_IMAGES: self.delete_images
        }
        return mappings