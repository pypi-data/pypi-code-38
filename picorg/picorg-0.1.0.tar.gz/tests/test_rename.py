import rename
import shutil
import pathlib

import test_base


TEST_DIR = ""


def setup_module(module):
    test_base.setup_module(module)


def setup_function(function):
    global TEST_DIR
    TEST_DIR = test_base.get_test_folder(function.__name__)
    shutil.copytree("tests/test_data/test_rename_base", TEST_DIR)


def teardown_function(function):
    print("teardown_function")


def test_list_files_is_correct():
    expected = [
        pathlib.Path(TEST_DIR, "pic1.jpg"),
        pathlib.Path(TEST_DIR, "pic2.jpg"),
        pathlib.Path(TEST_DIR, "pic3.jpg"),
        pathlib.Path(TEST_DIR, "pic4.jpg"),
        pathlib.Path(TEST_DIR, "pic7.JPG"),
        pathlib.Path(TEST_DIR, "subfolder1", "pic5.jpg"),
        pathlib.Path(TEST_DIR, "subfolder1", "NOK", "pic6.jpg"),
    ]
    result = rename._list_files(TEST_DIR)
    assert len(result) == len(expected)
    assert sorted(result) == sorted(expected)


def test_do_rename():
    expected = [
        pathlib.Path(TEST_DIR, "20070802_123020.jpg"),  # pic1.jpg
        pathlib.Path(TEST_DIR, "20070802_123020(1).jpg"),  # pic2.jpg
        pathlib.Path(TEST_DIR, "20150704_172516.jpg"),  # pic3.jpg
        pathlib.Path(TEST_DIR, "20070802_123020(2).jpg"),  # pic7.JPG
        pathlib.Path(TEST_DIR, "NOK", "pic4.jpg"),  # pic4.jpg
        pathlib.Path(TEST_DIR, "subfolder1", "20070802_123020.jpg"),  # pic5.jpg
        pathlib.Path(TEST_DIR, "subfolder1", "NOK", "pic6.jpg"),  # pic6.jpg
    ]

    # It should be possible to run the method multiple times on the same path
    # and get the same result every time.
    for _ in range(2):
        rename.rename_files(TEST_DIR)
        result = rename._list_files(TEST_DIR)
        assert len(result) == len(expected)
        assert sorted(result) == sorted(expected)


def test_find_new_filename():
    pathlib.Path(TEST_DIR, "20070802_123020.jpg").touch()
    pathlib.Path(TEST_DIR, "20070802_123020(1).jpg").touch()

    current_file = pathlib.Path(TEST_DIR, "pic1.jpg")
    new_name = rename._find_new_filename(str(current_file), "20070802_123020")

    result = pathlib.Path(new_name)
    assert result.parent == current_file.parent
    assert result.name == "20070802_123020(2).jpg"


def test_find_new_filename_file_aleady_renamed():
    pathlib.Path(TEST_DIR, "20070802_123020.jpg").touch()

    current_file = pathlib.Path(TEST_DIR, "20070802_123020.jpg")
    new_name = rename._find_new_filename(str(current_file), "20070802_123020")

    assert new_name == str(current_file)
