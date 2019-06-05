from .meta import BareException
from .const import EXECUTABLES, COMMANDS


class Line:
    """This class represents an individual line of text/code"""

    def __init__(self, lines, number, text=''):
        self.lines = lines
        self.editor = lines.editor
        self.config = lines.config
        self.number = number
        self.__text = text
        self.number_of_rows = 1
        self.row = {}
        self.calc_rows()
        self.split_rows()
        self.calc_cursor()
        self.__y = 0
        self.__x = self.end_x
        self.end_y = 0 - self.number_of_rows + 1
        self.end_x = 0
        self.length = len(text)
        self.syntax = {}
        self.listing = []
        self.executable = False
        self.collapsed = False
        self.indent_required = False
        self.error = False
        self.indentation = len(self.__text) - len(self.__text.lstrip())
        self.marked = False
        self.selected = False
        self.continue_quoting = False
        self.equal_continues = False
        self.if_continues = False
        for character in text:
            self.listing.append(character)

    def __str__(self):
        return self.__text

    def __int__(self):
        return self.lines.db

    def __add__(self, char):
        new_text = self.__text + char
        self.set_text(new_text)

    def calc_rows(self, width=None):
        """Calculates the number of rows required to print line"""
        width = width or self.editor.window.width
        number_of_lines = int(len(self.__text) / width + 1)
        self.number_of_rows = number_of_lines

    def check_executable(self):
        """Checks text to see if it contains an executable command"""
        if not self.config['inline_commands']:
            return
        if not self.config['highlight_commands']:
            return
        if not self.text:
            self.executable = False
            return
        for item in (
                ' ', '#', 'run ', 'strip ', 'prev ', 'new ', 'quit ', 'revert ', 'timestamp ', 'undo ', 'saveprefs ',
                'setcolor ', 'setcolors ', 'previous '):
            if self.text.startswith(item):
                self.executable = False
                return
        word1 = ''
        word2 = ''
        temp_list = self.text.split()
        if temp_list:
            word1 = temp_list[0]
        if len(temp_list) >= 2:
            word2 = temp_list[1]
        if self.config['inline_commands'] == 'protected':
            p_string = self.config['protect_string']
            if not word1.startswith(p_string):
                return
            word1 = word1.replace(p_string, '', 1)

        if word1 and word1 in EXECUTABLES and word1 == EXECUTABLES[EXECUTABLES.index(word1)]:
            if word1 in ('replace', 'protect') and ' with ' in self.text:
                self.executable = True

            elif len(temp_list) > 1 and word2 and word2[0] in ('=', '+', '-', '*', '/', '%', '(', '[', '{'):
                if word1 in ('save', 'saveas', 'load') and word2[0] == '/':
                    pass
                else:
                    self.executable = False

            elif word1 in (
                    'syntax', 'entry', 'live', 'formatting', 'tab', 'tabs', 'whitespace', 'show', 'hide', 'goto',
                    'color', 'help', 'debug', 'split', 'guide', 'pageguide') and self.text.count(' ') > 1:
                self.executable = False

            elif word1 in ('replace', 'protect') and \
                    self.text.count(' ') > 3 and \
                    ' with' not in self.text and \
                    '|' not in self.text:
                self.executable = False
                return

            elif word1 not in ('replace', 'protect', 'find', 'save', 'saveas', 'load', 'mark') and \
                    self.text.count(' ') - 1 > self.text.count(',') + (2 * self.text.count('-')):
                self.executable = False
                return

            elif word1 not in ('replace', 'protect', 'find', 'save', 'saveas', 'load', 'mark') and \
                    self.text.count('-') > 1:
                self.executable = False
                return

            elif word1 not in (
                    'replace', 'protect', 'find', 'save', 'saveas', 'load',
                    'mark') and '-' in self.text and ',' in self.text:
                self.executable = False
                return

            else:
                self.executable = True
        else:
            self.executable = False

    def split_rows(self, width=None):
        """This function creates a dictionary with strings of proper size"""
        width = width or self.editor.window.width
        self.row = {}
        for i in range(0, self.number_of_rows):
            self.row[i] = self.__text[(width * i):(width * i + width)]

    @staticmethod
    def num_left_of(text, position):
        """Function to compare position of number with other character"""
        flag = True
        if '[' not in text and '(' not in text and ':' not in text and ',' not in text and \
                ';' not in text and '=' not in text and '+' not in text and '-' not in text and \
                '*' not in text and '/' not in text and '%' not in text:
            return False
        
        for char in '[(:,;+-*/%=':
            if char in text:
                char_pos = text.rfind(char)
                if position <= char_pos:
                    flag = False
                    continue
                flag = True
                for i in range(char_pos, position):
                    if text[i].isalpha():
                        flag = False
        return flag

    def add_syntax(self):  # , width=None):
        """This function creates a dictionary with added syntax"""
        # width = width or self.editor.width
        self.syntax = {}
        self.continue_quoting = False
        double_quote = False
        single_quote = False
        triple_quote = False
        comment = False
        command = False
        number_char = False
        operator = False
        func = False
        separator = False
        backslash = False
        mark_on = False
        my_class = False
        # negative = False

        quote_number = 0
        mark_num = 1

        if self.number > 1 and self.continue_quoting:
            triple_quote = True
        # New section to fix multi-line quoting (with '\')
        elif self.number > 1 and \
                '_!DQT!_' in str(self.syntax.values()) and \
                '_!OFF!_' not in str(self.syntax.values()) and \
                self.text.endswith('\\'):
            double_quote = True
        elif self.number > 1 and \
                '_!SQT!_' in str(self.syntax.values()) and \
                '_!OFF!_' not in str(self.syntax.values()) and \
                self.text.endswith('\\'):
            single_quote = True

        try:
            if self.text and self.text[self.indentation] == '#':
                triple_quote = False
        except BareException:
            pass

        count = 0

        for key in range(0, len(self.row)):
            temp_list = []
            word = ''
            # phrase = ''
            old_letter = ''

            for j in range(0, len(self.row[key])):
                letter = self.row[key][j]
                try:
                    next_letter = self.row[key][j + 1]
                except BareException:
                    next_letter = ''

                word += letter

                var_found = False  # This bit used to determine when a number is part of variable
                if len(word) > 1:
                    if word[1].isalpha():
                        var_found = True
                    elif word[0].isalpha():
                        var_found = True
                elif len(word) == 1:
                    if word[0].isalpha():
                        var_found = True

                if mark_on:
                    mark_num += 1

                if self.marked and self.marked is not True and self.marked in self.row[key]:
                    try:
                        if self.row[key][j:j + len(self.marked)] == self.marked:
                            temp_list.append('_!MAR!_')
                            mark_on = True
                    except BareException:
                        pass

                if not backslash and not single_quote and not double_quote and not triple_quote:
                    try:
                        threesome = self.row[key][j:j + 3]
                        if threesome == '"""':
                            triple_quote = True
                            temp_list.append('_!TQT!_')
                            temp_list.append(letter)
                            word = ''
                            continue
                    except BareException:
                        pass

                if letter == '"':
                    quote_number += 1  # trying to fix triple quotes broken by line break
                else:
                    quote_number = 0

                if not backslash and letter == '\\':
                    if single_quote or double_quote or triple_quote:
                        backslash = True
                        temp_list.append(letter)
                        continue

                if backslash and letter in ('"', "'", '\\', 'n', 't', 'a', 'r', 'f', 'b'):  # added 'r', 'f' and 'b'
                    backslash = False
                    temp_list.append(letter)
                    continue

                if triple_quote and not temp_list:
                    temp_list.append('_!TQT!_')
                elif double_quote and not temp_list:
                    temp_list.append('_!DQT!_')
                elif single_quote and not temp_list:
                    temp_list.append('_!SQT!_')

                if number_char and letter not in '0123456789':
                    number_char = False
                    temp_list.append('_!NOF!_')

                if operator and letter not in '+-*/%=><![](){}':
                    operator = False
                    temp_list.append('_!OOF!_')

                if self.config['show_indent'] and letter == ' ' and count < self.indentation:
                    temp_list.append('_!IND!_')
                    count += 1
                elif self.config['showSpaces'] and letter == ' ' and not command and not func and not my_class:
                    temp_list.append('_!SPA!_')

                if separator and not temp_list:  # comment lines that wrap across rows
                    temp_list.append('_!SEP!_')

                if comment and not temp_list:  # comment lines that wrap across rows
                    temp_list.append('_!CMT!_')
                    temp_list.append(letter)

                elif word in ('def', 'def:') and \
                        not double_quote and \
                        not single_quote and \
                        not triple_quote and \
                        not command and \
                        not func and \
                        not my_class and \
                        not comment and \
                        not separator and \
                        next_letter in (' ', ''):
                    temp_list.insert(-len(word) + 1, '_!FUN!_')
                    func = True
                    word = ''
                    temp_list.append(letter)

                elif word in ('class', 'class:') and \
                        not double_quote and \
                        not single_quote and \
                        not triple_quote and \
                        not command and \
                        not func and \
                        not my_class and \
                        not comment and \
                        not separator and \
                        next_letter in (' ', ''):
                    temp_list.insert(-len(word) + 1, '_!CLA!_')
                    my_class = True
                    word = ''
                    temp_list.append(letter)

                elif word.endswith("False") and \
                        not word[word.rfind("False") - 1:].isalnum() and \
                        not double_quote and not single_quote and \
                        not triple_quote and not comment and \
                        not separator and not func and \
                        next_letter in (' ', '', ')', ',', ';', ']', '}', ':'):
                    temp_list.insert(-len('False') + 1, '_!NEG!_')
                    # negative = True
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!NEO!_')

                elif word[word.rfind('(') + 1:] in ('not', 'False', 'False,', 'False)', ', False)', 'False:') and \
                        not double_quote and not single_quote and \
                        not triple_quote and not comment and \
                        not separator and not func and \
                        next_letter in (' ', '', ')', ',', ';', ']', '}', ':'):
                    if '(' in word:
                        temp_list.insert(-len(word[word.rfind('(') + 1:]) + 1, '_!NEG!_')
                    elif ':' in word:
                        temp_list.insert(-len(word[word.find(':') + 1:]) + 1, '_!NEG!_')
                    else:
                        temp_list.insert(-len(word) + 1, '_!NEG!_')
                    # negative = True
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!NEO!_')

                elif word.endswith('True') and not word[word.rfind('True') - 1:].isalnum() and \
                        not double_quote and not single_quote and not triple_quote and \
                        not comment and not separator and not func and not next_letter.isalnum():
                    temp_list.insert(-len('True') + 1, '_!POS!_')
                    # positive = True
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!POO!_')

                elif word[word.rfind('(') + 1:] in ('True', 'True,', 'True)', ',True)', 'True:') and \
                        not double_quote and not single_quote and not triple_quote and \
                        not comment and not separator and not func and \
                        next_letter in (' ', '', ')', ',', ';', ']', '}', ':'):
                    if '(' in word:
                        temp_list.insert(-len(word[word.rfind('(') + 1:]) + 1, '_!POS!_')
                    elif ':' in word:
                        temp_list.insert(-len(word[word.find(':') + 1:]) + 1, '_!POS!_')
                    else:
                        temp_list.insert(-len(word) + 1, '_!POS!_')
                    # positive = True
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!POO!_')

                # New bit for CONSTANT variables
                elif not next_letter.isalnum() and next_letter != '_' and \
                        not single_quote and not double_quote and \
                        not triple_quote and not comment and not separator and \
                        word[word.rfind('(') + 1:].isupper() and "'" not in word and '"' not in word and \
                        len(word[word.rfind('(') + 1:]) > 2 and word[word.rfind('(') + 1].isalpha() and \
                        '+' not in word and '-' not in word and '*' not in word and '/' not in word:
                    if '(' in word:
                        temp_list.insert(-len(word[word.rfind('(') + 1:]) + 1, '_!CON!_')
                    else:
                        temp_list.insert(-len(word) + 1, '_!CON!_')
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!COO!_')

                # New bit for CONSTANT variables (handling ':')
                elif not next_letter.isalnum() and next_letter != '_' and not single_quote and \
                        not double_quote and not triple_quote and not comment and not separator and \
                        word[word.rfind(':') + 1:].isupper() and "'" not in word and '"' not in word and \
                        len(word[word.rfind(':') + 1:]) > 2 and word[word.rfind(':') + 1].isalpha() and \
                        '+' not in word and '-' not in word and '*' not in word and '/' not in word:
                    if ':' in word:
                        temp_list.insert(-len(word[word.rfind(':') + 1:]) + 1, '_!CON!_')
                    else:
                        temp_list.insert(-len(word) + 1, '_!CON!_')
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!COO!_')

                # New bit for CONSTANT variables (handling '[')
                elif not next_letter.isalnum() and next_letter != '_' and not single_quote and \
                        not double_quote and not triple_quote and not comment and not separator and \
                        word[word.rfind('[') + 1:].isupper() and "'" not in word and '"' not in word and \
                        len(word[word.rfind('[') + 1:]) > 2 and word[word.rfind('[') + 1].isalpha() and \
                        '+' not in word and '-' not in word and '*' not in word and '/' not in word:
                    if '[' in word:
                        temp_list.insert(-len(word[word.rfind('[') + 1:]) + 1, '_!CON!_')
                    else:
                        temp_list.insert(-len(word) + 1, '_!CON!_')
                    word = ''
                    temp_list.append(letter)
                    temp_list.append('_!COO!_')

                elif word in COMMANDS and not double_quote and not single_quote and not triple_quote and \
                        not command and not func and not my_class and not comment and not separator and \
                        next_letter in (' ', '', ',', ';'):
                    temp_list.insert(-len(word) + 1, '_!CMD!_')
                    command = True
                    word = ''  # changed from one space
                    temp_list.append(letter)

                elif func and letter in ' :=<>.()[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    func = False
                    temp_list.append('_!FOF!_')
                    if letter == ' ' and self.config['showSpaces']:
                        temp_list.append('_!SPA!_')
                    temp_list.append(letter)

                elif my_class and letter in ' :=<>.()[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    my_class = False
                    temp_list.append('_!FOF!_')
                    if letter == ' ' and self.config['showSpaces']:
                        temp_list.append('_!SPA!_')
                    temp_list.append(letter)

                elif command and letter in ' :=<>.()[]abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    command = False
                    temp_list.append('_!NOC!_')
                    if letter == ' ' and self.config['showSpaces']:
                        temp_list.append('_!SPA!_')
                    temp_list.append(letter)

                # New part to check for triple_quotes
                elif letter == '"' and '"""' in word and not backslash and not single_quote:
                    if triple_quote and '\\' in word:
                        try:
                            threesome = self.row[key][j - 2:j + 1]
                            four_ago = self.row[key][j - 3]
                            if threesome == '"""' and four_ago != '\\':
                                triple_quote = False
                                temp_list.append(letter)
                                temp_list.append('_!OFF!_')
                                word = ''
                                self.continue_quoting = False
                            else:
                                temp_list.append(letter)
                        except BareException:
                            pass

                    elif triple_quote:
                        triple_quote = False
                        temp_list.append(letter)
                        temp_list.append('_!OFF!_')
                        word = ''
                        self.continue_quoting = False
                    else:
                        triple_quote = True
                        temp_list.append('_!TQT!_')
                        temp_list.append(letter)
                        word = ''
                elif letter == '"' and not backslash and triple_quote and quote_number == 3:
                    # new bit to fix triple quotes broken by line break
                    triple_quote = False
                    temp_list.append(letter)
                    temp_list.append('_!OFF!_')
                    word = ''
                    self.continue_quoting = False

                elif letter == '"' and not backslash and \
                        not triple_quote and not double_quote and \
                        not single_quote and not comment and not separator:
                    double_quote = True
                    temp_list.append('_!DQT!_')
                    temp_list.append(letter)
                elif letter == "'" and not backslash and \
                        not triple_quote and not double_quote and \
                        not single_quote and not comment and not separator:
                    single_quote = True
                    temp_list.append('_!SQT!_')
                    temp_list.append(letter)
                elif letter == '"' and double_quote and not backslash:
                    double_quote = False
                    temp_list.append(letter)
                    temp_list.append('_!OFF!_')
                elif letter == "'" and single_quote and not backslash:
                    single_quote = False
                    temp_list.append(letter)
                    temp_list.append('_!OFF!_')

                elif letter == '#' and not double_quote and not single_quote and not triple_quote and not separator:
                    if next_letter == '#':
                        separator = True
                        temp_list.append('_!SEP!_')
                    else:
                        comment = True
                        temp_list.append('_!CMT!_')
                    temp_list.append(letter)

                # new number check
                elif letter.isdigit() and not var_found and not number_char and not double_quote and \
                        not single_quote and not triple_quote and not comment and not separator:
                    number_char = True
                    temp_list.append('_!NUM!_')
                    temp_list.append(letter)

                elif letter.isdigit() and not number_char and self.num_left_of(word, len(word)) and \
                        not old_letter.isalpha() and not double_quote and not single_quote and \
                        not triple_quote and not comment and not separator:
                    number_char = True
                    temp_list.append('_!NUM!_')
                    temp_list.append(letter)

                elif letter in '01234567890' and not number_char and j == 0 and not double_quote and \
                        not single_quote and not triple_quote and not comment and not separator:
                    number_char = True
                    temp_list.append('_!NUM!_')
                    temp_list.append(letter)

                elif letter in '+-*/%=><![](){}' and not number_char and not double_quote and \
                        not single_quote and not triple_quote and not comment and not separator:
                    operator = True
                    temp_list.append('_!OPE!_')
                    temp_list.append(letter)

                else:
                    temp_list.append(letter)
                if letter == ' ' or letter == '    ':
                    word = ''

                if mark_on and mark_num == len(self.marked):
                    temp_list.append('_!MOF!_')
                    mark_on = False
                    mark_num = 1

                old_letter = letter

            self.syntax[key] = temp_list
        if triple_quote:
            self.continue_quoting = True

    def set_text(self, text):
        """Changes line text and updates other attributes"""
        if self.lines.locked:
            return  # don't allow editing if locked
        # old_len = len(self.__text)
        self.__text = text
        self.calc_rows()
        self.split_rows()
        self.calc_cursor()
        self.length = len(text)
        self.listing = []
        for character in text:
            self.listing.append(character)
        self.end_y = 0 - self.number_of_rows + 1
        self.indentation = len(self.__text) - len(self.__text.lstrip())
        self.check_executable()
        # Add syntax if line other than current line is edited (fix acceleration bug)
        if self.config['syntax_highlighting'] and self.number != self.editor.current_num:
            self.add_syntax()

    def get_text(self):
        return self.__text

    def setx(self, num):
        self.__x = num
        if self.__x < 6 and self.__y >= self.end_y:
            self.__x = self.editor.window.width - 1
            self.__y -= 1
            if self.__y < self.end_y:
                self.__y = 0
                self.__x = self.end_x
        elif self.__x < 6 and self.__y != 0:
            self.__x = self.editor.window.width - 1
        elif self.__x < 6:
            self.__x = self.end_x
        elif self.__x > self.editor.window.width - 1 and self.__y < 0:
            self.__x = 6
            self.__y += 1
        elif self.__x > self.end_x and self.__y == 0:
            self.__y = self.end_y
            self.__x = 6

    def sety(self, num):
        self.__y = num
        if self.__y < self.end_y:
            self.__y = 0
        elif self.__y > 0:
            self.__y = 0

    def getx(self):
        return self.__x

    def gety(self):
        return self.__y

    def swap(self, obj):
        temp_text = self.__text
        self.set_text(obj.__text)
        obj.set_text(temp_text)

    def calc_cursor(self):
        self.end_x = len(self.row[(self.number_of_rows - 1)]) + 6

    text = property(get_text, set_text)
    x = property(getx, setx)
    y = property(gety, sety)


