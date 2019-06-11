import os
import pickle

dir_path = os.path.abspath(os.path.dirname(__file__))
file_en = "en.pki"
file_en_path = os.path.join(dir_path, file_en)


def model_en():
    model_data = pickle.load(open(file_en_path, "rb"))
    return model_data
