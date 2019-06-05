#!python

import os
import subprocess
import big_fiubrother_classification

module_path = os.path.dirname(big_fiubrother_classification.__file__)
model_path = module_path + "/model"
script_path = model_path + "/prepare_models.sh"

os.chdir(model_path)
subprocess.call(script_path, shell=True)