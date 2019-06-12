from .keras_callback import KerasCallback
from .pycaffe_callback import PyCaffeCallback
from .pytorch_project import PyTorchProject
from .tensorflow_project import TensorFlowProject
from .sklearn_project import SkLearnProject
from .vanilla_project import VanillaProject

global_root_logger_sniffer = None


def set_global_root_logger_sniffer(global_root_logger_sniffer_):
    global global_root_logger_sniffer

    global_root_logger_sniffer = global_root_logger_sniffer_


def get_global_root_logger_sniffer():
    return global_root_logger_sniffer


__all__ = [
    'KerasCallback', 'PyTorchProject', 'PyCaffeCallback', 'TensorFlowProject', 'SkLearnProject', 'VanillaProject',
    'set_global_root_logger_sniffer']
