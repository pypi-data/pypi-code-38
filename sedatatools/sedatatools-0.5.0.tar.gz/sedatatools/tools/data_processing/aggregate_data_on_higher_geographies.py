import pymssql
import yaml
import pandas as pd
import numpy as np
# from sqlalchemy import create_engine # needed for writing to db since pymssql doesn't support it yet

def get_config():
    with open(config_location +'config.yml', 'r') as conf:
        config = yaml.load(conf)
    return config


def fix_fipses(fetched_data):
    print("Add missing zeros to fips.")
    fix_cols = [c for c in fetched_data.columns if 'FIPS' in c]
    for col in fix_cols:
        fetched_data[col] = fetched_data[col].astype(str)
        for i, val in enumerate(fetched_data[col]):
            if fetched_data[col].isnull().any():
                print("Some null values in column {}, skipping ...".format(col))
            else:
                max_fips_length = fetched_data[col].map(len).max()
                if len(val) < max_fips_length:
                    fetched_data.loc[i, col] = ''.join(['0' for _ in range(max_fips_length - len(val))]) + val

def get_data():
    print("Fetch database data.")
    curs.execute("select name from sys.tables where name like '" + config['projectId'] + "_" + start_level + "%'")
    table_names = curs.fetchall()
    table_suffixes = [tn[0].replace(config['projectId'] + "_" + start_level + "_", '') for tn in table_names]

    table_container_agg = {}
    # load data for lower level to be aggregated
    for suff in table_suffixes:
        curs.execute('SELECT * FROM ' + config['projectId'] + "_" + start_level + "_" + suff)
        fetched_data = pd.DataFrame(data=curs.fetchall(), columns=[col[0] for col in curs.description])
        # fix_fipses(fetched_data)
        table_container_agg[suff] = fetched_data

    # get tables from higher level
        table_container = {}
    #
    if end_level == 'SL010':
        for suff in table_suffixes:
            curs.execute('SELECT * FROM ' + config['projectId'] + "_" + start_level + "_" + suff)
            columns = [col[0] for col in curs.description]
            table_container[suff] = pd.DataFrame(data=np.array(['', '', 'United States', '', 'SL010', '', '', '', '', '', '00', 'United States', '', '', '', '', '', '', '', '00', 'United States', '']), columns=columns)
    else:
        for suff in table_suffixes:
            curs.execute('SELECT * FROM ' + config['projectId'] + "_" + end_level + "_" + suff)
            table_container[suff] = pd.DataFrame(data=curs.fetchall(), columns=[col[0] for col in curs.description])

    return table_container_agg, table_container, table_suffixes

def aggregate_data(table_container_agg):
    print("Aggregate data.")
    # create aggregated dataframes
    for df_name, table_content in table_container_agg.items():
        agg_table = table_content.loc[:, [i for i in table_content.columns if (config['projectId'] in i) or i == 'FIPS']] # TODO if used in other projects remove 'AREA' (and 'AREA' in i)
        if end_level != 'SL010':
            agg_table['FIPS_partial'] = [i[:fips_size_start+fips_size] for i in agg_table.FIPS]
        else:
            agg_table['FIPS_partial'] = '00'
        agg_table.drop('FIPS', axis=1, inplace=True)
        # propper_table = table_content.loc[:, [i for i in table_content.columns if config['projectId'] in i]]
        table_container_agg[df_name] = agg_table.groupby('FIPS_partial').sum().reset_index()

    return table_container_agg

def merge_data(database_values_higher_level, aggregated_data, table_suffixes):
    print("Merge data.")
    table_container_result = {}
    for suff in table_suffixes:
        sys_cols = database_values_higher_level[suff].loc[:, [i for i in database_values_higher_level[suff].columns if config['projectId'] not in i]]
        table_container_result[suff] = pd.merge(sys_cols, aggregated_data[suff], left_on='FIPS', right_on='FIPS_partial')

    return table_container_result


def update_data_in_db(merged_data):
    print("Write to db/csv.")
    for k, v in merged_data.items():
        # try:
        #     curs.execute('drop table ' + config['projectId'] + "_" + end_level + "_" + k)
        # except Exception as e:
        #     print("Error while deleting table " + config['projectId'] + "_" + end_level + "_" + k, e)
        # v.to_sql(config['projectId'] + "_" + end_level + "_" + k, engine)
        v.drop('FIPS_partial', axis=1, inplace=True)
        v.to_csv(config_location + '/' + config['projectId'] + "_" + end_level + "_" + k + ".csv", sep=",", index = False)


def calculate_percentages(aggregated_data):
    for k, v in aggregated_data.items():
        calc_cols = [c for c in v.columns if c != 'FIPS_partial' and c != config['projectId']+'_001_AREA']
        # v['total_surface'] = v.loc[:, calc_cols].sum(axis=1)
        for col in calc_cols:
            area_col = [c for c in v.columns if c[-5:] == '_AREA'][0]
            v[col.replace('AREA', 'PROP')] = v[col]/v[area_col]*100
    return aggregated_data


if __name__ == '__main__':
    print("Start ... ")
    config_location = 'E:/LEHD/processing data/config_files/2014_tract_only/'
    start_level = 'SL040'
    end_level = 'SL010'
    fips_size_start = 0
    fips_size = 2
    config = get_config()
    if config['trustedConnection']:
        con = pymssql.connect(host=config['server'], database=config['dbname'])
    else:
        con = pymssql.connect(host=config['server'], database=config['dbname'], user=config['user'],
                              password=config['password'])

    # engine = create_engine('mssql+pyodbc://XXXXXXXXXX:XXXXXXX@prime/NHS')

    curs = con.cursor()

    # 1. get values for lower and upper levels from database
    database_values_lower_level, database_values_higher_level, table_suffixes = get_data()

    # 2. create aggregated dataframes from lower levels
    aggregated_data = aggregate_data(database_values_lower_level)

    # 2a. remove this step if you don't have to calculate percentages
    # aggregated_data = calculate_percentages(aggregated_data)

    # 3. merge aggregated dataframes with higher level dfs
    merged_data = merge_data(database_values_higher_level, aggregated_data, table_suffixes)

    # 4. write changes into database
    update_data_in_db(merged_data)
    