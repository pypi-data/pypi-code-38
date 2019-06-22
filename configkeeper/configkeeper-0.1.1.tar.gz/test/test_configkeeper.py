#  Imports
import pytest
import json
from os import path
import tempfile

from configkeeper import configkeeper

#  Constants
DATA_DIR = path.join(path.dirname(__file__), 'data')


@pytest.fixture
def path_json_path():
    return path.join(DATA_DIR, 'path.json')

@pytest.fixture
def path_json():
    with open(path.join(DATA_DIR, 'path.json'), 'r') as handle:
        path_json = json.load(handle)
    return path_json

@pytest.fixture
def temp_file():
    return tempfile.mkstemp()[1]


class TestConfigkeeper(object):

    @classmethod
    def setup_class(cls):
        cls.fake_repo = tempfile.TemporaryDirectory()
        cls.file = tempfile.NamedTemporaryFile(dir=cls.fake_repo.name, suffix='.txt')
        cls.file_name = cls.file.name.split('/')[-1]
        cls.args = {'filename': cls.file.name, 'dir': 'nest_dir'}
        cls.env = configkeeper.Environment(cls.fake_repo.name, **cls.args)
        cls.env.repo_dir = cls.fake_repo.name
        cls.env.index_path = path.join(DATA_DIR, 'path.json')
        cls.env.user = 'testuser_1'
        cls.env.host = 'testhost_1'

    def test_environment_is_created_correctly(self):
        assert self.env.full_file_path == path.join(self.fake_repo.name, self.file_name)
        assert self.env.filename == self.file_name
        assert self.env.destination_dir == path.join(self.fake_repo.name,
                                                     'testuser_1@testhost_1')

    def test_silent_create_leaves_existing_file_unchanged(self):
        self.file.write(b'This is a testfile')
        configkeeper.silent_create(self.file.name)
        self.file.seek(0)
        assert self.file.read() == b'This is a testfile'

    def test_silent_create_creates_file_if_not_found(self):
        file_name = self.file.name
        self.file.close()
        assert not path.exists(file_name)
        configkeeper.silent_create(file_name)
        assert path.exists(file_name)

    def test_silent_remove_file_with_file(self, temp_file):
        assert path.isfile(temp_file) is True
        configkeeper.silent_remove(temp_file)
        assert path.exists(temp_file) is False

    def test_silent_remove_file_if_not_found(self):
        not_a_file = 'not/a/path/test.txt'
        assert path.isfile(not_a_file) is False
        configkeeper.silent_remove(not_a_file)
        assert path.exists(not_a_file) is False

    def test_copy_directory(self, temp_file):
        source_dir = tempfile.TemporaryDirectory(prefix='source__')
        nested_dir = tempfile.TemporaryDirectory(dir=source_dir.name, prefix='moved__')
        dest_dir = tempfile.TemporaryDirectory(prefix='dest__')
        nested_dir_name = nested_dir.name.split('/')[-1]
        assert path.exists(path.join(source_dir.name, nested_dir_name))
        assert not path.exists(path.join(dest_dir.name, nested_dir_name))
        configkeeper.copy_dir(nested_dir.name, dest_dir.name)
        assert path.exists(path.join(dest_dir.name, nested_dir_name))

    def test_insert_path_with_host_and_user_found(self, path_json):
        fp = '/home/testuser_1/.pystartup'
        configkeeper.insert_path_into_path_json(self.env.user, self.env.host,
                                                fp, path_json)
        assert path_json['testuser_1@testhost_1']['.pystartup'] == fp

    def test_insert_path_with_new_user(self, path_json):
        fp = '/home/testuser_1/.pystartup'
        configkeeper.insert_path_into_path_json('new_user', self.env.host, fp, path_json)
        assert path_json['new_user@testhost_1']['.pystartup'] == fp

    def test_insert_path_with_new_host(self, path_json):
        fp = '/home/testuser_1/.pystartup'
        configkeeper.insert_path_into_path_json(self.env.user, 'new_host', fp, path_json)
        assert path_json['testuser_1@new_host']['.pystartup'] == fp

    def test_insert_path_appends_path(self, path_json):
        fp = '/home/testuser_1/.pystartup'
        number_of_items = len(path_json['testuser_1@testhost_1'])
        configkeeper.insert_path_into_path_json(self.env.user, self.env.host,
                                                fp, path_json)
        assert len(path_json['testuser_1@testhost_1']) == number_of_items + 1

    def test_path_is_split_into_object(self):
        fp = '/home/testuser_1/.pystartup'
        assert configkeeper.path_to_object(fp) == ('.pystartup',
                                                   '/home/testuser_1/.pystartup')

    def test_retrieve_or_create_index_file_with_index_found(self, path_json):
        index = configkeeper.retrieve_or_create_index_file(self.env.index_path)
        assert index == path_json

    def test_retrieve_or_create_index_file_with_incorrect_index_found(self, path_json):
        self.env.index_path = self.fake_repo.name
        index = configkeeper.retrieve_or_create_index_file(self.env.index_path)
        assert index == {}
        assert path.exists(path.join(self.fake_repo.name, 'index.json'))

    @classmethod
    def teardown_class(cls):
        cls.file.close()
        cls.fake_repo.cleanup()
