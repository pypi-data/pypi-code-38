# @Classes
from nlp_model_gen.packages.systemController.SystemController import SystemController

# @Utils
from nlp_model_gen.utils.fileUtils import create_dir_if_not_exist

create_dir_if_not_exist('tmp')
create_dir_if_not_exist('models')

name = "nlp_model_gen"

def NLPModelAdmin():
    return SystemController()
    