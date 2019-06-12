import shutil
from os.path import join, abspath, dirname, exists
from os import listdir, makedirs
from narrative2vec.narrative import Narrative

ABSOULTE_PATH_TO_NARRATIVE_TEST_PARENT_DIR = dirname(abspath(__file__))
NEEM_TEST_FILE_PATH = join(ABSOULTE_PATH_TO_NARRATIVE_TEST_PARENT_DIR, 'test_files', '1559042978791754.owl')
DESTINATION_PATH_DIR = join(ABSOULTE_PATH_TO_NARRATIVE_TEST_PARENT_DIR, 'test_result')


def test_should_read_neem_narrative_file():
    Narrative(NEEM_TEST_FILE_PATH)
    assert True


def test_should_convert_narrative_to_csv_file():
    if exists(DESTINATION_PATH_DIR):
        shutil.rmtree(DESTINATION_PATH_DIR)

    makedirs(DESTINATION_PATH_DIR)

    narrative = Narrative(NEEM_TEST_FILE_PATH)
    narrative.transform_to_csv_file(DESTINATION_PATH_DIR)

    narrative_dir_path  = join(DESTINATION_PATH_DIR, narrative.name)
    test_result_files = listdir(narrative_dir_path)
    assert len(test_result_files) == 3
