import pandas as pd
import os
import numpy as np
from fuzzywuzzy import fuzz
import getpass
import sys

pd.set_option('display.max_rows', 300)


def convert():
    print("CWD: " + os.getcwd())
    #  Project/data information input.
    project_number = input("What is the project number? (XXXXX): ")
    project_name = input("What is the project name? (no-spaces): ")
    while True:
        matrix = input("What matrix are you importing? (soil, sediment, water, gas, leachate): ").lower()
        if matrix in ['soil', 'sediment', 'water', 'gas', 'leachate']:
            break
        else:
            print("Please try again.")
    client = input("Who is the client? (no-spaces): ")
    output_file = "{0}_{1}_{2}_{3}.xlsx".format(project_number,
                                                client,
                                                project_name,
                                                matrix)

    #  Required columns created for dataframe
    df_datin = pd.DataFrame(columns=['StationName', 'FieldSampleID', 'QCSampleCode',
                                     'SampleDate_D', 'SampleMatrix', 'ParameterName',
                                     'Value', 'ReportingUnits', 'SampleTop',
                                     'SampleBottom', 'DepthUnits', 'Description'])

    #  Generate list of files to process, files should be in a subfolder
    #  named after the chosen matrix
    try:
        files = []
        files = [file for file in os.listdir('./{}'.format(matrix))
                 if file != output_file   #Do not process output file
                 and os.path.splitext(file)[0][0] != '~'   # Do not process hidden files
                 and (file.endswith('xlsx') or file.endswith('xls') or file.endswith('csv'))]
    except FileNotFoundError or UnboundLocalError:
        print("\n*** Import files should be in one of the following sub folders:")
        print("\n\t'Soil'\n\t'Sediment'\n\t'Water'\n\t'Gas'\n\t'Leachate'")
        print("\n\n*** OPERATION ABORTED - no files found ***")
        sys.exit()

    print("\n\nFiles being processed:\n\n")
    for file in files:
        print(file)
        # Location of source files
        cwd = os.getcwd()
        try:
            input_filepath = os.path.join(cwd, matrix, file)
        except FileNotFoundError:
            input_filepath = os.path.join(cwd, matrix.capitalize(), file)
        
        # Create dataframe from file
        try:
            df1 = pd.read_excel(input_filepath, header=None, sheet_name='Sheet1')
            df2 = pd.read_excel(input_filepath, header=None, sheet_name='Sheet2')
            if pd.isnull(df1[0][1]):
                df = df2.T
            elif pd.isnull(df2[1][0]):
                df = df1
        except:
            df = pd.read_excel(input_filepath, header=None)
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
            df_params.loc[2:,x] = df_params.loc[0,x]
        df_params.drop([0,1], inplace=True)
        df_params_melted = pd.melt(df_params, id_vars=field_list,
                                   value_vars=ref_list,
                                   var_name='ref',
                                   value_name='ParameterName')

#  Create melted datafarme with reference column and Units info
        df_units = df.copy()
        for x in range(10, num_cols):
            df_units.loc[2:, x] = df_units.loc[1, x]
        df_units.drop([0,1], inplace=True)
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
        df_datin = pd.concat([df_datin, df_values_melted], ignore_index=True, sort=False)

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

