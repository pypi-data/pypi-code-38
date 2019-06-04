
class FaceDetectorFactory:

    @staticmethod
    def build(settings):
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