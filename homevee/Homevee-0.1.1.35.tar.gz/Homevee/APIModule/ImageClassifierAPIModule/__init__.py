from abc import abstractmethod

from Homevee.APIModule import APIModule
from Homevee.Item.Status import *
from Homevee.Manager.ControlManager.ImageClassifierManager import ImageClassifierManager


class ImageClassifierAPIModule(APIModule):
    def __init__(self, manager: ImageClassifierManager):
        super(ImageClassifierAPIModule, self).__init__()
        self.manager = manager
        return

    @abstractmethod
    def get_function_mappings(self):
        raise NotImplementedError

    def get_classes(self, user, request, db):
        data = self.manager.get_classes(db)
        return Status(type=STATUS_OK, data={'classes':data})

    def save_class(self, user, request, db):
        data = self.manager.save_class(user, request['id'], request['data'], request['classname'], db)
        return Status(type=STATUS_OK, data=data)

    def start_training(self, user, request, db):
        data = self.manager.start_training(user, db)
        return Status(type=STATUS_OK, data=data)

    def get_performance_settings(self, user, request, db):
        data = self.manager.get_performance_settings(user, db)
        return Status(type=STATUS_OK, data=data)

    def set_performance_settings(self, user, request, db):
        data = self.manager.set_performance_settings(user, request['data'], db)
        return Status(type=STATUS_OK, data=data)

    def change_image_class(self, user, request, db):
        data = self.manager.change_image_class(user, request['ids'], request['newclass'], db)
        return Status(type=STATUS_OK, data=data)

    def get_image(self, user, request, db):
        data = self.manager.get_image(user, request['id'], db)
        print(data)
        return Status(type=STATUS_OK, data=data)

    def get_class_images(self, user, request, db):
        data = self.manager.get_class_images(user, request['class'], request['show'], request['offset'], db)
        return Status(type=STATUS_OK, data={'images':data})

    def upload_images(self, user, request, db):
        data = self.manager.upload_images(user, request['data'], request['class'], db)
        return Status(type=STATUS_OK, data=data)

    def classify_image(self, user, request, db):
        data = self.manager.classify_image(user, request['imagedata'], db)
        return Status(type=STATUS_OK, data=data)

    def delete_images(self, user, request, db):
        data = self.manager.delete_images(user, request['ids'], db)
        return Status(type=STATUS_OK, data=data)