import pandas as pd
import os
import sys
import chardet


class TextToCsvConverter:
    '''
    This class contains all the methods required to convert txt file to csv and change certain
    parameters like headers, seperators etc
    '''

    def __init__(self, section, logger_obj):
        self.config = section
        self.logger_obj = logger_obj

    # -------------------------------------------------------------------------
    #    Args: section_list : list of dictionary keys to be validated
    #    Desc: This function is used validate config information
    # -------------------------------------------------------------------------
    def check_required_field_exists(self, section_list=None):
        try:
            if section_list == None:
                section_list = self.config.keys()
            for section in section_list:
                for field in self.config[section].keys():
                    if field.split('_')[-1] == 'optional':
                        continue
                    elif len(self.config[section][field]) == 0:
                        message = "Field:{0} field in section {1} is not populated".format(field, section)
                        return False, message
            return True, "Fields have been validated successfully"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: flag:Boolean
    #           message: String to be output to the log file
    #    Desc: This function is used check output after calling each method
    # -------------------------------------------------------------------------
    def check_flag(self, flag, message):
        if not flag:
            self.logger_obj.error(message)
            sys.exit()
        else:
            self.logger_obj.info(message)
        return

    # -------------------------------------------------------------------------
    #    Args: section_list : list of keys to be validated
    #    Desc: This function is used to check if file exists
    # -------------------------------------------------------------------------
    def file_exists(self, section_list):
        try:
            if section_list == None:
                section_list = self.config.keys()
            for section in section_list:
                for field in self.config[section].keys():
                    if os.path.exists(self.config[section][field]):
                        continue
                    else:
                        return False, "Please enter correct path information in {}:field".format(field)
            return True, "Paths provided are valid"
        except Exception as e:
            return False, e.__str__()

    # -------------------------------------------------------------------------
    #    Args: txt : txt key in config dictionary
    #          file_path : txt file path
    #    Desc: This function is used to check if file contains data
    # -------------------------------------------------------------------------
    def verify_file_size(self, txt, file_path):
        try:

            text_sep = txt['file_seperator']
            if txt['header_available_in_file'] == 'yes':
                header_value = 0
            else:
                header_value = None
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
            df = pd.read_csv(file_path, sep=text_sep, header=header_value, encoding=result['encoding'], error_bad_lines=False)
            if not header_value:
                file_header = list(df.columns.values)
            if len(df) == 0:
                return False, "There is no data present in file", None
            else:
                return True, "File size Validated successfully", file_header
        except Exception as e:
            return False, e.__str__(), None

    # -------------------------------------------------------------------------
    #    Args: headers : expected headers in file
    #          txt_file_header : headers present in text file
    #    Desc: This function is used to check if the txt file contains expected headers
    # -------------------------------------------------------------------------
    def verify_columns_present(self, headers, txt_file_header):
        try:
            req_columns = headers.replace(' ', '').split(',')
            if len(req_columns) != len(txt_file_header):
                return False, "No of columns in txt file is different from columns provided in expected_headers field"
            num_missing_columns_txt_file = len(set(req_columns) - set(txt_file_header))
            num_additional_columns_txt_file = len(set(txt_file_header) - set(req_columns))
            if not num_missing_columns_txt_file and not num_additional_columns_txt_file:
                return True, "Columns validated Successfully"
            else:
                return False, "Missing columns in txt file:{} \n Extra columns in txt file: {}".format(str(set(txt_file_header) - set(req_columns)), str(set(req_columns) - set(txt_file_header)))
        except Exception as e:
            return False, e.__str__(), None

    # -----------------------------------------------------------------------------------
    #    Args: config : Dictionary containing config information
    #    Desc: This function converts txt file to csv and updates headers if set to 'yes'
    # ------------------------------------------------------------------------------------
    def convert(self, config):
        try:
            source_file = config['path']['source_file']
            destination_path = config['path']['destination_path']
            csv_seperator = config['csv']['seperator']
            csv_headers = config['csv']['headers_optional']
            update_csv_headers = config['csv']['update_header']
            txt_seperator = config['txt']['file_seperator']
            txt_header_available = config['txt']['header_available_in_file']
            if txt_header_available == 'yes':
                header_value = 0
            else:
                header_value = None
            with open(source_file, 'rb') as f:
                result = chardet.detect(f.read())
            df = pd.read_csv(source_file, header=header_value, sep=txt_seperator, encoding=result['encoding'], error_bad_lines=False)
            if update_csv_headers == 'yes':
                df.columns = csv_headers.split(',')
            if os.path.isdir:
                filename = source_file.split('/')[-1]
                filename = filename.replace('.txt', '.csv')
                destination_path = os.path.join(destination_path, filename)
            df.to_csv(destination_path, sep=csv_seperator, index=False)
            return True, "File was converted successfully"
        except Exception as e:
            return False, e.__str__()
