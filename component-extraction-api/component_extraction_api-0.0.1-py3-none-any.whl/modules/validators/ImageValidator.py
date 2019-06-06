import logging
from PIL import Image

from runnable_pkg.modules.validators.AbstractValidator import AbstractValidator

class ImageValidator(AbstractValidator):

    def __init__(self):
        logging.basicConfig(filename="cef.log", level=logging.DEBUG)


    @staticmethod
    def is_image_valid(file_path):
        """
        Checks whether the image is the valid by opening it
        :param file_path: the path to the image/file that is checked
        :return: returns whether the image is valid or not
        """
        if ImageValidator.file_exist(file_path):
            try:
                logging.info("Trying to open the image")
                Image.open(ImageValidator.get_filename_from_path(file_path))
            except IOError:
                logging.warning("File is not an image")
            else:
                logging.info("Image is valid")
                return True
        return False

    def validate(self, config):
        """
        Validates the image against the config
        :param config: the config parsed to validate against
        :return: returns whether the image is valid in relation to the config
        """
        is_valid = ImageValidator.is_image_valid(config)
        if is_valid:
            logging.info("File validated correctly")
        else:
            logging.error("Could not validate the file")
        return is_valid
