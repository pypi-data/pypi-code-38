from .base_server import BaseServer
from .classification import ClassificationServer
from .detection import DetectionServer
from .segmentation import SegmentationServer

SERVER_DICT = dict()

SERVER_DICT['basic'] = BaseServer
SERVER_DICT['classification'] = ClassificationServer
SERVER_DICT['detection'] = DetectionServer
SERVER_DICT['segmentation'] = SegmentationServer

def register_server(name, override=False):
    def register_func(server_class):
        if not override:
            assert(not name in SERVER_DICT)
        SERVER_DICT[name] = server_class
        return server_class
    return register_func


