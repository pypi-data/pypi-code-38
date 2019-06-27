# this will compare data formats between database and xml file and fix it in database

import pyodbc
import yaml
from lxml import etree as et
import pandas as pd


with open('config.yml', 'r') as conf:
    settings = yaml.load(conf)

conn = pyodbc.connect(driver="{SQL Server Native Client 11.0}", server=settings['s'], database=settings['db'], uid=settings['u'], pwd=settings['p'])
curs = conn.cursor()


def check_data_type(datum):
    """
    This function checks type of value because pymssql cannot distinguish int from float
    :param datum: Value to be checked
    :return:
    """
    if datum == '7':
        return 'float'
    elif datum == '4':
        return 'int'
    elif datum == '5':
        return 'bigint'
    elif datum == '2':
        return 'varchar(max)'
    else:
        print("Undefined data type in source data for: ", datum)  # if nothing then string


def get_info_from_database(table_prefix):
    tables_with_types = {}
    curs.execute("select name from sys.tables where name like '" + table_prefix + "%' order by 1;")
    table_list = [str(*i) for i in curs.fetchall()]
    for tn in table_list:
        sql = "select COLUMN_NAME ,DATA_TYPE from information_schema.columns where TABLE_NAME = '" + tn + "'"
        curs.execute(sql)
        table_data_types = {i[0]: i[1] for i in curs.fetchall()}
        tables_with_types[tn] = table_data_types
    return tables_with_types


def get_info_from_metadata(project_id):
    doc = et.parse(r'C:/Projects/Website-ASP.NET/pub/ReportData/Metadata/' + project_id + '.xml')
    tables = doc.xpath("//SurveyDataset[@name='Original Tables']/tables/table")
    tables_with_types = {table.attrib['DbTableSuffix']: {variable.attrib['name']: variable.attrib['dataType'] for variable in table.xpath('variable')} for table in tables}
    return tables_with_types


def compare_formats(db_formats, metadata_formats):
    differences = []
    for key, values in db_formats.items():
        table_suffix_cutoff = [i for i, t in enumerate(reversed(key)) if t == '_'][0]
        for k, v in values.items():
            try:
                if k in metadata_formats[key[-table_suffix_cutoff:]].keys():
                    if check_data_type(metadata_formats[key[-table_suffix_cutoff:]][k]) != v:
                        differences.append([key, k, v, 'should be:', check_data_type(metadata_formats[key[-table_suffix_cutoff:]][k])])
                        print('Difference found in {}, column format {} should be {}'.format(key, k, v))
                else:
                    if 'char' not in v:
                        print('Variable {} is not in metadata and not char.'.format(k))
                        differences.append([key, k, v, 'should be:', 'varchar(255)'])
            except KeyError as e:
                print(f'error: {e}')
    return differences


def fix_formats_in_db(format_differences):
    print("Fixing formats!!!")
    for diff in format_differences:
        try:
            curs.execute("ALTER TABLE " + diff[0] + " ALTER COLUMN " + diff[1] + " " + diff[4] + ";")
            conn.commit()
        except Exception as e:
            print("Error occurred while alter statement was run!!!", e, "On:", diff[0] + " " + diff[1] + " " + diff[4])

    conn.commit()


def main():
    db_formats = get_info_from_database(settings['table_prefix'])
    metadata_formats = get_info_from_metadata(settings['project_id'])
    format_differences = compare_formats(db_formats, metadata_formats)
    if settings['automatic_fix']:
        fix_formats_in_db(format_differences)
    else:
        pd.DataFrame(format_differences).to_csv('diff.csv', index=False)
        print('All done!')


if __name__ == '__main__':
    main()
