import requests
import pandas as pd
import sys
import csv
import os
from collections import defaultdict
years = sys.argv[-1]

def getData():

    acs_supp = pd.read_csv('Z:\\ACS_Supplemental\\Raw Data\\'+years+'\\OutputAPI_data\\ACS_Supplemental_raw_data.csv', sep=',', header=0, index_col=None, encoding='ISO-8859-1', converters={'Geo': str})

    header_list = []

    for ind, col in enumerate(acs_supp.columns):
        if col == 'NAME':
            col = col
        elif col == 'SUMLEVEL':
            col = col
        elif col == 'Geo':
            col = col
        elif col[-1] == 'M':
            col = col[:[index for index, j in enumerate(col) if j == "_"][-1]] + col[-4:-1] + 's'
        elif col[-1] == 'E':
            col = col[:[index for index, j in enumerate(col) if j == "_"][-1]] + col[-4:-1]

        header_list.insert(ind, col)

    acs_supp.columns = header_list

    for index, i in enumerate(acs_supp):
        acs_supp[i].replace('-555555555', '*****', inplace=True)
        acs_supp[i].replace('-666666666', '', inplace=True)
        acs_supp[i].replace('-333333333', '***', inplace=True)
        acs_supp[i].replace('-222222222', '**', inplace=True)

    acs_supp = acs_supp[[col for col in acs_supp.columns if 'MA' not in col]]
    acs_supp = acs_supp[[col for col in acs_supp.columns if 'EA' not in col]]

    for ind, col in enumerate(acs_supp.columns):
        if col[-1] == 's':
            for i, var in enumerate(acs_supp[col]):
                if var != '*****' and var != '***' and var != '**' and not pd.isnull(var) and col[:7] != 'K200103':
                    acs_supp.loc[i, col] = "{0:.2f}".format(float(var) / 1.65, 2)

    for index, column in enumerate(acs_supp.columns):
        if column[-1] == 's':
            for i, var in enumerate(acs_supp[column]):
                var1 = str(var)
                if var1 != '*****' and var1 != '***' and var1 != '**' and '.0' in var1[-2:]:
                    acs_supp.loc[i, column] = var1[:-2]

    for index1, column1 in enumerate(acs_supp.columns):
        if column1[-1] == 's':
            for i, var2 in enumerate(acs_supp[column1]):
                if var2 != '*****' and var2 != '***' and var2 != '**' and not pd.isnull(var2) and column1[:7] != 'K200103':
                    #print(i, column1, var2)
                    var3 = int(var2)
                    acs_supp.loc[i, column1] = '{:,}'.format(var3)
                    #acs_supp.loc[i, column] = '{:,}'.format(str(var1))

    for ind2, col2 in enumerate(acs_supp.columns):
        if col2[-1] != 's' and col2 != 'NAME' and col2 != 'SUMLEVEL' and col2 != 'Geo':
            for i, var1 in enumerate(acs_supp[col2]):
                var = str(var1)
                acs_supp.loc[i, col2] = var.rstrip('0').rstrip('.') if '.' in var else var

    acs_supp["K200001001s"] = ""
    acs_supp["K200002001s"] = ""

    acs_supp.loc[acs_supp.SUMLEVEL == 10, 'Geo'] = "0"

    acs_supp = acs_supp.rename(columns={'SUMLEVEL': 'SUMLEV'})
    acs_supp["SUMLEV"] = acs_supp.SUMLEV.map("{:03}".format)
    acs_supp['SUMLEV'] = 'SL' + acs_supp['SUMLEV']
    return acs_supp

def getgeoData():

    all_geos = requests.get('http://api.census.gov/data/'+years+'/acsse/geography.json')
    if all_geos.status_code == 200:
        all_data_new = all_geos.json()

    row = []

    for i in all_data_new['fips']:
                row.append([i['name'], i['geoLevelId']])

    geo_desc_df = pd.DataFrame(row, columns=["name", "geoLevelId"])

    geo_desc_df['name'] = geo_desc_df['name'].str.replace(' ', '+')
    geo_desc_df['geoLevelId'] = 'SL' + geo_desc_df['geoLevelId']

    return geo_desc_df

def getvariables():
    all_vars = requests.get('http://api.census.gov/data/' + years + '/acsse/variables.json')
    if all_vars.status_code == 200:
        all_vars_new = all_vars.json()

    row = [''] * 4

    exclude_list = ['for', 'in', 'NAME', 'SUMLEVEL']
    main = [['variable', 'label', 'type', 'concept']]
    for key, value in all_vars_new['variables'].items():
        if key in exclude_list or value['concept'] == 'Selectable Geographies':
            continue
        row[0] = key
        for k, l in value.items():
            if k == 'label':
                row[1] = l
            elif k == 'predicateType':
                row[2] = l
            elif k == 'concept':
                row[3] = l

        main.append(row)
        row = [''] * 4

    var_desc_df = pd.DataFrame(main[1:], columns=main[0])

    var_desc_df['variable2'] = ''
    for ind, i in enumerate(var_desc_df['variable']):
        if i[-1] == 'M':
            i = i[:[index for index, j in enumerate(i) if j == "_"][-1]] + i[-4:-1] + 's'
        elif i[-1] == 'E':
            i = i[:[index for index, j in enumerate(i) if j == "_"][-1]] + i[-4:-1]
        var_desc_df.loc[ind, 'variable2'] = i

    var_desc_df = var_desc_df[var_desc_df.variable2.str.contains("MA") == False]

    var_desc_df = var_desc_df[var_desc_df.variable2.str.contains("EA") == False]

    var_desc_df[['org_name', 'table_label']] = var_desc_df['concept'].str.split(".", expand=True)

    var_desc_df = var_desc_df.reset_index()

    var_desc_df['new_table_name'] = ''

    for index1, a in enumerate(var_desc_df['variable2']):
        if a[-1] == 's':
            a = a[:[index for index, j in enumerate(a)][-4]] + '_se'
        else:
            a = a[:[index for index, j in enumerate(a)][-3]]
        var_desc_df.loc[index1, 'new_table_name'] = a

    return var_desc_df

