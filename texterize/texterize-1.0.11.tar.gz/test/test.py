#to run, call `python3 test/test.py` from the working directory

from texterize.__init__ import create
from texterize.__init__ import createFromFile

TEST_PATH = "./test/test_files/test_1.txt"
TEST_IMG_PATH = "./test/test_img/test_1.png"
FILE_TYPE = "HTML"
WRITE_PATH = "./test/output_files/texterize_test"
OVERWRITE = True

createFromFile(TEST_PATH, TEST_IMG_PATH, output_file_type=FILE_TYPE, write_path=WRITE_PATH, overwrite=OVERWRITE)