# code and model from https://github.com/blaueck/tf-mtcnn
import pkg_resources
import tensorflow as tf
import multiprocessing
import bob.io.image


MODEL_PATH = pkg_resources.resource_filename(__name__, "data/mtcnn/mtcnn.pb")


class MTCNN:

    """MTCNN v1 wrapper. See
    https://kpzhang93.github.io/MTCNN_face_detection_alignment/index.html for more
    details on MTCNN and see :ref:`bob.ip.tensorflow_extractor.face_detect` for an
    example code.

    Attributes
    ----------
    factor : float
        Factor is a trade-off between performance and speed.
    min_size : int
        Minimum face size to be detected.
    thresholds : list
        thresholds are a trade-off between false positives and missed detections.
    """

    def __init__(
        self,
        min_size=40,
        factor=0.709,
        thresholds=(0.6, 0.7, 0.7),
        model_path=MODEL_PATH,
    ):
        self.min_size = min_size
        self.factor = factor
        self.thresholds = thresholds

        graph = tf.Graph()
        with graph.as_default():
            with open(model_path, "rb") as f:
                graph_def = tf.GraphDef.FromString(f.read())
                tf.import_graph_def(graph_def, name="")
        self.graph = graph
        config = tf.ConfigProto(
            intra_op_parallelism_threads=multiprocessing.cpu_count(),
            inter_op_parallelism_threads=multiprocessing.cpu_count(),
        )
        self.sess = tf.Session(graph=graph, config=config)

    def detect(self, img):
        """Detects all faces in the image.

        Parameters
        ----------
        img : numpy.ndarray
            An RGB image in Bob format.

        Returns
        -------
        tuple
            A tuple of boxes, probabilities, and landmarks.
        """
        # assuming img is Bob format and RGB
        assert img.shape[0] == 3, img.shape
        # network expects BGR opencv format
        img = bob.io.image.to_matplotlib(img)
        img = img[..., ::-1]
        feeds = {
            self.graph.get_operation_by_name("input").outputs[0]: img,
            self.graph.get_operation_by_name("min_size").outputs[0]: self.min_size,
            self.graph.get_operation_by_name("thresholds").outputs[0]: self.thresholds,
            self.graph.get_operation_by_name("factor").outputs[0]: self.factor,
        }
        fetches = [
            self.graph.get_operation_by_name("prob").outputs[0],
            self.graph.get_operation_by_name("landmarks").outputs[0],
            self.graph.get_operation_by_name("box").outputs[0],
        ]
        prob, landmarks, box = self.sess.run(fetches, feeds)
        return box, prob, landmarks

    def annotations(self, img):
        """Detects all faces in the image

        Parameters
        ----------
        img : numpy.ndarray
            An RGB image in Bob format.

        Returns
        -------
        list
            A list of annotations. Annotations are dictionaries that contain the
            following keys: ``topleft``, ``bottomright``, ``reye``, ``leye``, ``nose``,
            ``mouthright``, ``mouthleft``, and ``quality``.
        """
        boxes, scores, landmarks = self.detect(img)
        annots = []
        for box, prob, lm in zip(boxes, scores, landmarks):
            topleft = box[0], box[1]
            bottomright = box[2], box[3]
            right_eye = lm[0], lm[5]
            left_eye = lm[1], lm[6]
            nose = lm[2], lm[7]
            mouthright = lm[3], lm[8]
            mouthleft = lm[4], lm[9]
            annots.append(
                {
                    "topleft": topleft,
                    "bottomright": bottomright,
                    "reye": right_eye,
                    "leye": left_eye,
                    "nose": nose,
                    "mouthright": mouthright,
                    "mouthleft": mouthleft,
                    "quality": prob,
                }
            )
        return annots

    def __call__(self, img):
        """Wrapper for the annotations method.
        """
        return self.annotations(img)
