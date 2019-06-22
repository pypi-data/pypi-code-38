from unittest import TestCase
import os
import ntpath
from pathlib import Path
import lolly_helpers


class TestLollyHelpers(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLollyHelpers, self).__init__(*args, **kwargs)
        head, tail = ntpath.split(os.path.realpath(__file__))
        self.TEST_DATA_DIR = head + '/test_data'
        # tmp dir for tests in user's home dir
        home = str(Path.home())
        self.TMP_DIR = home + '/~tmp_test_lollylib'

    def __create_test_dir_if_not_exists(self):
        if not lolly_helpers.dir_exists(self.TMP_DIR):
            lolly_helpers.silent_create_path(self.TMP_DIR)
            # print("* temp test dir was created")
        if not lolly_helpers.dir_exists(self.TMP_DIR):
            raise OSError("Test 'TestLollyhelpers' error: can't create temporary directory '" + self.TMP_DIR + "'")

    def __remove_test_dir(self):
        lolly_helpers.silent_remove_dir(self.TMP_DIR)
        # print("* temp test dir was removed")

    def test___init(self):
        # The tests are executed in alphabetical order, '___' makes this test the first in the execution list
        self.__create_test_dir_if_not_exists()

    def test_file_exists(self):
        # for existing file returns true
        existing_test_file = self.TEST_DATA_DIR + '/lollyhelpers/existing_test_file.txt'
        assert lolly_helpers.file_exists(existing_test_file)

        # for existing dir returns false
        existing_test_dir = self.TEST_DATA_DIR + '/lollyhelpers'
        assert not lolly_helpers.file_exists(existing_test_dir)

        # for non-existing file returns false
        non_existing_file = 'not_exists'
        assert not lolly_helpers.file_exists(non_existing_file)

    def test_dir_exists(self):
        # for existing dir returns true
        existing_test_dir = self.TEST_DATA_DIR + '/lollyhelpers'
        assert lolly_helpers.dir_exists(existing_test_dir)

        # for existing file returns false
        existing_test_file = self.TEST_DATA_DIR + '/lollyhelpers/existing_test_file.txt'
        assert not lolly_helpers.dir_exists(existing_test_file)

    def test_path_base_and_leaf(self):
        path = '/a/b'
        result = lolly_helpers.path_base_and_leaf(path)
        assert result == {'base': '/a', 'leaf': 'b'}

        path = '/a/'
        result = lolly_helpers.path_base_and_leaf(path)
        assert result == {'base': '/', 'leaf': 'a'}

        path = '../a/b/some other dir/'
        result = lolly_helpers.path_base_and_leaf(path)
        assert result == {'base': '../a/b', 'leaf': 'some other dir'}

        path = './dir1/dir2/file.txt'
        result = lolly_helpers.path_base_and_leaf(path)
        assert result == {'base': './dir1/dir2', 'leaf': 'file.txt'}

    def test_silent_write_text_file(self):
        self.__create_test_dir_if_not_exists()
        path = self.TMP_DIR + '/' + 'silent_write_text_file.txt'

        # Check file not yet exists
        if lolly_helpers.file_exists(path):
            lolly_helpers.silent_remove_file(path)
        contents = 'TEST'
        assert not lolly_helpers.silent_write_text_file(path, contents)['error']
        assert lolly_helpers.file_exists(path)
        data = lolly_helpers.silent_read_text_file(path)
        assert data['contents'] == contents

        # Check that existing file is rewritten
        contents = 'YET ANOTHER CONTENTS'
        assert not lolly_helpers.silent_write_text_file(path, contents)['error']
        assert lolly_helpers.file_exists(path)
        data = lolly_helpers.silent_read_text_file(path)
        assert data['contents'] == contents

    def test_silent_create_path(self):
        # sad path can't be easily tested because python replaces illegal characters in file names with legal
        # some_wrong_path = self.TMP_DIR + "/:::"
        # assert lollyhelpers.silent_create_path(some_wrong_path)['error']

        # happy path
        path = self.TMP_DIR + '/some/test/directory'
        assert not lolly_helpers.silent_create_path(path)['error']
        assert lolly_helpers.dir_exists(path)
        # create a file inside that directory
        filepath = path + '/testfile.txt'
        lolly_helpers.silent_write_text_file(filepath, 'TEST')

    def test_silent_remove_file(self):
        self.__create_test_dir_if_not_exists()
        # sad path can't be easily tested

        # happy path
        non_existent_file = self.TMP_DIR + '/non_existent.txt'
        assert not lolly_helpers.silent_remove_file(non_existent_file)['error']
        existent_file = self.TMP_DIR + '/existent.txt'
        assert not lolly_helpers.silent_write_text_file(existent_file, 'TEST')['error']
        assert lolly_helpers.file_exists(existent_file)
        assert not lolly_helpers.silent_remove_file(existent_file)['error']
        assert not lolly_helpers.file_exists(existent_file)

    def test_silent_remove_dir(self):
        self.__create_test_dir_if_not_exists()
        # sad path can't be easily tested

        # happy path
        non_existent_dir = self.TMP_DIR + '/non_existent_dir'
        assert not lolly_helpers.silent_remove_dir(non_existent_dir)['error']
        existent_dir = self.TMP_DIR + '/existent'
        lolly_helpers.silent_create_path(existent_dir)
        assert lolly_helpers.dir_exists(existent_dir)
        assert not lolly_helpers.silent_remove_dir(existent_dir)['error']
        assert not lolly_helpers.dir_exists(existent_dir)

    def test_silent_copy_file(self):
        self.__create_test_dir_if_not_exists()
        dest = self.TMP_DIR + '/copied.txt'
        # sad path
        bad_origin = self.TMP_DIR + '/non_existent.txt'
        assert lolly_helpers.silent_copy_file(bad_origin, dest)['error']
        # happy path
        origin = self.TMP_DIR + '/copy_origin.txt'
        msg = 'copy_file_test'
        lolly_helpers.silent_write_text_file(origin, msg)
        assert not lolly_helpers.silent_copy_file(origin, dest)['error']
        assert lolly_helpers.silent_read_text_file(dest)['contents'] == msg

    def test_silent_move_file(self):
        self.__create_test_dir_if_not_exists()
        dest = self.TMP_DIR + '/moved.txt'
        # sad path
        bad_origin = self.TMP_DIR + '/non_existent.txt'
        assert lolly_helpers.silent_move_file(bad_origin, dest)['error']
        # happy path
        origin = self.TMP_DIR + '/move_origin.txt'
        msg = 'move_file_test'
        lolly_helpers.silent_write_text_file(origin, msg)
        assert not lolly_helpers.silent_move_file(origin, dest)['error']
        assert not lolly_helpers.file_exists(origin)
        assert lolly_helpers.silent_read_text_file(dest)['contents'] == msg

    def test_silent_copy_dir(self):
        self.__create_test_dir_if_not_exists()
        dest = self.TMP_DIR + '/copied'
        # sad path
        bad_origin = self.TMP_DIR + '/non_existent'
        assert lolly_helpers.silent_copy_dir(bad_origin, dest)['error']
        # happy path
        origin = self.TMP_DIR + '/copy_origin'
        lolly_helpers.silent_create_path(origin)
        assert not lolly_helpers.silent_copy_dir(origin, dest)['error']
        assert lolly_helpers.dir_exists(origin)
        assert lolly_helpers.dir_exists(dest)

    def test_silent_move_dir(self):
        self.__create_test_dir_if_not_exists()
        dest = self.TMP_DIR + '/moved'
        # sad path
        bad_origin = self.TMP_DIR + '/non_existent'
        assert lolly_helpers.silent_move_dir(bad_origin, dest)['error']
        # happy path
        origin = self.TMP_DIR + '/move_origin'
        lolly_helpers.silent_create_path(origin)
        assert not lolly_helpers.silent_move_dir(origin, dest)['error']
        assert not lolly_helpers.dir_exists(origin)
        assert lolly_helpers.dir_exists(dest)

    def test_get_subdirs(self):
        self.__create_test_dir_if_not_exists()
        base_dir = self.TMP_DIR + '/subdirs_test'
        lolly_helpers.silent_create_path(base_dir)
        dir_names = ['one', 'two', 'three']
        dir_names.sort()
        for name in dir_names:
            lolly_helpers.silent_create_path(base_dir + '/' + name)
        result = lolly_helpers.get_subdirs(base_dir)
        sorted_subdirs = sorted(result['subdirs'])
        assert not result['error']
        assert sorted_subdirs == dir_names

    def test_get_file_list(self):
        self.__create_test_dir_if_not_exists()
        base_dir = self.TMP_DIR + '/file_list_test'
        lolly_helpers.silent_create_path(base_dir)
        file_names = ['one', 'two', 'three']
        file_names = sorted(file_names)
        for name in file_names:
            lolly_helpers.silent_write_text_file(base_dir + '/' + name, name)
        result = lolly_helpers.get_file_list(base_dir)
        sorted_result = sorted(result['files'])
        assert not result['error']
        assert sorted_result == file_names

    def test_get_dir_item_count(self):
        self.__create_test_dir_if_not_exists()
        base_dir = self.TMP_DIR + '/item_count'
        lolly_helpers.silent_create_path(base_dir, overwrite=True)
        assert lolly_helpers.get_dir_item_count(base_dir)['count'] == 0
        file_names = ['one.txt', 'two.txt', 'three.txt']
        file_names = sorted(file_names)
        for name in file_names:
            lolly_helpers.silent_write_text_file(base_dir + '/' + name, name)
        assert lolly_helpers.get_dir_item_count(base_dir)['count'] == 3

        dir_names = ['one', 'two', 'three']
        dir_names = sorted(dir_names)
        for name in dir_names:
            lolly_helpers.silent_create_path(base_dir + '/' + name)
        assert lolly_helpers.get_dir_item_count(base_dir)['count'] == 6

    def test_dir_empty(self):
        self.__create_test_dir_if_not_exists()
        base_dir = self.TMP_DIR + '/empty_dir_test'
        lolly_helpers.silent_create_path(base_dir, overwrite=True)
        assert lolly_helpers.dir_empty(base_dir)
        lolly_helpers.silent_write_text_file(base_dir + '/test.txt', 'test')
        assert not lolly_helpers.dir_empty(base_dir)

    def test_get_filesystem_item_properties(self):
        self.__create_test_dir_if_not_exists()
        base_dir = self.TMP_DIR + '/item_props'
        lolly_helpers.silent_create_path(base_dir, overwrite=True)
        assert lolly_helpers.get_filesystem_item_type(base_dir)['type'] == 'dir'
        assert not lolly_helpers.get_filesystem_item_type('dummy_non_existent_path')['type']

    # -----------------------------------------------------------------------------------------------------------------
    # Strings

    def test_substr_enclosed_in_seq(self):
        data = 'hello'
        initial_seq = ''
        terminal_seq = ''
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq)
        assert result['value'] == ''
        assert result['start'] == 0
        assert result['end'] == 0
        assert result['error'] == ''

        data = '[##hello##]'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq)
        # print("* Result: ", result)
        assert result == {'value': 'hello', 'start': 0, 'end': 11, 'error': ''}

        data = '[##one##] [##two##]'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 9)
        assert result == {'value': 'two', 'start': 10, 'end': 19, 'error': ''}

        # test trailing new line inclusion
        data = '[##A##]\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 8, 'error': ''}

        data = '[##A##]\r'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 8, 'error': ''}

        data = '[##A##]\r\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 9, 'error': ''}

        data = '[##A##]\n\r\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 9, 'error': ''}

        data = '[##A##]\r\r\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 8, 'error': ''}

        data = '[##A##]\n\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.substr_enclosed_in_seq(data, initial_seq, terminal_seq, 0, -1, True)
        assert result == {'value': 'A', 'start': 0, 'end': 8, 'error': ''}

    def test_extract_substr_enclosed_in_seq(self):
        data = 'hello'
        initial_seq = ''
        terminal_seq = ''
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq)
        assert result == {'extracted': '', 'remainder': 'hello', 'error': ''}

        data = '[##hello##]'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq)
        assert result == {'extracted': 'hello', 'remainder': '', 'error': ''}

        data = '[##one##] [##two##]'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=10,
                                                              to_index=len(data))
        assert result == {'extracted': 'two', 'remainder': '[##one##] ', 'error': ''}

        # test trailing new line inclusion
        data = '[##A##]\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '', 'error': ''}

        data = '[##A##]\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=False)
        assert result == {'extracted': 'A', 'remainder': '\n', 'error': ''}

        data = '[##A##]\r'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '', 'error': ''}

        data = '[##A##]\r\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '\r\n', 'error': ''}

        data = '[##A##]\n\r\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '\n\r\n', 'error': ''}

        data = '[##A##]\r\r\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '\r\r\n', 'error': ''}

        data = '[##A##]\n\n\r\n'
        initial_seq = '[##'
        terminal_seq = '##]'
        result = lolly_helpers.extract_substr_enclosed_in_seq(data, initial_seq, terminal_seq, from_index=0,
                                                              to_index=-1, include_trailing_newline=True)
        assert result == {'extracted': 'A', 'remainder': '\n\r\n', 'error': ''}

    def test_strip_quotes(self):
        data = 'test'
        result = lolly_helpers.strip_quotes(data)
        assert result == {'value': 'test', 'error': ''}

        data = '"test " '
        result = lolly_helpers.strip_quotes(data)
        assert result == {'value': 'test ', 'error': ''}

        data = "'test ' "
        result = lolly_helpers.strip_quotes(data)
        assert result == {'value': 'test ', 'error': ''}

        # sad path
        data = "'test  "  # omitted closing quote
        result = lolly_helpers.strip_quotes(data)
        assert result == {'value': '', 'error': 'syntax'}

        data = '"test  '  # omitted closing double quote
        result = lolly_helpers.strip_quotes(data)
        assert result == {'value': '', 'error': 'syntax'}

    def test_parse_assignment(self):
        data = "a = 3"
        result = lolly_helpers.parse_assignment(data)
        assert result == {'name': 'a', 'value': '3', 'error': ''}

        data = "a = 3 5 "
        result = lolly_helpers.parse_assignment(data)
        assert result == {'name': 'a', 'value': '3 5', 'error': ''}

        data = "a='3 5 '"
        result = lolly_helpers.parse_assignment(data)
        assert result == {'name': 'a', 'value': '3 5 ', 'error': ''}

        data = 'a="3 5 "'
        result = lolly_helpers.parse_assignment(data)
        assert result == {'name': 'a', 'value': '3 5 ', 'error': ''}

        # sad path - assign symbol not found
        data = 'a "3 5 "'
        result = lolly_helpers.parse_assignment(data)
        assert result == {'name': '', 'value': '', 'error': 'syntax'}

    def test_strip_whitespaces_in_list(self):
        strlist = [' a ', 'b ', '    c', 'd']
        result = lolly_helpers.strip_whitespaces_in_list(strlist)
        assert result == ['a', 'b', 'c', 'd']

    def test_remove_empty_lines_from_list(self):
        strlist = ['', '', ' a ', 'b ', '', ' c', 'd']
        result = lolly_helpers.remove_empty_lines_from_list(strlist)
        assert result == [' a ', 'b ', ' c', 'd']

    def test_remove_closed_range_from_list(self):
        the_list = [1, 2, 3, 4]
        result = lolly_helpers.remove_closed_range_from_list(the_list, 1, 2)
        assert result == [1, 4]

    def test_open_range_sublist(self):
        the_list = [1, 2, 3, 4]
        result = lolly_helpers.open_range_sublist(the_list, 0, 1)
        assert result == [1]

        result = lolly_helpers.open_range_sublist(the_list, 0, -1)
        assert result == [1, 2, 3, 4]

        result = lolly_helpers.open_range_sublist(the_list, 1, 1)
        assert result == []

        result = lolly_helpers.open_range_sublist(the_list, 1, 3)
        assert result == [2, 3]

    def test_split_line_into_cmd_and_args(self):
        line = "mycmd first_arg second_arg"
        result = lolly_helpers.split_line_into_cmd_and_args(line)
        assert result == {'cmd': 'mycmd', 'args': ['first_arg', 'second_arg'], 'error': ''}

        line = "mycmd 'first arg' 'second arg' "
        result = lolly_helpers.split_line_into_cmd_and_args(line)
        assert result == {'cmd': 'mycmd', 'args': ['first arg', 'second arg'], 'error': ''}

        line = 'mycmd "long/first/arg" second_arg    '
        result = lolly_helpers.split_line_into_cmd_and_args(line)
        assert result == {'cmd': 'mycmd', 'args': ['long/first/arg', 'second_arg'], 'error': ''}

        # sad path
        line = 'mycmd "long/first/arg" "second_arg'
        result = lolly_helpers.split_line_into_cmd_and_args(line)
        assert result['error'] == 'syntax'

    def test_extract_first_word(self):
        line = ''
        extracted = lolly_helpers.extract_first_word(line)
        assert extracted == {'value': '', 'remainder': '', 'error': ''}

        line = '               '
        extracted = lolly_helpers.extract_first_word(line)

        assert extracted == {'value': '', 'remainder': '', 'error': ''}

        line = ' one two three '
        extracted = lolly_helpers.extract_first_word(line)
        assert extracted == {'value': 'one', 'remainder': 'two three ', 'error': ''}

        # line = '  " one" two three '
        # extracted = lollyhelpers.extract_first_word(line)
        # print("* extracted:", extracted)
        # assert extracted == {'value': ' one', 'remainder': 'two three ', 'error': ''}

    def test_extract_first_value_in_quotes(self):
        line = ''
        extracted = lolly_helpers.extract_first_value_in_quotes(line, "'")
        assert extracted == {'value': '', 'remainder': '', 'error': 'syntax'}

        line = '"'
        extracted = lolly_helpers.extract_first_value_in_quotes(line, '"')
        assert extracted == {'value': '', 'remainder': '"', 'error': 'syntax'}

        line = ' " " '
        extracted = lolly_helpers.extract_first_value_in_quotes(line, '"')
        assert extracted == {'value': ' ', 'remainder': ' ', 'error': ''}

        line = ' "first""second" '
        extracted = lolly_helpers.extract_first_value_in_quotes(line, '"')
        assert extracted == {'value': 'first', 'remainder': '"second" ', 'error': ''}

    def test_remove_selected_from_list(self):
        the_list = [1, 2, 3, 4]
        indexes = [0]
        result = lolly_helpers.remove_selected_from_list(the_list, indexes)
        assert result == [2, 3, 4]

        indexes = [0, 3]
        result = lolly_helpers.remove_selected_from_list(the_list, indexes)
        assert result == [2, 3]

    def test_replace_keys(self):
        the_string = 'Hello, this is a test'
        the_dict = {'this': 'that', ' is ': ' was '}
        result = lolly_helpers.replace_keys(the_string, the_dict)
        assert result == 'Hello, that was a test'

    def test_find_line_starting_with_seq(self):
        the_list = ['one', 'two', 'smallfoot']
        # happy path
        result = lolly_helpers.find_line_starting_with_seq(the_list, 'sm')
        assert result == 2

        # sad path
        result = lolly_helpers.find_line_starting_with_seq(the_list, 'NOT_EXISTS')
        assert result == -1

    def test_replace_in_string_list(self):
        the_list = ['one', 'two', 'smallfoot']
        the_dict = {'small': 'big', 'one': 'first', 'two': 'second'}
        result = lolly_helpers.replace_in_string_list(the_list, the_dict)
        assert result == ['first', 'second', 'bigfoot']

    def test_current_year_utc(self):
        year = lolly_helpers.current_year_utc()
        assert len(year) == 4
        assert year[0] == '2' and year[1] == '0'

    def test_current_date_utc(self):
        the_date = lolly_helpers.current_date_utc()
        assert len(the_date) > 5
        assert the_date[0] == '2' and the_date[1] == '0'

    def test_current_datetime_utc(self):
        the_dtime = lolly_helpers.current_datetime_utc()
        assert the_dtime[0] == '2' and the_dtime[1] == '0'
        assert the_dtime.find('+') != -1  # plus sign for time zone

    def test_current_time_utc(self):
        lolly_helpers.current_time_utc()


    def test_zzz_cleanup(self):
        # Tests are executed in alphabetical order, 'zzz' makes it the last in the execution list
            self.__remove_test_dir()

