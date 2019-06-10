import pandas as pd
import os
import numpy as np
from fuzzywuzzy import fuzz
import getpass

#  Set pandas to display at least 300 rows in the dataframe
pd.set_option('display.max_rows', 300)


class Convert:
    
    def __init__(self):
        self.output_file = None

    def project_input(self):
        """
        Project/data information input.
        project
        :return: 
        """
        project_number = input("What is the project number? (XXXXX): ")
        project_name = input("What is the project name? (no-spaces): ")
        matrix = input("What matrix are you importing? (soil, water, gas, leachate): ")
        client = input("Who is the client? (no-spaces): ")
        self.output_file = "{0}_{1}_{2}_{3}.xlsx".format(project_number,
                                                    client,
                                                    project_name,
                                                    matrix)
        
    def generate_input_files(self):
        file_list = []
        for file in os.listdir('.'):
            if file.endswith('csv'):
                file_list.append(file)

        field_names_col1 = [
            'Description',
            'QCSampleCode',
            'SampleTop',
            'SampleBottom',
            'DepthUnits',
            'SampleMatrix',
            'StationName',
            'FieldSampleID',
            'SampleDate_D',
            'Parameters']

        field_names_col2 = [
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            'Units']

        df_template = pd.DataFrame()
        df_template[0] = field_names_col1
        df_template[1] = field_names_col2

        # In[180]:

        for file in file_list:
            #  read excel file containing extracted data
            df = pd.read_excel(file, header=None)
            basename, ext = os.path.splitext(file)

            #  Create dataframe with only header labels
            df_field_values = pd.DataFrame(columns=df.columns[3:])

            for i in range(0, 10):
                df_temp = df[df[0] == i].iloc[:, 3:]
                if df_temp.index.size > 0:
                    df_temp.index = [i - 1]
                #  col_names = df.columns[2:]
                df_field_values = pd.concat([df_field_values, df_temp])
            df_field_values.columns = df_field_values.columns - 1

            df_headings = df_template.join(df_field_values, how='outer')
            df_headings.iloc[4, 2:] = 'm'
            if df[2].str.contains('ug/g').any():
                df_headings.iloc[5, 2:] = 'soil'
            else:
                df_headings.iloc[5, 2:] = 'water'
            df_headings.iloc[:, 2:].columns = df_headings.iloc[:, 2:].columns - 1

            df_values = df[(df[2] == 'ug/g') | (df[2] == 's.u.') | (df[2] == 'pH_Units') | (df[2] == 'ug/L')]
            del df_values[0]
            df_values.columns = df_values.columns - 1
            df_final = pd.concat([df_headings, df_values])

            df_final.to_excel(basename + "_dbinput.xlsx", index=False, header=False, sheet_name="Sheet1")

        # In[179]:

        df_final

        # In[84]:

        df_headings = df_template.join(df_field_values, how='outer')

        # In[91]:

        df_values = df[(df[2] == 'ug/g') | (df[2] == 's.u.') | (df[2] == 'pH_Units') | (df[2] == 'ug/L')]

    def setup(self):
        #  Required columns created for dataframe
        df_datin = pd.DataFrame(columns=['StationName', 'FieldSampleID', 'QCSampleCode',
                                         'SampleDate_D', 'SampleMatrix', 'ParameterName',
                                         'Value', 'ReportingUnits', 'SampleTop',
                                         'SampleBottom', 'DepthUnits', 'Description'])
        
    def file_list(self):
        """
        #  Generate list of files to process, files should be in ./source_files
        :return: 
        """
        files = [file for file in os.listdir('./source_files')
                 if file != self.output_file  # Do not process output file
                 and os.path.splitext(file)[0][0] != '~'  # Do not process hidden files
                 and (file.endswith('xlsx') or file.endswith('xls') or file.endswith('csv'))]
        
    def process_data(self):
        for file in files:
            print(file)
            # Location of source files
            cwd = os.getcwd()
            self.output_filepath = os.path.join(cwd, 'source_files', file)

            # Create dataframe from file
            df = pd.read_excel(self.output_filepath, header=None)
            #  Transpose dataframe if required
            if df[0].isin(['FieldSampleID']).any():
                df = df.T
            # Calculate number of columns in the dataframe
            num_cols = len(df.columns)

            #  Modify dataframe to have fields (cols 1-10) and reference #s (cols 11-end) as column headers
            #  The reference column acts as a unique identifier to ensure the Parameters, Values and
            #  units allign correctly when the dataframes are merged.

            df.loc[-1] = df.loc[0][0:9]
            df.loc[-1][10:num_cols] = df.columns[10:num_cols]
            df.columns = df.loc[-1]
            df.loc[1][0:9] = df.columns[0:9]
            del df.columns.name
            df.drop([-1], inplace=True)

            field_list = list(df.columns.values)[:9]
            ref_list = list(df.columns.values)[10:num_cols]

            #  Create melted dataframe with reference column and Values data
            df_values = df.copy()
            df_values.drop([0, 1], inplace=True)
            df_values_melted = pd.melt(df_values, id_vars=field_list,
                                       value_vars=ref_list,
                                       var_name='ref',
                                       value_name='Value')

            #  Create melted dataframe with reference column and Parameter Names
            df_params = df.copy()
            for x in range(10, num_cols):
                df_params.loc[2:, x] = df_params.loc[0, x]
            df_params.drop([0, 1], inplace=True)
            df_params_melted = pd.melt(df_params, id_vars=field_list,
                                       value_vars=ref_list,
                                       var_name='ref',
                                       value_name='ParameterName')

            #  Create melted datafarme with reference column and Units info
            df_units = df.copy()
            for x in range(10, num_cols):
                df_units.loc[2:, x] = df_units.loc[1, x]
            df_units.drop([0, 1], inplace=True)
            df_units_melted = pd.melt(df_units, id_vars=field_list,
                                      value_vars=ref_list,
                                      var_name='ref',
                                      value_name='ReportingUnits')

            #  Add Parameter names column and Units column to values dataframe
            df_values_melted['ParameterName'] = df_params_melted.ParameterName
            df_values_melted['ReportingUnits'] = df_units_melted.ReportingUnits

            #  Delete reference column
            df_values_melted.drop(['ref'], axis=1, inplace=True)

            #  Concatenate values of each file/dataframe to main dataframe "df_datin"
            df_datin = pd.concat([df_datin, df_values_melted], ignore_index=True)
            
    def post_process(self):
        #  Adjustments to df_datin as per database input requirements
        df_datin['SiteName'] = project_number + "_" + project_name
        df_datin.SampleTop.fillna('0', inplace=True)
        df_datin.SampleBottom.fillna('0', inplace=True)
        df_datin.QCSampleCode.fillna('o', inplace=True)
        df_datin.DepthUnits.fillna('m', inplace=True)
        #  Replace dash with NaN
        df_datin.Value.replace("-", np.nan, inplace=True)
        #  Remove all rows where Value column has "NaN"
        df_datin.dropna(subset=['Value'], inplace=True)
        #  Convert date format
        df_datin.SampleDate_D = pd.to_datetime(df_datin.SampleDate_D.astype(str), errors='coerce')
        df_datin.SampleDate_D = df_datin.SampleDate_D.dt.strftime('%m/%d/%Y')
        #  Replaces "nan" with an empty string.
        df_datin.fillna('', inplace=True)
        #  Converts each item in the dataframe into a string.
        df_datin = df_datin.astype(str)
        # Re-order columns
        df_datin = df_datin[['StationName', 'FieldSampleID', 'QCSampleCode',
                             'SampleDate_D', 'SampleMatrix', 'ParameterName',
                             'Value', 'ReportingUnits', 'SampleTop',
                             'SampleBottom', 'DepthUnits', 'Description',
                             'SiteName']]
        
    def match_parameter_names(self):
        username = getpass.getuser()
        dat_filepath = ("/Users/{}/Dropbox (Core6)/- references/"
                        "Database/Data Extraction/parnames/"
                        "datnames.xlsx".format(username))
        df_datnames = pd.read_excel(dat_filepath, header=None)
        col_size = df_datnames.columns.size

        tabnames_set = set(df_datin.ParameterName)

        param_dict = {}
        match_list1 = []
        match_list2 = []
        for param in tabnames_set:
            match = (0, 0, 0)
            col = 0
            while col < col_size and match[1] < 95:
                for dat_param in df_datnames[col]:
                    ratio = fuzz.ratio(str(param), str(dat_param))
                    if ratio > match[1]:
                        dat_name = df_datnames[df_datnames[col] == dat_param][0]
                        match = (param, ratio, dat_name.item())
                col += 1

            match_list1.append(match)
            if match[1] < 80:
                match_list2.append(match)
            param_dict.update({param: match[2]})

        print("\n\nParameter Name Matches:\n\n")
        df_match1 = pd.DataFrame(set(match_list1), columns=['Old Param Name', 'Match %', 'New Param Name'])
        print(df_match1)

        print("\n\n***Check these matches:\n\n")
        df_match2 = pd.DataFrame(set(match_list2), columns=['Old Param Name', 'Match %', 'New Param Name'])
        print(df_match2)

        df_datin.ParameterName = df_datin.ParameterName.map(param_dict)
        
    def write_file(self):
        #  Write dataframe to Excel file.
        writer = pd.ExcelWriter(self.output_file)
        df_datin.to_excel(writer, 'sheet1', index=None)
        writer.save()
        print("output.xlsx file successfully created!")




