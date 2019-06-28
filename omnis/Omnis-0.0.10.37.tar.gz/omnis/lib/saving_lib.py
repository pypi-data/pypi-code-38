import json

from keras.engine import saving
from keras.utils.io_utils import H5Dict

HDF5_OBJECT_HEADER_LIMIT = 64512


def save_models_with_class_indices(model, filepath, include_optimizer=True):
    h5dict = H5Dict(filepath, mode='w')
    h5dict['class_indices'] = json.dumps(model.class_indices)
    try:
        saving._serialize_model(model, h5dict, include_optimizer)
    finally:
        h5dict.close()


def load_models_with_class_indices(filepath, custom_objects=None, compile=True):
    model = None
    h5dict = H5Dict(filepath, 'r')
    try:
        model = saving._deserialize_model(h5dict, custom_objects, compile)
        class_indices_json = h5dict['class_indices']
        model.class_indices = json.loads(class_indices_json)
    finally:
        h5dict.close()

    return model
