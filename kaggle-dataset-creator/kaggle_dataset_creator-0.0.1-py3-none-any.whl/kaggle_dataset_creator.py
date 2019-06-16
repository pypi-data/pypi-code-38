import os
import re
import pandas as pd
from .message import Message
from datetime import datetime

class KaggleDataSet(Message):
    """
    Description
    ===========
        - A class containing number of methods and attributes (almost all're initialized)
          to create dataset in the form of csv/json etc. so that either 
            (a) they could be used to work with pandas
            (b) or used to upload/publish our own created data on Kaggle (https://www.kaggle.com/datasets)
                as the data to be uploaded on Kaggle should be excellent and unique

        - This class provides attributes that you can use to 

        - This class provides you methods that asks user to enter data for each column
          of rows 1 after 1 and generates csv/json as final output 

    """

    def __init__(self, 
                  path='.',
                  extension = 'csv'
                ):

        """
        A constructor
        =============
            - which initializes number of parameters to start the creation of Kaggle 
              dataset

        Parameters
        ==========
            - path: Absolute/relative path of the output file (csv, json)
            - extension: Extension to use for the output file (default: csv)
        """
        self.__validate_and_set(path, extension)

        # Conatiner of enetered data (an input to pandas.DataFrame)
        self.container = {} 

        # Used to store the number of enetered columns in the CSV
        self.total_columns = 0

        # Used to store the name of enetered name of all columns (initially blank)
        self.columns = []

        # Used to store length of all column names
        self.collens = [] 

        # Private variable to maintain the calling sequences
        self.__states = {}

        # If DataFrame is SET
        self.df_set = False

        # For implementing the feature of printing relevant messages to the console
        self.message = Message()

        # Used to store the type of data types of all columns
        self.data_types = {}

        # Used to store number of enetered rows 
        self.rows = 0

    def __validate_and_set(self, path, extension):
        """
        Description
        ===========
            - Validates path and returuns a tuple => (filedir, filename, extension)

        Opeartions
        ==========

            >>> os.path.splitext("C:\\TC\\a.txt")
            ('C:\\TC\\a', '.txt')
            >>>
            >>> os.path.exists(".")
            True
            >>>
            >>>
            >>> re.match("^\w+(\w+[-_])*\w+$", "dffdfd-ddgg-$")
            >>> re.match("^\w+(\w+[-_])*\w+$", "dffdfd-ddgg-dffd")
            <_sre.SRE_Match object at 0x00000000029FCD50>
            >>>
            >>> re.match("^\w+(\w+[-_])*\w+$", "dffdfd-ddgg_dffd")
            <_sre.SRE_Match object at 0x00000000029FCDC8>
            >>>
            >>> re.match("^\w+(\w+[-_])*\w+$", "dffdfd_ddgg_dffd")
            <_sre.SRE_Match object at 0x00000000029FCD50>
            >>>
            >>> re.match("^\w+(\w+[-_])*\w+$", "dffdfd_ddgg+dffd")
            >>>
        """

        this_filename = datetime.now().strftime("DataSet-%d-%m-%Y-%H%M%S")
        this_dir = '.' # os.path.dirname(os.path.abspath(__file__))

        if path and type(path) is str:
            filedir, file_w_ext = os.path.split(path)
            filename, ext = os.path.splitext(file_w_ext)

            if ext:
                ext = ext.lstrip('.')

                if ext in ['json', 'csv']:
                    extension = ext
                else:
                    extension = 'csv'
            else:
                extension = "csv"

            if not filedir:
                filedir = this_dir

            if not os.path.exists(filedir):
                filedir = this_dir

            if not re.match(r"^\w+(\w+[-_])*\w+$", filename):
                filename = this_filename
                self._Message__warning('Valid file names are: my-data-set, mydataset, my-data_set, mydataset.csv etc, so taking %s.%s' % (filename, extension));
        else:
            filename = this_filename;
            filedir = this_dir

            if not extension in ["json", 'csv']:
                extension = 'csv';

        # Used to store the relative/absolute path of the destination directory
        # This value will be used while creating the JSON/CSV file 
        # If you do not provide file path while instantiation then the current 
        # directory (.) will be used
        self.filedir = filedir

        # Used to store the base name of file (A.py => A)
        self.filename = filename

        # Used to store the extension of the file
        self.extension = extension

        # Repeatedly check for an existence of specified filename, 
        # if it already exists (do not override)
        # and choose another file name by appending numbers like 1, 2, 3 and so...on
        self.__set_names()


    def get_data_type(self, value):
        """
        Description
        ===========
            - It returns the type of data basically the result would be either 'numeric' or 'string'
            - If the passed data is int/float or if contains a sequence of numbers including . (dot)
              the returned value will always be 'numeric' otherwise 'string'.

        Code
        ====
            + Below is the logic of getting the type of data

            >>> import re
            >>>
            >>> numeric_regex = r"^(\d+)$|^(\d+\.\d+)$|^(\d*\.\d+)$|^(\d+\.\d*)$"
            >>> re.match(numeric_regex, "14-08-1992")
            >>> re.match(numeric_regex, "14081992")
            <_sre.SRE_Match object; span=(0, 8), match='14081992'>
            >>> 
            >>> re.match(numeric_regex, "140819.92")
            <_sre.SRE_Match object; span=(0, 9), match='140819.92'>
            >>> re.match(numeric_regex, "140819.")
            <_sre.SRE_Match object; span=(0, 7), match='140819.'>
            >>> re.match(numeric_regex, ".8855")
            <_sre.SRE_Match object; span=(0, 5), match='.8855'>
            >>> re.match(numeric_regex, ".")
            >>> re.match(numeric_regex, ".2")
            <_sre.SRE_Match object; span=(0, 2), match='.2'>
            >>> re.match(numeric_regex, "4")
            <_sre.SRE_Match object; span=(0, 1), match='4'>
            >>> 
        """

        numeric_regex = r"^(\d+)$|^(\d+\.\d+)$|^(\d*\.\d+)$|^(\d+\.\d*)$"
        
        if re.match(numeric_regex, str(value)):
            _type = 'numeric';
        else:
            _type = 'string';

        return _type;


    def get_value_for(self, rowno, colname, max_col_len):
        """ 
        Description
        ===========
            - Returns the value entered on console
        """

        s = "[DATA ENTRY] <row: " + str(rowno) + "> "
        l = len(s) + max_col_len + 4
        f = ("%-" + str(l) + "s : ") % (s + " " + colname)
        value = input(f).strip()

        _type = self.get_data_type(value)
        if colname in self.data_types:
            """
                {
                    'fullname': 'string',
                    'age': 'numeric'
                }
            """

            current_type = self.data_types[colname]

            if _type != current_type:
                if self.data_types[colname] == "numeric":
                    self._Message__warning('Previously this column was numeric, now it is of type string')
                    self.data_types[colname] = _type # Set to string
        else:
            self.data_types[colname] = _type

        return value


    def set_container(self):
        """
        Description
        ===========
            - Asks user to enter data for each rows, column by column 
            - Finally sets the container attribute of the class
        """

        ask_for_data_entry = True
        done = False

        if self.__states.get('start'):
            if self.__states.get('set_column_names'):
                done = True
            else:
                self._Message__warning("You are directly trying to invoke, set_container() method"
                    ", please call start() => set_column_names() methods first")
        else:
            self._Message__warning("You are directly trying to invoke, set_container() method"
                    ", please call start() method first")

        if done:
            satisfied = False
            rowno = 1
            equals =  "=" * 50
            msg = "\n" + equals + "\nDo you want to add 1 more row / view data (y/n/v): "
            max_col_len =  max(self.collens)

            while not satisfied:
                if ask_for_data_entry:
                    for colname in self.columns:
                        value = self.get_value_for(rowno, colname, max_col_len)

                        if colname in self.container:
                            self.container[colname].append(value)
                        else:
                            self.container[colname] = [value]


                inp = (input(msg).strip()).lower()

                if inp == 'y' or inp == 'yes':
                    rowno += 1
                    print(equals)
                    ask_for_data_entry = True
                    continue # To continue with entering data for next row
                elif inp.lower() == 'v' or inp.lower() == 'view':
                    self.__create() # Recreation of DataFrame with newly entered data
                    self._Message__data(self.df)
                    viewed = True
                    ask_for_data_entry = False
                    continue
                else:
                    # This is just to make the code meaningful even break can also be used
                    nmtc = no_or_mistakenly_typed_confirmation = input("Is this mistakenly typed (y/n): ").strip()

                    if(nmtc.lower() == "n" or nmtc.lower() == "no"):
                        self.rows = rowno
                        satisfied = True
                    elif not(nmtc.lower() == 'y' or nmtc.lower() == 'yes'):
                        self._Message__warning("This is for your help, just type proper value to exit/continue")
                    else:
                        rowno += 1

                    print(equals) 
                    ask_for_data_entry = True

            self.__states["set_container"] = True
            return True  # Success
        else:
            return False # Failure


    def set_column_names(self):
        """
        Description
        ===========
            - Asks user to enter the name of columns that will appear in csv 
              or (as keys in json object) 
        """

        if self.__states.get('start', None):
            cols = self.total_columns # To short the name (value of cols >= 1)
            
            d = {
                1: '1st',
                2: '2nd',
                3: '3rd'
            }

            f = str(len(str(cols)) + 2) # cols => Total number of columns (extra 2 is for st, nd, rd, th etc.)
            s = "Enter the name of %s column: " % ("%-" + f + "s")
            
            i = 1
            while i <= cols:
                if i <= 3:
                    colname = input(s % (d[i]))
                else:
                    colname = input(s % (str(i) + 'th'))

                if not(re.match(r"^\w*(\w+[-_])*\w+$", colname)):
                    self._Message__warning("Please do not use characters for column names other than "
                            "A-Za-z0-9_-")
                    continue

                if colname in self.columns:
                    self._Message__warning('The entered column name {} has been already choosen '
                           '(please enter another name)'.format(colname))
                    continue

                self.columns.append(colname)
                self.collens.append(len(colname)) 
                i += 1

            self.__states["set_column_names"] = True
            return True # Success
        else:
            self._Message__warning("You are directly trying to invoke, set_column_names() method"
                    ", please call start() method first")
            return False # Failure


    def start(self):
        """
        Description
        ===========
            - Initiates the process of creating dataset, asks for number of columns
            - Valiates entered value (no. of columns), checks if that is a positive 
              integer
            - Checks if it is >= 1
            - Continues to ask user to enter proper value if it does not satisfy the 
              requirement
        """     

        everything_is_ok = False

        while not everything_is_ok:
            cols = input('Enter number of columns that you want in your dataset: ').strip(); 

            if re.match(r"^\d+$", cols):
                cols = int(cols)

                if cols == 0:
                    self._Message__warning("You are looking for 0 column names, please enter >= 1")
                    continue

                everything_is_ok = True
            else:
                self._Message__warning("The entered value doesn't look like a +ve integer "
                    "please enter a valid integer number")

        self.total_columns = cols
        self.__states = {"start": True}

        # Do not need to add \n either at beginning or end while calling messages
        # function like success() / warning() / error() etc.
        self._Message__success("You are successfully done with no. of columns") 

        ret = self.set_column_names()
        if ret:
            self._Message__success("You are successfully done with the column names")
        else:
            self._Message__error("Something unexpected happened")

        ret = self.set_container()
        if ret:
            self._Message__success("You are successfully done with entering data for your dataset")
        else:
            self._Message__error("Something unexpected happened")


    def status_is_ok(self):
        states = self.__states

        if states.get("start", None):
            if states.get("set_column_names", None):
                if states.get("set_container", None):
                    return True
                else:
                    self._Message__warning("You are directly trying to invoke, view() method"
                        ", please call start() => set_column_names() => set_container() methods first")
            else:
                self._Message__warning("You are directly trying to invoke, view() method"
                    ", please call start() => set_column_names() methods first")
        else:
            self._Message__warning("You are directly trying to invoke, view() method"
                ", please call start() method first")

        return False # Failure


    def __create(self, **kwargs):
        self.df = pd.DataFrame(self.container)
        self.df_set = True


    def view(self, add_dashes = True):
        """
        Description
        ===========
            - Shows the entered data as a pandas DataFrame
              by using the data contained in class attribute 'container'

            - The 'container' which is a dictionary can be directly accessed via the class
              instance as below:
              
            >>> kd = KaggleDataSet()
            >>> kd.start() 
            >>> kd.container
        """

        if self.status_is_ok():
            # if not self.df_set:
            self.__create()

            self._Message__data(self.df, add_dashes) # Success, printing data on Terminal
            return True

        return False


    @property
    def dataset(self):
        """
        Description
        ===========
            - Returns pandas.DataFrame object created using 'container' 
              dictionary

            - Returns False if the status is not ok i.e. if you failed to call start(),
              and other methods like set_column_names() etc. (Please check documentation
              for more details)
        """

        if self.status_is_ok() or self.df_set:
            self.__create()
            return self.df
        else:
            return None

    def __set_names(self):
        while os.path.exists(os.path.join(self.filedir, self.filename + '.' + self.extension)):
            # >>> re.match(r'\w+-\d+', "KaggleDataSet-55")
            # <_sre.SRE_Match object; span=(0, 16), match='KaggleDataSet-55'>
            # >>>
            # >>> re.match(r'\w+-\d+', "KaggleDataSet55")
            # >>>
            # >>> re.match(r'\w+-\d+', "Abc-67")
            # <_sre.SRE_Match object; span=(0, 6), match='Abc-67'>
            # >>>

            if re.match(r'\w+-\d+', self.filename):
                base, num = self.filename.split('-');
                num = str(int(num) + 1)
                self.filename = base + '-' + num
            else:
                if "-" in self.filename:
                    count = self.filename.count('-')

                    if count > 1:
                        self.filename = self.filename.replace('-', '_') + '-1'


    def __get_path(self, extension_type):
        # self.__set_names()
        if self.extension == 'csv' and extension_type == 'json':
            self.extension = extension_type

        path = os.path.join(self.filedir, self.filename + '.' + self.extension)
        return path


    def to_csv(self, index=False, **kwargs):
        """
        Description
        ===========
            - Creates CSV file containing the entered data from Terminal
            - Uses the value of attribute named 'container' for creating DataFrame
        """

        csv_path = self.__get_path('csv')
        self.df.to_csv(csv_path, index=index, **kwargs)
        self._Message__success('CSV file is successfully saved as %s' % (csv_path))


    def to_json(self, index=False, **kwargs):
        """
        Description
        ===========
            - Creates JSON file containing the enetered data from Terminal
            - Uses the value of attribute named 'container' for creating DataFrame
        """
        json_path = self.__get_path('json')
        self.df.to_json(json_path, **kwargs)
        self._Message__success('JSON file is successfully saved as %s' % (json_path))



