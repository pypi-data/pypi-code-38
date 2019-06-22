from unittest import TestCase
import os
import ntpath
from pathlib import Path
from lolly_wiz import LollyWiz
import lolly_helpers


class TestLollyWiz(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLollyWiz, self).__init__(*args, **kwargs)
        head, tail = ntpath.split(os.path.realpath(__file__))
        self.TEST_DATA_DIR = head + '/test_data'
        # get name of tmp dir for tests in user's home dir
        home = str(Path.home())
        self.TMP_DIR = home + '/~tmp_test_lollylib'

    def __create_test_dir_if_not_exists(self):
        if not lolly_helpers.dir_exists(self.TMP_DIR):
            lolly_helpers.silent_create_path(self.TMP_DIR)
            # print("* temp test dir was created")
        if not lolly_helpers.dir_exists(self.TMP_DIR):
            raise OSError("'TestLollyWiz' error: can't create temporary directory '" + self.TMP_DIR + "'")

    def __remove_test_dir(self):
        lolly_helpers.silent_remove_dir(self.TMP_DIR)
        # print("* temp test dir was removed")

    def test___init(self):
        # The tests are executed in alphabetical order, '___' makes it the first in the list
        print("***** Starting lolly_wiz tests. This will produce some expected "
              "error messages, please don't worry...")
        self.__create_test_dir_if_not_exists()

    def test_comments_removal(self):
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)
        wiz._instr_file_full_path = 'dummy_test_data (expected error)'

        # happy path
        data = "/*test*/"
        assert wiz._remove_comments(data) == ''

        data = "/*test1*/data /*test2*/"
        assert wiz._remove_comments(data) == 'data '

        # sad path
        data = "/*test"
        assert wiz._remove_comments(data) == ''
        assert wiz.error == 'syntax'

        data = "/*test /*data*/"
        assert wiz._remove_comments(data) == ''
        assert wiz.error == 'syntax'

    def test_condition_processing(self):
        # self.__create_test_dir_if_not_exists()
        src_dir = self.TEST_DATA_DIR + '/lollywiz/condition_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)
        wiz._instr_file_full_path = 'dummy_test_data (expected error)'

        # happy path --------------------------------------------------
        # test case 1: if/endif pair
        data = "start.[##if cond1##]val1[##endif##].end"
        result = wiz._process_conditional_directives(data, 'test_data_1')
        assert not wiz.error and result == "start..end"

        wiz.set_definitions(['cond1'])
        result = wiz._process_conditional_directives(data, 'test_data_1')
        assert not wiz.error and result == "start.val1.end"

        # test case 2: if/else/endif
        data = "start.[##if cond1##]val1[##else##]else_val[##endif##].end"
        wiz.set_definitions([])
        result = wiz._process_conditional_directives(data, 'test_data_2')
        assert not wiz.error and result == "start.else_val.end"

        wiz.set_definitions(['cond1'])
        result = wiz._process_conditional_directives(data, 'test_data_2')
        assert not wiz.error and result == "start.val1.end"

        # test case 3: if/elif/endif
        data = "start.[##if cond1##]val1[##elif cond2##]val2[##elif cond3##]val3[##endif##].end"
        wiz.set_definitions([])
        result = wiz._process_conditional_directives(data, 'test_data_3')
        assert not wiz.error and result == "start..end"

        wiz.set_definitions(['cond1'])
        result = wiz._process_conditional_directives(data, 'test_data_3')
        assert not wiz.error and result == "start.val1.end"

        wiz.set_definitions(['cond2', 'cond3'])
        result = wiz._process_conditional_directives(data, 'test_data_3')
        assert not wiz.error and result == "start.val2.end"

        wiz.set_definitions(['cond3'])
        result = wiz._process_conditional_directives(data, 'test_data_3')
        assert not wiz.error and result == "start.val3.end"

        # test case 4: if/elif/else/endif
        data = "start.[##if cond1##]val1[##elif cond2##]val2[##elif cond3##]val3[##else##]else_val[##endif##].end"
        wiz.set_definitions([])
        result = wiz._process_conditional_directives(data, 'test_data_4')
        assert not wiz.error and result == "start.else_val.end"

        wiz.set_definitions(['cond1'])
        result = wiz._process_conditional_directives(data, 'test_data_4')
        assert not wiz.error and result == "start.val1.end"

        wiz.set_definitions(['cond2'])
        result = wiz._process_conditional_directives(data, 'test_data_4')
        assert not wiz.error and result == "start.val2.end"

        wiz.set_definitions(['cond2', 'cond3'])
        result = wiz._process_conditional_directives(data, 'test_data_4')
        assert not wiz.error and result == "start.val2.end"

        wiz.set_definitions(['cond3'])
        result = wiz._process_conditional_directives(data, 'test_data_4')
        assert not wiz.error and result == "start.val3.end"

        # test case 5: trailing new line removal
        data = "start.\n[##if cond1##]val1[##endif##]\n.end"
        result = wiz._process_conditional_directives(data, 'test_data_1')
        assert not wiz.error and result == "start.\n.end"

        data = "start.\r[##if cond1##]val1[##endif##]\r\n.end"
        result = wiz._process_conditional_directives(data, 'test_data_1')
        assert not wiz.error and result == "start.\r.end"

        # test case 6: real life file processing
        wiz.set_definitions(['SHOW_BRIEF_COMMENT'])
        file1 = src_dir + '/cond_template1.hpp'
        data = lolly_helpers.silent_read_text_file(file1)['contents']
        result = wiz._process_conditional_directives(data, file1)
        assert not wiz.error
        file1_verify = src_dir + '/cond_result1.hpp'
        verification = lolly_helpers.silent_read_text_file(file1_verify)['contents']
        assert result == verification

        # sad path --------------------------------------------------

    def test_check_version(self):
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR + '/generic_tests'
        wiz = LollyWiz(src_dir, dest_dir)
        wiz._instr_file_full_path = 'dummy_test_data (expected error)'

        # sad path
        # does not contain LOLLYWIZ_TEXTFILE_VERSION
        str_list = ["this", "test"]
        wiz._check_version(str_list)
        assert wiz.error == 'version'

        # LOLLYWIZ_TEXTFILE_VERSION is greater, software is outdated
        str_list = ["LOLLYWIZ_TEXTFILE_VERSION = 1.1.0", "test"]
        wiz._check_version(str_list)
        assert wiz.error == 'version'

        # LOLLYWIZ_TEXTFILE_VERSION has no value
        str_list = ["LOLLYWIZ_TEXTFILE_VERSION = ", "test"]
        wiz._check_version(str_list)
        assert wiz.error == 'version'

        # LOLLYWIZ_TEXTFILE_VERSION has no value
        str_list = ["LOLLYWIZ_TEXTFILE_VERSION", "test"]
        wiz._check_version(str_list)
        assert wiz.error == 'version'

        str_list = ["LOLLYWIZ_TEXTFILE_VERSION = 0", "test"]
        wiz._check_version(str_list)
        assert wiz.error == 'version'

        # happy path
        str_list = ["test", "LOLLYWIZ_TEXTFILE_VERSION = 0.0.24"]
        result = wiz._check_version(str_list)
        assert not wiz.error and result == ['test']

        wiz.VERSION = '0.1.2'
        str_list = ["test", "LOLLYWIZ_TEXTFILE_VERSION = 0.1.2-a"]
        result = wiz._check_version(str_list)
        assert not wiz.error
        assert result == ['test']

    def test_common_replacements(self):
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)
        wiz._instr_file_full_path = 'dummy_test_data (expected error)'

        # override original instruction file with test data
        wiz._is_instr_file_read = True
        wiz._instr_file_data = "LOLLYWIZ_TEXTFILE_VERSION = 0.1.0\n[$$__YEAR__$$]"
        wiz._parse_instructions()
        # assert year placeholder is replaced correctly
        assert wiz._instr_file_data[0][0] == '2' and wiz._instr_file_data[0][1] == '0'

    def test_execute_copy(self):
        self.__create_test_dir_if_not_exists()
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)

        wiz._instr_file_full_path = 'dummy_test_data'
        # override original instruction file with test data
        wiz._is_instr_file_read = True
        wiz._instr_file_data = "LOLLYWIZ_TEXTFILE_VERSION = 0.1.0\n" \
                               "#instructions_begin\n" \
                               "copy 'test_dir' 'dest_test_dir'\n" \
                               "#instructions_end\n"
        wiz.instantiate()
        assert lolly_helpers.dir_exists(dest_dir + '/dest_test_dir')
        assert lolly_helpers.file_exists(dest_dir + '/dest_test_dir/test.txt')
        lolly_helpers.silent_remove_dir(dest_dir + '/dest_test_dir')

    def test_execute_mkdir(self):
        self.__create_test_dir_if_not_exists()
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)

        test_dir = dest_dir + '/test_dir'
        # lolly_helpers.silent_create_path(test_dir)
        lolly_helpers.silent_remove_dir(test_dir)
        assert not lolly_helpers.dir_exists(test_dir)

        wiz._instr_file_full_path = 'dummy_test_data'
        # override original instruction file with test data
        wiz._is_instr_file_read = True
        wiz._instr_file_data = "LOLLYWIZ_TEXTFILE_VERSION = 0.1.0\n" \
                               "#instructions_begin\n" \
                               "mkdir 'test_dir'\n" \
                               "#instructions_end\n"
        wiz.instantiate()
        assert lolly_helpers.dir_exists(test_dir)
        lolly_helpers.silent_remove_dir(test_dir)

    def test_execute_remove(self):
        self.__create_test_dir_if_not_exists()
        src_dir = self.TEST_DATA_DIR + '/lollywiz/generic_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)

        test_dir = dest_dir + '/test_dir'
        lolly_helpers.silent_create_path(test_dir)
        assert lolly_helpers.dir_exists(test_dir)

        wiz._instr_file_full_path = 'dummy_test_data'
        # override original instruction file with test data
        wiz._is_instr_file_read = True
        wiz._instr_file_data = "LOLLYWIZ_TEXTFILE_VERSION = 0.1.0\n" \
                               "#instructions_begin\n" \
                               "remove 'test_dir'\n" \
                               "#instructions_end\n"
        wiz.instantiate()
        assert not lolly_helpers.dir_exists(test_dir)

    def test_instantiate(self):
        self.__create_test_dir_if_not_exists()
        src_dir = self.TEST_DATA_DIR + '/lollywiz/instantiation_tests'
        dest_dir = self.TMP_DIR
        wiz = LollyWiz(src_dir, dest_dir)
        wiz.instantiate()
        result = lolly_helpers.silent_read_text_file(dest_dir + '/default_class.hpp')
        assert not result['error']
        verification = lolly_helpers.silent_read_text_file(src_dir + '/verify1.txt')
        assert not verification['error']
        assert result['contents'] == verification['contents']

        wiz.set_definitions(['SHOW_BRIEF_COMMENT', 'USE_TEMPLATE1', 'COND1'])
        wiz.set_replacements({'CLASS_NAME': 'TestClass', 'CLASS_FILE_NAME': 'test_class'})
        wiz.instantiate()
        result = lolly_helpers.silent_read_text_file(dest_dir + '/test_class.hpp')
        assert not result['error']
        verification = lolly_helpers.silent_read_text_file(src_dir + '/verify2.txt')
        assert not verification['error']
        assert result['contents'] == verification['contents']

    # def test_set_src_from_lib(self):
    #     self.__create_test_dir_if_not_exists()
    #     wiz = LollyWiz()
    #     wiz.set_src_from_lib('git')
    #     wiz.set_dest(self.TMP_DIR)
    #     wiz.set_definitions(['LICENSE_TYPE_MIT'])
    #     wiz.set_replacements({'PROJECT_NAME': 'Git Project'})
    #     wiz.instantiate()

    def test_zzz_cleanup(self):
        # Tests are executed in alphabetical order, 'zzz' makes it the last in the list
        self.__remove_test_dir()
        print("***** lolly_wiz tests done.")
