from abc import abstractmethod

from Homevee.APIModule.ImageClassifierAPIModule.ARControlAPIModule import ImageClassifierAPIModule
from Homevee.Manager.ControlManager.ImageClassifierManager.PeopleClassifierManager import PeopleClassifierManager

ACTION_KEY_CLASSIFY_IMAGE = "classifyperson"
ACTION_KEY_GET_CLASSES = "getpeopleclasses"
ACTION_KEY_SAVE_CLASS = "savepeopleclass"
ACTION_KEY_START_TRAINING = "startpeopletraining"
ACTION_KEY_CHANGE_IMAGE_CLASS = "changepeopleimageclass"
ACTION_KEY_GET_CLASS_IMAGES = "getpeopleclassimages"
ACTION_KEY_GET_IMAGE = "getpeopleimage"
ACTION_KEY_GET_PERFORMANCE_SETTINGS = "getpeopleperformancesettings"
ACTION_KEY_SET_PERFORMANCE_SETTINGS = "setpeopleperformancesettings"
ACTION_KEY_UPLOAD_IMAGES = "uploadpeopleimages"
ACTION_KEY_DELETE_IMAGES = "deletepeopleimages"

class PeopleClassifierAPIModule(ImageClassifierAPIModule):
    def __init__(self):
        manager = PeopleClassifierManager()
        super(PeopleClassifierAPIModule, self).__init__(manager)
        return

    @abstractmethod
    def get_function_mappings(self):
        mappings = {
            ACTION_KEY_CLASSIFY_IMAGE: self.classify_image,
            ACTION_KEY_GET_CLASSES: self.get_classes,
            ACTION_KEY_SAVE_CLASS: self.save_class,
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