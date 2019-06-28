import sys

sys.path.append('../texterize')
from __init__ import create
from __init__ import createFromFile

TEST_PATH = "./test_files/test_3.txt"
TEST_IMG_PATH = "./test_img/test_2.jpg"
FILE_TYPE = "HTML"
WRITE_PATH = "./output_files/texterize_test"
OVERWRITE = True

createFromFile(TEST_PATH, TEST_IMG_PATH, output_file_type=FILE_TYPE, write_path=WRITE_PATH, overwrite=OVERWRITE)