class Lines:
    def __init__(self, editor):
        self.editor = editor
        self.config = editor.config
        self.window = editor.window
        self.number = 0
        self.total = 0
        self.locked = False
        self.db = {}

    def add(self, text=''):
        self.total = len(self.db) + 1
        self.db[self.total] = Line(self, self.total, text)
        return self.db[self.total]

    def renum(self):
        """Renumber lines"""
        current_num = 1
        for key, value in self.db.items():
            # temp = value
            self.db[current_num] = value
            self.db[current_num].number = current_num  # new bit

            if value.number > current_num:
                del self.db[key]
                self.db[1].recalc_total()
            current_num += 1

    def recalc_total(self):
        self.total = len(self.db)

    @staticmethod
    def end_colon(text):
        """Finds end colon in text even when followed by comment
                Returns 'True' if colon found, 'False' otherwise"""
        if text and text[-1] == ':':
            return True
        elif ':' in text:
            temp_list = text.split(':')
            prev = temp_list[-2]
            last = temp_list[-1]
            if last.strip().startswith('#') and not prev.rstrip().endswith('#'):
                return True
            else:
                return False
        else:
            return False

    def collapse_these(self, num):
        """Helper function to process redundant text checks in collapse function"""
        item = self.db[num]
        if item.text.endswith(':') or self.end_colon(item.text):
            self.collapse_line(num)

    def collapse(self, text):
        """Function that attempts to collapse lines"""
        # global program_message
        self.editor.program_message = ' Collapsed lines '
        selection = False
        func_total = 0
        if text == 'collapse':
            selection, item_count = self.editor.get_selected()
            if selection:
                text = 'collapse %s' % selection
        temp_text = text
        self.editor.reset_line()

        num = 0
        item_found = ''
        search_string = ''
        try:
            # Search for function or class
            if len(temp_text) > 9 and temp_text[9].isalpha() and \
                    self.editor.get_args(temp_text) not in ('function', 'functions', 'class', 'classes'):
                search_string = temp_text[9:]
                find_function = 'def ' + search_string + '('
                find_class = 'class ' + search_string + '('
                for i in range(1, len(self.db) + 1):
                    item = self.db[i]
                    if item.text.strip().startswith(find_function) or item.text.strip().startswith(find_class):
                        if item.text.strip().startswith('def'):
                            item_found = 'function'
                        elif item.text.strip().startswith('class'):
                            item_found = 'class'
                        temp_text = 'collapse %i' % i
                        func_total += 1
                        break
                if not func_total:
                    self.editor.program_message = ' Specified function/class not found! '
                    return

            if self.editor.get_args(temp_text) in ('function', 'functions', 'class', 'classes'):
                # settings['collapse_functions'] = True
                self.collapse_functions()
            elif 'tab' in temp_text or 'indent' in temp_text:
                indent_num = int(self.editor.get_args(temp_text)[1])
                self.editor.program_message = ' Collapsed lines with indent of %i ' % indent_num
                for i in range(1, len(self.db) + 1):
                    self.editor.status_message('Processing: ', (100 / (self.total * 1.0 / i)))
                    # item = self.db[i]
                    try:
                        _next = self.db[i + 1]
                    except BareException:
                        return
                    if _next.indentation >= indent_num * 4:
                        self.collapse_these(i)
            elif '-' in temp_text:
                temp_list = self.editor.get_args(temp_text, ' ', '-')
                start = max(1, int(temp_list[0]))
                end = min(self.total, int(temp_list[1]))
                self.editor.program_message = ' Collapsed lines between %i and %i ' % (start, end)
                for i in range(start, end + 1):
                    self.editor.status_message('Processing: ', (100 / ((end - start) * 1.0 / i)))
                    self.collapse_these(i)
            elif ',' in temp_text:
                temp_list = self.editor.get_args(temp_text, ' ', ',')
                self.editor.program_message = ' Collapsed %i lines ' % len(temp_list)
                for i in range(0, len(temp_list)):
                    num = int(temp_list[i])
                    self.collapse_these(num)
            else:
                arg_list = self.editor.get_args(temp_text)
                if 'str' in str(type(arg_list)):
                    num = int(arg_list)
                    self.collapse_these(num)
                else:
                    for i in range(0, len(arg_list)):
                        num = int(arg_list[i])
                        self.collapse_these(num)
                self.editor.program_message = ' Collapsed line number %i ' % num
            if selection:
                self.editor.program_message = ' Selection collapsed '
            elif func_total:
                self.editor.program_message = " Collapsed %s '%s' " % (item_found, search_string)
        except BareException:
            self.editor.program_message = ' Error, collapse failed! '

    def collapse_functions(self):
        """Collapses all function and class definitions"""
        # global program_message
        for i in range(2, len(self.db) + 1):
            self.editor.status_message('Processing: ', (100 / (self.total * 1.0 / i)))
            prev_item = self.db[i - 1]
            item = self.db[i]
            if not prev_item.collapsed:
                if prev_item.text[prev_item.indentation:(prev_item.indentation + 4)] == 'def ':
                    item.collapsed = True
                    item.indent_required = prev_item.indentation
                elif prev_item.text[prev_item.indentation:(prev_item.indentation + 6)] == 'class ':
                    item.collapsed = True
                    item.indent_required = prev_item.indentation
            elif prev_item.collapsed:
                if not item.text:
                    item.collapsed = True
                    item.indent_required = prev_item.indent_required
                elif item.indentation <= prev_item.indent_required:
                    item.collapsed = False
                else:
                    item.collapsed = True
                    item.indent_required = prev_item.indent_required
            self.editor.program_message = ' Functions & classes collapsed '

    def collapse_line(self, number):
        """Attempt to collapse line number"""
        for i in range(number + 1, len(self.db)):
            item = self.db[i]
            if item.indentation > self.db[number].indentation or not item.text:
                if item.collapsed:
                    item.indent_required = min(item.indent_required, self.db[number].indentation)
                else:
                    item.indent_required = self.db[number].indentation
                item.collapsed = True
            else:
                return

    def expand(self, text):
        """Processes 'expand' command"""
        # global program_message
        selection = False
        func_total = 0
        if text == 'expand':
            selection, item_count = self.editor.get_selected()
            if selection:
                text = 'expand %s' % selection

        self.editor.reset_line()
        num = 0
        item_found = ''
        search_string = ''
        try:
            if len(text) > 7 and text[7].isalpha():  # Search for function or class
                search_string = text[7:]
                find_function = 'def ' + search_string + '('
                find_class = 'class ' + search_string + '('
                for i in range(1, len(self.db) + 1):
                    item = self.db[i]
                    if item.text.strip().startswith(find_function) or item.text.strip().startswith(find_class):
                        if item.text.strip().startswith('def'):
                            item_found = 'function'
                        elif item.text.strip().startswith('class'):
                            item_found = 'class'
                        text = 'collapse %i' % i
                        func_total += 1
                        break
                if not func_total:
                    self.editor.program_message = ' Specified function/class not found! '
                    return

            if 'expand all' in text:
                self.expand_all()
                self.editor.program_message = ' Expanded all lines '
            elif "-" in text:  # expand range of lines
                temp_list = self.editor.get_args(text, ' ', '-')
                start = max(1, int(temp_list[0]))
                end = min(self.total, int(temp_list[1]))
                self.editor.program_message = ' Expanded lines %i to %i ' % (start, end)
                for i in range(start, end + 1):
                    self.expand_line(i)
            elif ',' in text:  # expand list of lines
                temp_list = self.editor.get_args(text, ' ', ',')
                self.editor.program_message = ' Expanded %i lines ' % len(temp_list)
                for i in range(0, len(temp_list)):
                    num = int(temp_list[i])
                    self.expand_line(num)
            elif 'functions' in text:  # expand functions
                self.editor.program_message = ' Expanded functions & classes '
                for i in range(1, len(self.db) + 1):
                    item = self.db[i]
                    if item.text[item.indentation:(item.indentation + 4)] == 'def ':
                        self.editor.expand_line(i)
                    elif item.text[item.indentation:(item.indentation + 6)] == 'class ':
                        self.editor.expand_line(i)
            else:  # expand line number
                arg_list = self.editor.get_args(text)
                if 'str' in str(type(arg_list)):
                    num = int(arg_list)
                    self.expand_line(num)
                else:
                    for i in range(0, len(arg_list)):
                        num = int(arg_list[i])
                        self.expand_line(num)
                self.editor.program_message = ' Expanded line number %i ' % num
            if selection:
                self.editor.program_message = ' Selection expanded '
            elif func_total:
                self.editor.program_message = " Expanded %s '%s' " % (item_found, search_string)
        except BareException:
            self.editor.program_message = ' Error, expand failed! '

    def expand_line(self, number):
        """Attempt to expand line number"""
        if self.db[number].collapsed:
            return
        for i in range(number + 1, len(self.db) + 1):
            item = self.db[i]
            if item.indentation > self.db[number].indentation or not item.text:
                item.collapsed = False
            elif item.indentation <= self.db[number].indentation:
                return

    def expand_all(self):
        """Expand all lines"""
        # global program_message
        self.editor.program_message = " Expanded all lines "
        for i in range(1, len(self.db) + 1):
            self.db[i].collapsed = False
