import click
import pkg_resources
from click_plugins import with_plugins
from bob.extension.scripts.click_helper import AliasedGroup, ConfigCommand, ResourceOption, verbosity_option
import os
import bob.extension
import bob.extension.download
import bob.io.base
import logging
import bob.extension.rc_config

logger = logging.getLogger(__name__)


def get_models():
    """
    Define the models to be downloaded
    """

    class Model(object):

        def __init__(self, group, model_name, url, inside_file_structure):

            module = "bob.bio.face_ongoing."
            self.group       = group
            self.model_name  = model_name
            self.url         = url
            self.config_name = module + group + "-" + model_name
            self.inside_file_structure = inside_file_structure


    # MAKE AS PARAMETERS
    branch = "master"
    base_url = "https://www.idiap.ch/software/bob/data/bob/bob.bio.face_ongoing/"
    extension = ".tar.gz"
    models = []

    groups = ["casia-webface", "msceleb"]

    # Defining the models to be downloaded
    for g in groups:
        model_name = "inception-v1_batchnorm_gray"
        url = os.path.join(base_url, branch, g, model_name + extension)
        #inside_file_structure = os.path.join("inception-v1_batchnorm_gray", "centerloss_alpha-0.90_factor-0.02")
        inside_file_structure = os.path.join("inception-v1_batchnorm_gray")
        models.append(Model(g, model_name, url, inside_file_structure))

        model_name = "inception-v1_batchnorm_rgb"
        url = os.path.join(base_url, branch, g, model_name + extension)
        inside_file_structure = os.path.join("inception-v1_batchnorm_rgb")
        models.append(Model(g, model_name, url, inside_file_structure))

        model_name = "inception-v2_batchnorm_gray"
        url = os.path.join(base_url, branch, g, model_name + extension)
        inside_file_structure = os.path.join("inception-v2_batchnorm_gray")
        models.append(Model(g, model_name, url, inside_file_structure))

        model_name = "inception-v2_batchnorm_rgb"
        url = os.path.join(base_url, branch, g, model_name + extension)
        inside_file_structure = os.path.join("inception-v2_batchnorm_rgb")
        models.append(Model(g, model_name, url, inside_file_structure))

    return models


@click.command()
@click.argument('destination_path', required=True)
@verbosity_option(cls=ResourceOption)
def download_models(destination_path, **kwargs):
    """
    Download pretrained CNN models that is used in the package.

    The models are the following:

       Trained with casia-webface

         - inception-v1-gray: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV1.py

         - inception-v1-rgb: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV1.py

         - inception-v2-gray: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV2.py

         - inception-v2-rgb: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV2.py

       \b
       \b

       Trained with MS-Celeb:

          - inception-v1-gray: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV1.py

         - inception-v1-rgb: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV1.py

         - inception-v2-gray: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV2.py

         - inception-v2-rgb: https://gitlab.idiap.ch/bob/bob.learn.tensorflow/blob/39471f5bb2ae42cf6ef7fcc69e305d76a8b44ff9/bob/learn/tensorflow/network/InceptionResnetV2.py
         
    """
   
    models = get_models()

    # Downloading
    extension = ".tar.gz"
    rc = bob.extension.rc_config._loadrc()
    for m in models:
        output_path = os.path.join(destination_path, m.group, m.model_name + extension)

        # Downloading
        model_path = os.path.join(os.path.dirname(output_path), m.inside_file_structure)
        if os.path.exists(model_path):
            logger.info("Model {0} already exists in {1}".format(m.model_name, output_path))
        else:
            logger.info("Downloading {0} in {1}".format(m.model_name, output_path))
            bob.io.base.create_directories_safe(model_path)
            bob.extension.download.download_and_unzip([m.url], output_path)

        # Setting the path
        rc[m.config_name] = model_path
        bob.extension.rc_config._saverc(rc)

    pass

@click.command()
def check_models():
    """
    Check if all the downloaded models are available
    """

    models = get_models()

    # Downloading
    rc = bob.extension.rc_config._loadrc()
    for m in models:

        if m.config_name in rc:
            print("Found module {0} in {1}".format(m.config_name, rc[m.config_name]))
        else:
            print("Module {0} not found, please download it "
                  "via `bob bio face_ongoing download_models`".format(m.config_name))
 
