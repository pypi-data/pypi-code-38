import yaml
import os

class FaceDetectorFactory:

    @staticmethod
    def build(settings_file_path):

        with open(settings_file_path) as config_file:
            total_settings = yaml.load(config_file)
            settings = total_settings['face_detector']

        face_detector_type = settings['type']
        if face_detector_type == "caffe_mtcnn":
            from big_fiubrother_detection.face_detector_caffe_mtcnn import FaceDetectorCaffeMTCNN
            return FaceDetectorCaffeMTCNN()
        elif face_detector_type == "movidius_mtcnn":
            from big_fiubrother_detection.face_detector_movidius_mtcnn import FaceDetectorMovidiusMTCNN
            return FaceDetectorMovidiusMTCNN(settings['movidius_id_pnet'], settings['movidius_id_onet'])
        elif face_detector_type == "movidius_ssd":
            from big_fiubrother_detection.face_detector_movidius_ssd import FaceDetectorMovidiusSSD
            return FaceDetectorMovidiusSSD(settings['movidius_id'], settings['longrange'])

    @staticmethod
    def build_movidius_ssd():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_mvds_ssd.yaml"
        return FaceDetectorFactory.build(config_path)

    @staticmethod
    def build_movidius_ssd_longrange():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_mvds_ssd_longrange.yaml"
        return FaceDetectorFactory.build(config_path)

    @staticmethod
    def build_movidius_mtcnn():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_mvds_mtcnn.yaml"
        return FaceDetectorFactory.build(config_path)

    @staticmethod
    def build_caffe_mtcnn():
        config_path = os.path.dirname(os.path.realpath(__file__)) + "/config/config_caffe_mtcnn.yaml"
        return FaceDetectorFactory.build(config_path)