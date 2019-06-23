import os

from swissarmykit.lib.core import Singleton, Config
from swissarmykit.lib.inspector import Inspector
from swissarmykit.utils.fileutils import FileUtils


@Singleton
class AppConfig(Config, Inspector):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGES_PATH = 'I:/download_images'
    HTML_PATH = 'I:/html'


    # Extend more on your property

appConfig: AppConfig = AppConfig.instance() # Global variable
