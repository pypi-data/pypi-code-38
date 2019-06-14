import base64
import io
import json
import os
import time
import traceback
from _thread import start_new_thread

from PIL import Image

from Homevee.Exception import NoPermissionException, AlreadyTrainingException
from Homevee.Helper import Logger
from Homevee.Utils import Constants, FileUtils
from Homevee.Utils.Database import Database


class ImageClassifierManager:
    def __init__(self, data_table, learning_data_table, settings_prefix, is_training_tag, classifier_tag, classifier, retrainer):
        self.data_table = data_table
        self.learning_data_table = learning_data_table
        self.settings_prefix = settings_prefix
        self.is_training_tag = is_training_tag
        self.classifier_tag = classifier_tag
        self.classifier = classifier
        self.retrainer = retrainer
        return

    def get_classes(self, db: Database = None):
        results = db.select_all("SELECT * FROM "+self.data_table)
        classes = []
        for row in results:
            item = {'id': int(row['ID']), 'name': row['NAME'], }
            classes.append(item)
        item = {'id': None, 'name': 'Nicht zugeordnet'}
        classes.append(item)
        return classes

    def save_class(self, user, id, data, class_name, db: Database = None):
        if db is None:
            db = Database()
        return

    def get_class_data(self, id, db: Database = None):
        if db is None:
            db = Database()
        return db.select_one("SELECT * FROM "+self.data_table+" WHERE ID = :id;", {'id': id})

    def start_training(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission('admin'):
            raise NoPermissionException
        is_training = db.get_server_data(self.is_training_tag)
        if (is_training is not None and is_training == "true"):
            raise AlreadyTrainingException
        start_new_thread(self.training_thread, (user, None))

    def get_performance_settings(self, user, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission('admin'):
            raise NoPermissionException
        tf_data = {}
        indices = ['TF_TRAINING_STEPS', 'TF_MODEL_SIZE', 'TF_MODEL_IMAGE_SIZE']
        for index in indices:
            result = db.select_one("SELECT VALUE FROM SERVER_DATA WHERE KEY = :key",
                                   {'key': self.settings_prefix+index})
            if (result is not None and 'VALUE' in result):
                tf_data[index] = result['VALUE']
        return {'data': tf_data, 'graph_sizes': self.classifier.get_graph_sizes(),
                'image_sizes': self.retrainer.get_image_sizes()}

    def set_performance_settings(self, user, data, db: Database = None):
        if db is None:
            db = Database()
        if not user.has_permission('admin'):
            raise NoPermissionException
        data = json.loads(data)
        indices = ['TF_TRAINING_STEPS', 'TF_MODEL_SIZE', 'TF_MODEL_IMAGE_SIZE']
        for index in indices:
            param_array = {'value': data[index], 'key': self.settings_prefix+index}
            db.update("UPDATE OR IGNORE SERVER_DATA SET VALUE = :value WHERE KEY = :key;", param_array)
            db.insert("INSERT OR IGNORE INTO SERVER_DATA (VALUE, KEY) VALUES (:value, :key);", param_array)

    def training_thread(self, user, d):
        db = Database()
        db.set_server_data(self.is_training_tag, False)
        try:
            self.retrainer.start_training(user.username)
        except:
            if (Logger.IS_DEBUG):
                traceback.print_exc()
        db.set_server_data(self.is_training_tag, "false")

    def delete_images(self, user, ids, db: Database = None):
        if db is None:
            db = Database()
        ids = json.loads(ids)
        for id in ids:
            Logger.log("deleting: " + str(id))
            item = db.select_one("SELECT * FROM "+self.learning_data_table+" WHERE ID == :id;", {'id': id})
            if (item is not None):
                rel_path = item['PATH']
                image_path = os.path.join(Constants.DATA_DIR, rel_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                else:
                    Logger.log(image_path + " not found")
                db.delete("DELETE FROM "+self.learning_data_table+" WHERE ID == :id;", {'id': id})

    def change_image_class(self, user, ids, new_class, db: Database = None):
        if db is None:
            db = Database()
        if new_class == "-1":
            new_class = None
        ids = json.loads(ids)
        Logger.log(ids)
        for id in ids:
            db.update("UPDATE "+self.learning_data_table+" SET CLASS_ID = :key WHERE ID == :id;",
                      {'key': new_class, 'id': id})

    def get_image(self, user, id, db: Database = None):
        if db is None:
            db = Database()
        result = db.select_one("SELECT PATH FROM " + self.learning_data_table + " WHERE ID == :id", {'id': id})
        rel_path = result['PATH']
        path = os.path.join(Constants.DATA_DIR, rel_path)
        Logger.log(("Path: " + path))
        try:
            im = Image.open(path)
        except:
            return None
        size = 50
        image_dimensions = size, size
        im.thumbnail(image_dimensions, Image.ANTIALIAS)
        buffer = io.BytesIO()
        im.save(buffer, format="JPEG")
        encoded_string = base64.b64encode(buffer.getvalue())
        encoded_string = encoded_string.decode('utf-8')
        im.close()
        return encoded_string

    def get_images(self, user, class_name, show, offset, db: Database = None):
        if db is None:
            db = Database()
        param_array = {'limit': show, 'offset': offset}

        if class_name is None or class_name == "-1":
            results = db.select_all(
                "SELECT * FROM "+self.learning_data_table+" WHERE CLASS_ID IS NULL LIMIT :limit OFFSET :offset",
                param_array)
        else:
            param_array['key'] = class_name
            results = db.select_all(
                "SELECT * FROM "+self.learning_data_table+" WHERE CLASS_ID = :key LIMIT :limit OFFSET :offset",
                param_array)

        images = []

        for img in results:
            images.append(img['ID'])

        return images

    def get_class_images(self, user, class_name, show, offset, db: Database = None):
        if db is None:
            db = Database()
        param_array = {'limit': show, 'offset': offset}
        if class_name is None or class_name == "-1" or class_name == -1:
            results = db.select_all(
                "SELECT * FROM "+self.learning_data_table+" WHERE CLASS_ID IS NULL OR CLASS_ID = -1 LIMIT :limit OFFSET :offset",
                param_array)
        else:
            param_array['key'] = class_name
            results = db.select_all(
                "SELECT * FROM "+self.learning_data_table+" WHERE CLASS_ID = :key LIMIT :limit OFFSET :offset",
                param_array)
        images = []
        for img in results:
            images.append(img['ID'])
        return images

    def upload_images(self, user, data, class_name, db: Database = None):
        if db is None:
            db = Database()
        images = json.loads(data)
        counter = 0
        if (class_name == "-1" or class_name == -1):
            img_class = None
        for image in images:
            filename = self.classifier_tag+"-" + str(int(time.time())) + "_" + str(counter)
            counter += 1
            image_path = FileUtils.create_image(filename, "people", image, optimize=True)
            db.insert("INSERT INTO PEOPLE_LEARNING_DATA (PATH, CLASS_ID) VALUES (:path, :class_id)",
                      {'path': image_path, 'class_id': class_name})

    def classify_image(self, user, image_data, db: Database = None):
        if db is None:
            db = Database()
        filename = "person-" + str(int(time.time()))
        image_path = FileUtils.create_image(filename, "people", image_data, optimize=True)
        db.insert("INSERT INTO PEOPLE_LEARNING_DATA (PATH) VALUES (:path)",
                  {'path': image_path})
        predictions = self.classifier.predict(os.path.join(Constants.DATA_DIR, image_path))
        for prediction in predictions:
            person_data = self.get_class_data(prediction['prediction'])
            Logger.log(person_data['NAME'] + ": " + str(prediction['confidence']))
        Logger.log(image_path)
        person_data = self.get_class_data(predictions[0]['prediction'])
        return {'label': person_data['NAME'], 'confidence': str(predictions[0]['confidence'] * 100)}