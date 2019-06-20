import os
import abc

from os.path import *

class config(abc.ABC):
	BASE_DIR = abspath(os.environ.get("BASE_DIR", "."))

	INFO_FILE = join(BASE_DIR, "info_files", "test_info.yml")
