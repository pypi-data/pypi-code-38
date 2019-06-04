import yaml
import os

class FaceEmbedderFactory:

    @staticmethod
    def build(settings_file_path):

        with open(settings_file_path) as config_file:
            total_settings = yaml.load(config_file)
            settings = total_settings['face_embedder']

        face_embedder_type = settings['type']
        if face_embedder_type == "movidius_facenet":
            from big_fiubrother_classification.face_embedder_mvds_facenet import FaceEmbedderMovidiusFacenet
            return FaceEmbedderMovidiusFacenet(settings['movidius_id'])
        elif face_embedder_type == "tensorflow_facenet":
            from big_fiubrother_classification.face_embedder_tensorflow_facenet import FaceEmbedderTensorflowFacenet
            return FaceEmbedderTensorflowFacenet()

    @staticmethod
    def build_mvds_facenet():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_mvds_facenet.yaml"
        return FaceEmbedderFactory.build(config_path)

    @staticmethod
    def build_tensorflow_facenet():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_tensorflow_facenet.yaml"
        return FaceEmbedderFactory.build(config_path)