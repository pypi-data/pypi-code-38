import pathlib
import os

import duplicates
import settings

import test_base


TEST_DIR = ""
PREV_WORKING_DIR = ""


def setup_module(module):
    test_base.setup_module(module)


def setup_function(function):
    global TEST_DIR
    TEST_DIR = test_base.get_test_folder(function.__name__)
    TEST_DIR.mkdir(parents=True)
    global PREV_WORKING_DIR
    PREV_WORKING_DIR = os.getcwd()
    os.chdir(TEST_DIR)
    # Need to change the settings dir or else we might destroy our own config.
    settings.SETTINGS_DIR = pathlib.Path(".picorg")


def teardown_function(function):
    os.chdir(PREV_WORKING_DIR)


def test_find_duplicates_duplicates_folder_not_created_if_no_file_equals():
    pathlib.Path("pic1.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic2.jpg").write_bytes(b"Some different bytes here")

    duplicates.handle_duplicates()

    assert not pathlib.Path("duplicates").exists()


def test_find_duplicates_two_files_same_content_file_with_biggest_name_is_moved():
    pathlib.Path("pic1.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic2.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic3.jpg").write_bytes(b"Some different bytes here")
    pathlib.Path("pic4.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic1 (1).jpg").write_bytes(b"Some bytes here")

    result = duplicates.handle_duplicates()

    assert pathlib.Path("duplicates").is_dir()
    assert pathlib.Path("pic1.jpg").is_file()
    assert pathlib.Path("pic3.jpg").is_file()
    assert pathlib.Path("duplicates", "pic2.jpg").is_file()
    assert pathlib.Path("duplicates", "pic4.jpg").is_file()
    assert pathlib.Path("duplicates", "pic1 (1).jpg").is_file()

    expected = [
        pathlib.Path("duplicates", "pic2.jpg"),
        pathlib.Path("duplicates", "pic4.jpg"),
        pathlib.Path("duplicates", "pic1 (1).jpg"),
    ]
    assert len(result) == len(expected)
    assert sorted(result) == sorted(expected)


# If a file has the same filename and content as one of the files located in pic_paths,
# then the file from current dir is moved to duplicates. We also make sure that
# duplicates are handled in current folder first in case we have three files with
# the same content as:
# pic_lib_1/pic1.jpg
# ./pic1.jpg
# ./pic11.jpg
# Then pic1.jpg and pic11.jpg will be moved. If a file pic2.jpg in pic_lib_1 has
# the same content, it will stay there as there are no matching file from cwd.
def test_find_duplicates_compare_files_to_the_ones_in_pic_paths():
    pathlib.Path("pic_lib_1", "subfolder1").mkdir(parents=True)
    pathlib.Path("pic_lib_1", "subfolder1", "pic1.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic_lib_1", "subfolder1", "pic2.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic1.jpg").write_bytes(b"Some bytes here")
    pathlib.Path("pic11.jpg").write_bytes(b"Some bytes here")

    settings.get("pic_paths", [str(pathlib.Path("pic_lib_1"))])
    result = duplicates.handle_duplicates()

    assert pathlib.Path("pic_lib_1", "subfolder1", "pic1.jpg").is_file()
    assert pathlib.Path("pic_lib_1", "subfolder1", "pic2.jpg").is_file()
    assert pathlib.Path("duplicates", "pic1.jpg").is_file()
    assert pathlib.Path("duplicates", "pic11.jpg").is_file()

    expected = [
        pathlib.Path("duplicates", "pic1.jpg"),
        pathlib.Path("duplicates", "pic11.jpg"),
    ]
    assert len(result) == len(expected)
    assert sorted(result) == sorted(expected)