def writevariables():

    var_desc_df = getvariables()

    var_desc_df1 = var_desc_df[['variable2', 'label']]

    var_desc_df1['indent'] = var_desc_df1.label.str.count('!!') + 1

    for index, i in var_desc_df1.iterrows():
        if i['variable2'][-4:-1] == '001' or i['variable2'][-3:] == '001':
            var_desc_df1.loc[index, 'indent'] = '0'
        else:
            var_desc_df1.loc[index, 'indent'] = i['indent']

    var_desc_df1['label3'] = var_desc_df1['label'].apply(lambda x: x.split('!!')[-1])

    for index2, e in var_desc_df1.iterrows():
        if 's'[-1] in e['variable2']:
            var_desc_df1.loc[index2, 'label2'] = 'Std. Error: ' + e['label3']
        else:
            var_desc_df1.loc[index2, 'label2'] = e['label3']

    var_desc_df1 = var_desc_df1[['variable2', 'label2', 'indent']]

    b = pd.DataFrame({'variable2': ['K200001001s', 'K200002001s'], 'label2' : ['Std. Error: Total:', 'Std. Error: Total:'], 'indent' : [0, 0]})

    var_desc_df1 = b.append(var_desc_df1, ignore_index=True)

    var_desc_df1 = var_desc_df1[['variable2', 'label2', 'indent']]
    var_desc_df1.to_csv('Z:\\ACS_Supplemental\\Input Scripts\\'+years+'\\Config Files\\variable_descriptions.txt', index=False,header=None, mode='a')

    return var_desc_df1

def geoTypes():

    geo_desc_df = getgeoData()
    geo_desc_df = geo_desc_df.rename(columns={'name': 'TYPE'})
    acs_supp_transformed = getData()
    geo_results = acs_supp_transformed[['Geo', 'NAME', 'SUMLEV']]
    geo_results = geo_results.rename(columns={'Geo': 'FIPS'})

    merged_left = pd.merge(left=geo_results, right=geo_desc_df, how='left', left_on='SUMLEV', right_on='geoLevelId')

    merged_left = merged_left[['FIPS', 'NAME', 'TYPE', 'SUMLEV']]

    merged_left.TYPE.replace(['us'],['Nation'], inplace=True)

    merged_left['TYPE'] = merged_left['TYPE'].str.replace('+', ' ')
    merged_left['TYPE'] = merged_left['TYPE'].str.title()

    var_desc_df1 = getvariables()

    var_desc_df2 = var_desc_df1['new_table_name'].tolist()

    myset = set(var_desc_df2) #unique the vars in list

    var_desc_df2 = list(myset) #return set to list

    var_desc_df2.extend(["K200001_se", "K200002_se",])

    geoID1 = []

    for i in var_desc_df2:
        temp = pd.DataFrame({'col1': i,
                          'col2': merged_left['SUMLEV'].drop_duplicates()
                          })
        geoID1.append(temp)

    geoID = pd.concat(geoID1)

    geoID.to_csv('Z:\\ACS_Supplemental\\Input Scripts\\'+years+'\\Config Files\\geo_divisions_by_dataset_ID.txt', index=False, header = False, mode='a')

    merged_left.to_csv('Z:\\ACS_Supplemental\\Input Scripts\\'+years+'\\Config Files\\all_geotypes_and_sumlev.csv', index=False, mode='a')

def writeData():

    acs_supp_transformed = getData()

    var_desc_df = getvariables()

    var_desc_df2 = var_desc_df['new_table_name'].tolist()

    myset = set(var_desc_df2) #unique the vars in list

    var_desc_df2 = list(myset) #return set to list

    var_desc_df['concept'] = var_desc_df['concept'].str.replace("/", " ")

    var_desc_df[['org_name', 'table_label']] = var_desc_df['concept'].str.split(".", expand=True)

    var_desc_df['table_label'] = var_desc_df['table_label'].str.lstrip()

    var_desc_df_dict = var_desc_df.set_index('new_table_name')['table_label'].to_dict()

    var_desc_df_dict['K200001_se'] = 'Unweighted Sample Count of the Population'
    var_desc_df_dict['K200002_se'] = 'Unweighted Sample Housing Units'

    dataDic = defaultdict(list)
    for ind, i in enumerate(acs_supp_transformed.columns):
        if i[-1] == 's':
            dataDic[i[:-4] + '_se'].append(i)
        elif (i[-1] != 's' and i != 'SUMLEV' and i != 'Geo') and i != 'NAME':
            dataDic[i[:-3]].append(i)

    for k, v in dataDic.items():
        cols = ['SUMLEV', 'Geo']+ v
        acs_supp_transformed[cols].to_csv(
                'Z:\\ACS_Supplemental\\Processing csv Files\\' + years + '\\' + k + '_' + var_desc_df_dict[k] + '.csv',index=False, mode='a')

    with open('Z:\\ACS_Supplemental\\Input Scripts\\' + years + '\\Config Files\\files_list.txt', 'r+',
              newline='') as f:
        w = csv.writer(f)
        for path, dirs, files in os.walk('Z:\\ACS_Supplemental\\Processing csv Files\\' + years + '\\'):
            sort = sorted(files, key=lambda x: ('_se' in x, x))
            for filename in sort:
                w.writerow([filename])

def processFiles():
    getData()
    getgeoData()
    writevariables()
    geoTypes()
    writeData()


if __name__ == '__main__':
    processFiles()


