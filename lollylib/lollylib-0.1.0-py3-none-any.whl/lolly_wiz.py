import os
import ntpath
import lolly_helpers
import semver


class LollyWiz:
    def __init__(self, source_dir=None, destination_dir=None, definitions=None,
                 replacement_dict=None):
        # LollyWiz version is treated independently from lollylib version;
        # It has impact on how lollywiz.txt is processed:
        # the file's version must be same or less than the software version.
        self.VERSION = '0.1.0'
        self._TEXTFILE_VERSION_VAR_NAME = 'LOLLYWIZ_TEXTFILE_VERSION'  # version of lollywiz.txt
        self.OPTIONS = {'remove_trailing_new_lines_after_conditional_directives_in_template': True}
        self.src_root_dir = source_dir
        self.dest_root_dir = destination_dir

        self.definitions = definitions
        if self.definitions is None:
            self.definitions = []
        self.replacement_dict = replacement_dict
        if self.replacement_dict is None:
            self.replacement_dict = {}

        # constants
        self.PATH_DELIMITER_CHAR = '/'
        self.COMMENT_START_SEQ = '/*'
        self.COMMENT_END_SEQ = '*/'
        self.REPLACEMENT_START_SEQ = '[$$'
        self.REPLACEMENT_END_SEQ = '$$]'
        self.COND_START_SEQ = '[##'
        self.COND_END_SEQ = '##]'

        self.INSTRUCTION_FILE_NAME = 'lollywiz.txt'
        self.SUPPORTED_INSTRUCTIONS = ['copy', 'remove', 'inst', 'mkdir']
        self._MAX_LOOP_ITERS = 1000  # prevent looping forever in case of unexpected error

        # internal status variables
        self._is_src_dir_set = False
        self._is_dest_dir_set = False
        self._is_instr_file_read = False
        self._is_instr_file_parsed = False

        # instruction file
        self._instr_file_full_path = ''
        self._instr_file_data = None

        # error handling
        # empty: no error;
        # other possible values: 'syntax', 'file', 'procedural', 'version';
        # more detailed error message is printed to the console;
        self.error = ''

        if self.src_root_dir is not None:
            self.set_src(self.src_root_dir)
        if self.dest_root_dir is not None:
            self.set_dest(self.dest_root_dir)
        if self.definitions is not None:
            self.set_definitions(self.definitions)
        if self.replacement_dict is not None:
            self.set_replacements(self.replacement_dict)

    # USER METHODS
    def set_src(self, src_dir):
        """
        Sets template source folder. 'src_dir' must exist and contain file lollywiz.txt.
        :param src_dir: string
        :return: None
        """
        self._is_src_dir_set = False
        self._is_instr_file_parsed = False
        self._clear_error()
        self.src_root_dir = src_dir
        self._instr_file_full_path = self.src_root_dir + self.PATH_DELIMITER_CHAR + self.INSTRUCTION_FILE_NAME
        src_root_dir_exists = lolly_helpers.dir_exists(self.src_root_dir)
        if not src_root_dir_exists:
            self._report_file_operation_error("template source directory '" + self.src_root_dir
                                              + "' does not exist")
        if not lolly_helpers.file_exists(self._instr_file_full_path):
            self._report_file_operation_error("instruction file '" + self._instr_file_full_path
                                              + "' does not exist")
            return
        self._is_src_dir_set = True

    def set_src_from_lib(self, template_name):
        """
        An alternative way to set src folder from mini template library that is shipped with lollylib.
        :param template_name: string - name of the template
        :return: None
        """
        head, tail = ntpath.split(os.path.realpath(__file__))
        templates_dir = head + '/assets/lollywiz_templates/'
        self.set_src(templates_dir + template_name)

    def set_dest(self, dest_dir):
        """
        Sets destination directory where result is generated. If this directory exists,
        it will be overwritten.
        :param dest_dir:
        :return: None
        """
        self.dest_root_dir = dest_dir
        self._is_dest_dir_set = True

    def set_definitions(self, condition_list):
        """
        Sets condition definitions that will be used during template instantiation and when parsing lollywiz.txt.
        :param condition_list: list of strings
        :return: None
        """
        self._is_instr_file_parsed = False  # signal re-parsing of instructions is required
        self._is_instr_file_read = False
        self.definitions = condition_list
        if self.definitions is None:
            self.definitions = []

    def set_replacements(self, replacement_dict):
        """
        Sets condition definitions that will be used during template instantiation and when parsing lollywiz.txt.
        :param replacement_dict: dict of string:string pairs
        :return: None
        """
        self._is_instr_file_parsed = False  # signal re-parsing of instructions is required
        self._is_instr_file_read = False
        self.replacement_dict = replacement_dict
        if self.replacement_dict is None:
            self.replacement_dict = {}

    def instantiate(self):
        """
        Instantiates template according to parsed lollywiz.txt file.
        :return:
        """
        # Parse instruction if not parsed yet
        if not self._is_instr_file_parsed:
            self._parse_instructions()
        if not self.error:
            # Execute each instruction
            for i in self._instr_file_data:
                if self.error:
                    break
                self._execute_instruction(i)
            self._is_instr_file_parsed = True

    # PRIVATE METHODS

    def _check_version(self, str_list):
        """
        Search for LOLLYWIZ_TEXTFILE_VERSION in str_list and check
        if current software version is greater or equal to it.
        Set self.error to 'version' if versions are not compatible.
        :param str_list: list of strings
        :return: processed str_list;
        """
        if self.error == 'version':
            self.error = ''
        v_index = lolly_helpers.find_line_starting_with_seq(str_list, self._TEXTFILE_VERSION_VAR_NAME)
        if -1 == v_index:
            self._report_version_error("required variable '" + self._TEXTFILE_VERSION_VAR_NAME + "' not found.")
            return str_list

        file_ver = lolly_helpers.parse_assignment(str_list[v_index])
        if file_ver['error']:
            self._report_version_error(self._TEXTFILE_VERSION_VAR_NAME + " does not have value.")
            return str_list
        file_ver = file_ver['value']

        # if not self.VERSION.is_greater_or_equal(file_ver):
        compare_result = 0
        try:
            compare_result = semver.compare(self.VERSION, file_ver)
        except ValueError as e:
            self._report_version_error("LOLLYWIZ_TEXTFILE_VERSION must be compatible with semver.org")
            return str_list
        if compare_result < 0:
            self._report_version_error("version is newer than current software version. Update lolly_wiz.py.")
            return str_list
        str_list = lolly_helpers.remove_selected_from_list(str_list, [v_index])
        return str_list

    def _generate_common_replacements(self):
        """
        Generates common replacements such as __DATE__, __DATETIME__, __TIME__, __YEAR__
        :return: None
        """
        self.replacement_dict['__DATE__'] = lolly_helpers.current_date_utc()
        self.replacement_dict['__DATETIME__'] = lolly_helpers.current_datetime_utc()
        self.replacement_dict['__TIME__'] = lolly_helpers.current_time_utc()
        self.replacement_dict['__YEAR__'] = lolly_helpers.current_year_utc()

    def _parse_instructions(self):
        if not self._is_src_dir_set:
            self._report_procedural_error("template source dir must be set before instantiating")
            return
        if not self._is_dest_dir_set:
            self._report_procedural_error("destination dir must be set before instantiating")
            return
        self._generate_common_replacements()
        if not self._is_instr_file_read:
            self._read_instruction_file()
        if self.error:
            return
        self._apply_definitions_to_instr_file()  # this must be done before data is split into string list
        if self.error:
            return
        self._remove_instr_file_comments_and_empty_lines()  # also splits data into string list
        if self.error:
            return
        self._instr_file_data = self._check_version(self._instr_file_data)
        if self.error:
            return
        self._apply_replacements_to_instr_file()
        if self.error:
            return
        # print("* LollyWiz debug instructions AFTER applied definitions: ", self._instr_file_data)
        instr_start_pos = lolly_helpers.find_line_starting_with_seq(self._instr_file_data, "#instructions_begin")
        instr_end_pos = lolly_helpers.find_line_starting_with_seq(self._instr_file_data, "#instructions_end")
        if instr_start_pos == -1:
            self._report_syntax_error("'#instructions_begin' directive is missing")
            return
        if instr_end_pos == -1:
            self._report_syntax_error("'#instructions_end' directive is missing")
            return
        if instr_start_pos > instr_end_pos:
            self._report_syntax_error("'#instructions_end' must go after '#instructions_begin'")
            return
        if instr_start_pos == instr_end_pos - 1:
            self._instr_file_data = []
            return
        # Remove everything except what is between '#instructions_begin' and '#instructions_end'
        self._instr_file_data = lolly_helpers.open_range_sublist(self._instr_file_data,
                                                                 instr_start_pos + 1, instr_end_pos)
        # print("* LollyWiz debug instructions AFTER final parsing: ", self._instructions)
        self._parse_and_validate_instructions()

    def _process_conditional_directives(self, data, filename):
        """
        Process condition directives according to definitions self.definitions.
        'filename' is used for error messages only.
        :param data: string
        :param filename: string
        :return: processed data
        """
        groups = []
        iterations = 0
        cur_index = 0
        search_lim_index = -1

        # print("* DEBUG DATA: ---------------------------------\n", data)
        while True:
            iterations += 1
            if iterations > self._MAX_LOOP_ITERS:
                self._report_procedural_error("endless loop detected in _process_conditional_directives. "
                                              "Report this to the developer.")
                return data

            group = {'blocks': [], 'endif': [-1, -1]}

            # 1. Search for 'if' directive
            found = self._get_first_cond_directive(data, filename, 'if', cur_index, search_lim_index)
            if found[0] is None:  # template does not contain any more 'if's
                break
            else:
                inst = found[0]
                cur_index = found[2]
                if_block = {'start': found[1], 'dir_end': found[2], 'end': -1, 'is_true': False}  # -1: not yet known
                # check number of arguments and if condition is true
                if len(inst['args']) != 1:
                    self._report_syntax_error("'if' in source file '" + filename +
                                              "' must have exactly one argument.")
                    return data
                if inst['args'][0] in self.definitions:
                    if_block['is_true'] = True
                group['blocks'].append(if_block)

                # 2. Search for 'endif' directive
                found = self._get_first_cond_directive(data, filename, 'endif', cur_index, search_lim_index)
                if found[0] is None:
                    self._report_syntax_error("'if' directive does not have matching 'endif' in source file '"
                                              + filename + "'.")
                    return data
                else:  # in case 'endif' found
                    group['endif'] = [found[1], found[2]]
                    group['blocks'][0]['end'] = group['endif'][0]

                    # 3. Search for 'else' directive between end of 'if' and start of 'endif'
                    cur_index = if_block['dir_end']
                    search_lim_index = group['endif'][0]
                    found = self._get_first_cond_directive(data, filename, 'else', cur_index, search_lim_index)
                    if found[0] is None:  # if 'else' directive not found
                        else_block = None
                    else:  # if 'else' directive found
                        inst = found[0]
                        else_block = {'start': found[1], 'dir_end': found[2], 'end': group['endif'][0],
                                      'is_true': False}
                        # check number of arguments and that condition is true
                        if len(inst['args']):
                            self._report_syntax_error("'else' in source file '" + filename +
                                                      "' must not have arguments.")
                            return data
                        # 3.1 Check if any conditional directives between 'if' and 'else'
                        if self._no_conditional_directives_in_range(data, filename, if_block['dir_end'],
                                                                    else_block['start']):
                            # parsing of current group is complete
                            else_block['is_true'] = not if_block['is_true']

                        else:  # cond directives between 'if' and 'else' found
                            pass

                        # 3.2 Check if any conditional directives between 'else' and 'endif'
                        if self._no_conditional_directives_in_range(data, filename, else_block['dir_end'],
                                                                    group['endif'][0]):
                            pass
                            # print("* debug: NO cond directives between 'else' and 'endif'")
                        else:
                            self._report_syntax_error("there must be no directives between 'else' and 'endif' "
                                                      "in source file '" + filename + "'.")
                            return data

                # Fetch all elif blocks
                cur_index = if_block['dir_end']
                elif_blocks_end = group['endif'][0]
                if else_block is not None:
                    elif_blocks_end = else_block['start']
                search_lim_index = elif_blocks_end
                elif_blocks = self._fetch_elif_blocks(data, filename, cur_index, search_lim_index)

                # Set correct 'end' indexes for each 'elif' block
                blocks_total = len(elif_blocks)
                if blocks_total > 1:
                    for i in range(blocks_total - 1):
                        elif_blocks[i]['end'] = elif_blocks[i + 1]['start']
                    elif_blocks[blocks_total - 1]['end'] = elif_blocks_end
                elif blocks_total == 1:
                    elif_blocks[0]['end'] = elif_blocks_end

                # Correct condition values according to 'if' block
                matching_block_found = False
                if if_block['is_true']:
                    matching_block_found = True
                for elif_block in elif_blocks:
                    if elif_block['is_true']:
                        if not matching_block_found:
                            matching_block_found = True
                        else:
                            elif_block['is_true'] = False
                    # Append all elif blocks to the group
                    group['blocks'].append(elif_block)

                # Finally append 'else' block if any
                if else_block is not None:
                    if not matching_block_found:
                        else_block['is_true'] = True
                    else:
                        else_block['is_true'] = False
                    group['blocks'].append(else_block)

                # Correct first 'if's [end] index
                if len(group['blocks']) > 1:
                    group['blocks'][0]['end'] = group['blocks'][1]['start']
                groups.append(group)

                cur_index = group['endif'][1]
                search_lim_index = -1

        # process data according to parsed definitions
        processed_data = ''
        cur_index = 0
        if groups:
            for g in groups:
                # add everything before group start
                processed_data = processed_data + data[cur_index:g['blocks'][0]['start']]
                for b in g['blocks']:
                    if b['is_true']:
                        # Add block contents with matching condition
                        processed_data = processed_data + data[b['dir_end']:b['end']]
                cur_index = g['endif'][1]
        # Add everything between last group and data end
        processed_data = processed_data + data[cur_index:]
        return processed_data

    def _get_first_cond_directive(self, data, data_filename, directive_name, from_index, to_index):
        result = [None, -1, -1]
        if to_index == -1:
            to_index = len(data)
        cur_index = from_index
        iterations = 0
        remove_trailing_newlines = self.OPTIONS['remove_trailing_new_lines_after_conditional_directives_in_template']
        while True:
            iterations += 1
            if iterations > self._MAX_LOOP_ITERS:
                self._report_procedural_error("endless loop detected in _process_conditional_directives."
                                              " Report this to the developer.")
                return data
            # print ("* DEBUG DATA: ", data)
            found = lolly_helpers.substr_enclosed_in_seq(data, self.COND_START_SEQ, self.COND_END_SEQ,
                                                         cur_index, to_index, remove_trailing_newlines)
            if found['start'] == -1:  # no more condition directives within current scope
                return result
            if found['error']:
                self._report_syntax_error("conditional directive has no closing '" +
                                          self.COND_END_SEQ + "' in source file '"
                                          + data_filename + "'.")
                return result
            if found['value'].find(self.COND_START_SEQ) != -1:
                self._report_syntax_error("conditional directive '" + found['value'] +
                                          "' contains extra '" + self.COND_START_SEQ
                                          + "' in source file '" + data_filename + "'.")
                return result
            inst = lolly_helpers.split_line_into_cmd_and_args(found['value'])
            if inst['cmd'] == directive_name:
                result[0] = inst
                result[1] = found['start']
                result[2] = found['end']
                break
            cur_index = found['end']
            if cur_index > to_index:
                return result
        return result

    def _no_conditional_directives_in_range(self, data, data_filename, from_index, to_index):
        if to_index == -1:
            to_index = len(data)
        cur_index = from_index
        iterations = 0
        remove_trailing_newlines = self.OPTIONS['remove_trailing_new_lines_after_conditional_directives_in_template']
        while True:
            iterations += 1
            if iterations > self._MAX_LOOP_ITERS:
                self._report_procedural_error("endless loop detected in __no_conditional_directives_in_range. "
                                              "Report this to the developer.")
                return False

            found = lolly_helpers.substr_enclosed_in_seq(data, self.COND_START_SEQ,
                                                         self.COND_END_SEQ, cur_index, to_index,
                                                         remove_trailing_newlines)
            if found['start'] == -1:  # no more condition directives within current range
                return True

            if found['error']:
                self._report_syntax_error("conditional directive has no closing '" +
                                          self.COND_END_SEQ + "' in source file '"
                                          + data_filename + "'.")
                return False

            if found['value'].find(self.COND_START_SEQ) != -1:
                self._report_syntax_error("conditional directive '" + found['value'] +
                                          "' contains extra '" + self.COND_START_SEQ
                                          + "' in source file '" + data_filename + "'.")
                return False

            inst = lolly_helpers.split_line_into_cmd_and_args(found['value'])
            if inst['cmd'] == 'if':
                return False
            elif inst['cmd'] == 'elif':
                return False
            elif inst['cmd'] == 'else':
                return False
            elif inst['cmd'] == 'endif':
                return False
            cur_index = found['end']
            if to_index >= to_index:
                return True

    def _fetch_elif_blocks(self, data, filename, from_index, to_index):
        if to_index == -1:
            to_index = len(data)
        result = []
        iterations = 0
        while True:
            iterations += 1
            if iterations > self._MAX_LOOP_ITERS:
                self._report_procedural_error(
                    "endless loop detected in _process_conditional_directives. "
                    "Report this to the developer.")
                return data
            found = self._get_first_cond_directive(data, filename, 'elif', from_index, to_index)
            if found[0] is None:
                return result
            else:
                inst = found[0]
                block = {'start': found[1], 'dir_end': found[2], 'end': -1,
                         'is_true': False}  # -1 means: not yet known
                # check number of arguments
                if len(inst['args']) != 1:
                    self._report_syntax_error("'elif' in source file '" + filename +
                                              "' must have exactly one argument.")
                    return result
                # Check condition
                if inst['args'][0] in self.definitions:
                    block['is_true'] = True
                result.append(block)
                from_index = found[2]
                if from_index >= to_index:
                    return result

    # def _debug_print_group(self, group, data):
    #     i = 1
    #     print("------- GROUP BEGIN -------")
    #     for block in group['blocks']:
    #         print("- BLOCK " + str(i) + ": ", block)
    #         print("'" + data[block['start']:block['end']] + "'")
    #         i += 1
    #     print("------- GROUP END -------")

    # INSTRUCTION PROCESSING

    def _check_instruction_supported(self, i):
        if i['cmd'] in self.SUPPORTED_INSTRUCTIONS:
            return True
        return False

    def _parse_and_validate_instructions(self):
        validated = []
        if not len(self._instr_file_data):
            return validated
        for i in self._instr_file_data:
            parsed = lolly_helpers.split_line_into_cmd_and_args(i)
            if parsed['error']:
                self._report_syntax_error(i)
                return
            if not self._check_instruction_supported(parsed):
                self._report_syntax_error("unknown instruction '" + parsed['cmd'] + "'")
                return
            validated.append(parsed)
        self._instr_file_data = validated

    # Instruction executors
    def _execute_inst(self, i):
        """
        Instantiates single template file
        :param i: string list
        :return: None
        """
        # append src and dest root parts to names (must be done once)
        if not self._is_instr_file_parsed:
            i['args'][0] = self.src_root_dir + self.PATH_DELIMITER_CHAR + i['args'][0]
            i['args'][1] = self.dest_root_dir + self.PATH_DELIMITER_CHAR + i['args'][1]

        src_filename = i['args'][0]
        dest_filename = i['args'][1]
        split_df = lolly_helpers.path_base_and_leaf(dest_filename)
        contents = lolly_helpers.silent_read_text_file(src_filename)
        if contents['error']:
            self._report_file_operation_error("can't read file '" + src_filename + "'.")
            return
        # process conditions
        contents = self._process_conditional_directives(contents['contents'], src_filename)
        contents = lolly_helpers.replace_keys(contents, self.replacement_dict)
        # make sure dest directory exists
        lolly_helpers.silent_create_path(split_df['base'])
        if not lolly_helpers.dir_exists(split_df['base']):
            self._report_file_operation_error("can't create folder: '" + split_df['base'] + "'")
            return
        lolly_helpers.silent_write_text_file(dest_filename, contents)
        if not lolly_helpers.file_exists(dest_filename):
            self._report_file_operation_error("can't write file: '" + dest_filename +
                                              "'")
            return

    def _execute_copy(self, i):
        """
        Copies file or dir tree. If src is directory, dest with same name will be removed before copying.
        :param i:
        :return:
        """
        if len(i['args']) != 2:
            self._report_syntax_error("'copy' has wrong number of arguments, 2 expected")
            return
        # append src and dest root parts to names (must be done once)
        if not self._is_instr_file_parsed:
            i['args'][0] = self.src_root_dir + self.PATH_DELIMITER_CHAR + i['args'][0]
            i['args'][1] = self.dest_root_dir + self.PATH_DELIMITER_CHAR + i['args'][1]

        src_filename = i['args'][0]
        dest_filename = i['args'][1]

        src_props = lolly_helpers.get_filesystem_item_type(src_filename)
        if not src_props['exists']:
            self._report_file_operation_error("required source '" + src_filename + "' doesn't exist")
            return
        dest_props = lolly_helpers.get_filesystem_item_type(dest_filename)

        # delete old filesystem entity if exists
        if dest_props['exists']:
            if dest_props['type'] == 'dir':
                lolly_helpers.silent_remove_dir(dest_filename)
            elif dest_props['type'] == 'file':
                lolly_helpers.silent_remove_file(dest_filename)
            elif dest_props['type'] == 'symlink':
                lolly_helpers.silent_remove_symlink(dest_filename)
        dest_props = lolly_helpers.get_filesystem_item_type(dest_filename)

        # report error if old destination can't be deleted
        if dest_props['exists']:
            self._report_file_operation_error("can't delete file or folder: '" + src_filename +
                                              "'")
            return

        # copy src to dest
        if src_props['type'] == 'dir':
            lolly_helpers.silent_copy_dir(src_filename, dest_filename)
        elif src_props['type'] == 'file':
            lolly_helpers.silent_copy_file(src_filename, dest_filename)
        elif src_props['type'] == 'symlink':
            pass  # TODO: deside how to be with symlinks, for now just ignore them

        dest_props = lolly_helpers.get_filesystem_item_type(dest_filename)

        # report error if destination does not exist
        if not dest_props['exists']:
            self._report_file_operation_error("can't create file or folder: '" + src_filename +
                                              "'")

    def _execute_remove(self, i):
        # print("*DEBUG removing: ", i)
        if len(i['args']) != 1:
            self._report_syntax_error("'remove' must have one argument")
            return
        # append src and dest root parts to names (must be done once)
        if not self._is_instr_file_parsed:
            i['args'][0] = self.dest_root_dir + self.PATH_DELIMITER_CHAR + i['args'][0]
        filename = i['args'][0]
        file_props = lolly_helpers.get_filesystem_item_type(filename)
        if not file_props['exists']:  # nothing to remove
            return

        if file_props['type'] == 'dir':
            lolly_helpers.silent_remove_dir(filename)
        elif file_props['type'] == 'file':
            lolly_helpers.silent_remove_file(filename)
        file_props = lolly_helpers.get_filesystem_item_type(filename)
        # report error if old destination can't be deleted
        if file_props['exists']:
            self._report_file_operation_error("can't delete file or folder: '" +
                                              filename + "'")
            return

    def _execute_mkdir(self, i):
        """
        Creates new directory if doesn't exist;
        :param i: string list
        :return: None
        """
        if len(i['args']) != 1:
            self._report_syntax_error("'mkdir' must have one argument")
            return
        # append src and dest root parts to names (must be done once)
        if not self._is_instr_file_parsed:
            i['args'][0] = self.dest_root_dir + self.PATH_DELIMITER_CHAR + i['args'][0]
        dirname = i['args'][0]
        file_props = lolly_helpers.get_filesystem_item_type(dirname)
        if file_props['exists']:  # nothing to remove
            if file_props['type'] == 'dir':
                return
            if file_props['type'] == 'file':
                lolly_helpers.silent_remove_file(dirname)
            if file_props['type'] == 'symlink':
                lolly_helpers.silent_remove_symlink(dirname)
            else:  # item exists and is of unknown type
                self._report_syntax_error("'mkdir' can't remove existing '" + dirname + "'")
                return
        lolly_helpers.silent_create_path(dirname)

    def _execute_instruction(self, i):
        # print ("* Debug executing instruction: ", i)
        if i['cmd'] == 'copy':  # copies file or directory tree without changes
            self._execute_copy(i)
        elif i['cmd'] == 'inst':  # instantiates template
            self._execute_inst(i)
        elif i['cmd'] == 'remove':  # removes file or directory tree
            self._execute_remove(i)
        elif i['cmd'] == 'mkdir':  # creates an empty dir
            self._execute_mkdir(i)

    def _clear_error(self):
        self.error = ''

    def _report_version_error(self, msg):
        print("* LollyWiz version error in file ",
              self._instr_file_full_path, ': ',
              msg)
        self.error = 'version'

    def _report_syntax_error(self, msg):
        print("* LollyWiz syntax error in file ",
              self._instr_file_full_path, ': ',
              msg)
        self.error = 'syntax'

    def _report_file_operation_error(self, msg):
        print("* LollyWiz file operation error: ",
              msg)
        self.error = 'file'

    def _report_procedural_error(self, msg):
        print("* LollyWiz procedural error: ",
              msg)
        self.error = 'procedural'

    def _read_instruction_file(self):
        self._is_instr_file_read = False
        raw_file_contents = lolly_helpers.silent_read_text_file(self._instr_file_full_path)
        if raw_file_contents['error']:
            self._report_file_operation_error("can't read instruction file '" + self._instr_file_full_path + "'")
            return
        self._instr_file_data = raw_file_contents['contents']
        self._is_instr_file_read = True

    def _remove_instr_file_comments_and_empty_lines(self):
        self._instr_file_data = self._remove_comments(self._instr_file_data).splitlines()
        self._instr_file_data = lolly_helpers.strip_whitespaces_in_list(self._instr_file_data)
        self._instr_file_data = lolly_helpers.remove_empty_lines_from_list(self._instr_file_data)
        self._instr_file_data = self._parse_instr_file_default_replacement_map(self._instr_file_data)

    def _remove_comments(self, the_string):
        iterations = 0
        while True:
            iterations += 1
            if iterations >= self._MAX_LOOP_ITERS:
                self._report_procedural_error("endless loop detected in '_remove_comments() method'")
                return ''
            result = lolly_helpers.extract_substr_enclosed_in_seq(the_string, self.COMMENT_START_SEQ,
                                                                  self.COMMENT_END_SEQ)
            if result['error']:
                self._report_syntax_error("unterminated comment.")
                return ''
            if not result['extracted']:
                return result['remainder']
            the_string = result['remainder']

    def _parse_instr_file_default_replacement_map(self, doc):
        initial_seq = '#default_replacement_map_begin'
        terminal_seq = '#default_replacement_map_end'
        initial_seq_pos = lolly_helpers.find_line_starting_with_seq(doc, initial_seq)
        terminal_seq_pos = lolly_helpers.find_line_starting_with_seq(doc, terminal_seq)
        if initial_seq_pos == -1:
            return doc
        if terminal_seq_pos == -1:
            self._report_syntax_error("#default_replacement_map_end' not found.")
            return doc
        # merge extracted default values and self.replacement_dict,
        # user supplied values have greater priority
        for i in range(initial_seq_pos + 1, terminal_seq_pos):
            result = lolly_helpers.parse_assignment(doc[i])
            if result['error']:
                continue
            if not result['name'] in self.replacement_dict:
                self.replacement_dict[result['name']] = result['value']
        # remove #default_replacement_map section from the doc
        doc = lolly_helpers.remove_closed_range_from_list(doc, initial_seq_pos, terminal_seq_pos)
        return doc

    def _setup_instr_file_replacements(self):
        """ Enclose dictionary keys into self.LOCAL_REPLACEMENT_SEQ """
        tmp = {}
        for key, val in self.replacement_dict.items():
            transformed_key = self.REPLACEMENT_START_SEQ + key + self.REPLACEMENT_END_SEQ
            tmp[transformed_key] = val
        self.replacement_dict = tmp

    def _apply_replacements_to_instr_file(self):
        self._setup_instr_file_replacements()
        self._instr_file_data = lolly_helpers.replace_in_string_list(self._instr_file_data, self.replacement_dict)

    def _apply_definitions_to_instr_file(self):
        self._instr_file_data = self._process_conditional_directives(self._instr_file_data, self._instr_file_full_path)