# -----------
#  Matching parameter names
# -----------

    #  Get username of user on their specific computer
    username = getpass.getuser()
    dat_filepath = ("/Users/{}/Dropbox (Core6)/- references/"
                    "Database/Data Extraction/"
                    "datnames.xlsx".format(username))
    df_datnames = pd.read_excel(dat_filepath, header=None)
    col_size = df_datnames.columns.size

    tabnames_set = set(df_datin.ParameterName)

    # Compares each parameter name with names in datnames.xlsx on Dropbox,
    # determines the match percentage, and keeps the highest one.
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



    # Print matches for user to review
    print("\n\nParameter Name Matches:\n\n")
    df_match1 = pd.DataFrame(set(match_list1), columns=['Old Param Name', 'Match %', 'New Param Name'])
    if matrix == 'soil':
        df_match1["New Param Name"].replace('LEPH[swv]?$', 'LEPHs', regex=True, inplace=True)
        df_match1["New Param Name"].replace('HEPH[swv]?$', 'HEPHs', regex=True, inplace=True)
        df_match1["New Param Name"].replace('VPH[swv]?$', 'VPHs', regex=True, inplace=True)
    elif matrix == 'water':
        df_match1["New Param Name"].replace('LEPH[swv]?$', 'LEPHw', regex=True, inplace=True)
        df_match1["New Param Name"].replace('HEPH[swv]?$', 'HEPHw', regex=True, inplace=True)
        df_match1["New Param Name"].replace('VPH[swv]?$', 'VPHw', regex=True, inplace=True)
    elif matrix == 'gas':
        df_match1["New Param Name"].replace('LEPH[swv]?$', 'LEPHv', regex=True, inplace=True)
        df_match1["New Param Name"].replace('HEPH[swv]?$', 'HEPHv', regex=True, inplace=True)
        df_match1["New Param Name"].replace('VPH[swv]?$', 'VPHv', regex=True, inplace=True)
    print(df_match1)

    # Matches with lower match percentage should be scrutinized.
    print("\n\n***Double check these matches (lower matching percentage):\n\n")
    df_match2 = pd.DataFrame(set(match_list2), columns=['Old Param Name', 'Match %', 'New Param Name'])
    if matrix == 'soil':
        df_match2["New Param Name"].replace('LEPH[swv]?$', 'LEPHs', regex=True, inplace=True)
        df_match2["New Param Name"].replace('HEPH[swv]?$', 'HEPHs', regex=True, inplace=True)
        df_match2["New Param Name"].replace('VPH[swv]?$', 'VPHs', regex=True, inplace=True)
    elif matrix == 'water':
        df_match2["New Param Name"].replace('LEPH[swv]?$', 'LEPHw', regex=True, inplace=True)
        df_match2["New Param Name"].replace('HEPH[swv]?$', 'HEPHw', regex=True, inplace=True)
        df_match2["New Param Name"].replace('VPH[swv]?$', 'VPHw', regex=True, inplace=True)
    elif matrix == 'gas':
        df_match2["New Param Name"].replace('LEPH[swv]?$', 'LEPHv', regex=True, inplace=True)
        df_match2["New Param Name"].replace('HEPH[swv]?$', 'HEPHv', regex=True, inplace=True)
        df_match2["New Param Name"].replace('VPH[swv]?$', 'VPHv', regex=True, inplace=True)
    print(df_match2)

    # Replace ParameterName column with matched names
    df_datin.ParameterName = df_datin.ParameterName.map(param_dict)

    if matrix == 'soil':
        df_datin.ParameterName.replace('LEPH[swv]?$', 'LEPHs', regex=True, inplace=True)
        df_datin.ParameterName.replace('HEPH[swv]?$', 'HEPHs', regex=True, inplace=True)
        df_datin.ParameterName.replace('VPH[swv]?$', 'VPHs', regex=True, inplace=True)
    elif matrix == 'water':
        df_datin.ParameterName.replace('LEPH[swv]?$', 'LEPHw', regex=True, inplace=True)
        df_datin.ParameterName.replace('HEPH[swv]?$', 'HEPHw', regex=True, inplace=True)
        df_datin.ParameterName.replace('VPH[swv]?$', 'VPHw', regex=True, inplace=True)
    elif matrix == 'gas':
        df_datin.ParameterName.replace('LEPH[swv]?$', 'LEPHv', regex=True, inplace=True)
        df_datin.ParameterName.replace('HEPH[swv]?$', 'HEPHv', regex=True, inplace=True)
        df_datin.ParameterName.replace('VPH[swv]?$', 'VPHv', regex=True, inplace=True)

    # Convert all values in df_datin to string type
    df_datin = df_datin.astype(str)
   
    # Re-order columns
    df_datin = df_datin[['StationName', 'FieldSampleID', 'QCSampleCode',
                                     'SampleDate_D', 'SampleMatrix', 'ParameterName',
                                     'Value', 'ReportingUnits', 'SampleTop',
                                     'SampleBottom', 'DepthUnits', 'Description',
                                     'SiteName']]

     #  Write dataframe to Excel file.
    writer = pd.ExcelWriter(output_file)
    df_datin.to_excel(writer, 'sheet1', index=None)
    writer.save()
    print("\n\n{} import file successfully created!".format(matrix.capitalize()))






