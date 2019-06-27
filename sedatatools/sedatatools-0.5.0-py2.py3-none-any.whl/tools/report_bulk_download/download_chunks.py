"""
V 1.0
"""

import requests
from lxml import etree as et
import argparse
import time
import pickle

from loguru import logger

from os import remove


def get_table_names_from_db(mf):
    docs = et.parse(mf)
    tables = docs.xpath('//table')
    tables_dic = {t.attrib['name']: t.attrib['DbTableSuffix'] for t in tables}
    return tables_dic


def extract_cmd_arguments():
    """
    Get and parse CMD arguments,

    Example: "C2000" "SF1" "SL795" "C:\Projects\Website-ASP.Net\pub\ReportData\Metadata\C2000 Metadata v2.6.2.xml" c:\vedad\ 1

    :return:
    """
    # argument parser
    parser = argparse.ArgumentParser(
        description='Download data from reports system in chunks.',
        epilog=r'example usage: py download_chunks.py "C2000" "SF1" "SL795" "C:\Projects\Website-ASP.Net\pub\ReportData\Metadata\C2000 Metadata v2.6.2.xml" "c:\\vedad\\" 1 False')
    parser.add_argument('survey_name', help='Survey name e.g. ACS2016_5yr.')
    parser.add_argument('data_set_abbreviation', help='Data set abbreviation.')
    parser.add_argument('geo_levels', help='Geo levels for which to download files.')
    parser.add_argument('metadata_file', help='Full path to metadata file.')
    parser.add_argument('output_dir', help='Full path to output dir.')
    parser.add_argument('step', help='Number of tables in chunks.')
    parser.add_argument('GUID_v', help='Set to True if you want to get GUIDs instead of the var names')

    args = parser.parse_args()

    return args.survey_name, args.data_set_abbreviation, args.geo_levels.split(','), args.metadata_file, args.output_dir, int(args.step), \
           'Guid=1&' if args.GUID_v == 'True' else ''


def get_tables_list(metadata_file_path):
    doc = et.parse(metadata_file_path)
    # get all the variables from the data set
    table_list = list(doc.xpath("//SurveyDataset[@abbreviation='{}']/tables/table/@name".format(ds)))
    # exclude standard error variables
    table_list = [el for el in table_list if '_se' not in el]

    return table_list


def chunk_tables_list_by_step(list_of_tables_to_chunk, step_):
    start_end = []
    # you can increase this number if you need it.
    # Step will download n number of variable in one file (in this case: 500)
    # step = 200
    st = 0
    for n, _ in enumerate(list_of_tables_to_chunk):
        if n % step_ == 0 and n != 0 and step_ > 1:  # step > 1 to exclude cases when only one variable is needed
            start_end.append([list_of_tables_to_chunk[st], list_of_tables_to_chunk[n]])
            st = n + 1
            # for the last iteration, if less than n number
            if (len(list_of_tables_to_chunk) - n) < step_:
                start_end.append([list_of_tables_to_chunk[n + 1], list_of_tables_to_chunk[len(list_of_tables_to_chunk) - 1]])
                break
        elif step_ == 1:
            start_end.append([list_of_tables_to_chunk[st], list_of_tables_to_chunk[st]])
            st = n + 1

    return start_end


def get_list_of_finished_variables() -> list:
    try:
        finished_vars = pickle.load(open('finished_vars.pkl', 'rb'))
        logger.info(f'starting from {finished_vars[-1]}')
    except (OSError, IOError):
        logger.info('Starting from the beginning.')
        finished_vars = []

    return finished_vars


def download_files(geo_name, table_list, database_table_names, finished_vars):

    for i in geo_name:
        for ind, se in enumerate(table_list):

            if se in finished_vars:
                logger.info(f'Variables {se} already done, skipping ...')
                continue

            tab_in_db_id = database_table_names[se[0]]

            logger.info(f'Processing geo {i} vars {se} ({tab_in_db_id, database_table_names[se[1]]}).')
            start_time = time.time()

            success = False

            number_of_retries = 5

            while not success:

                try:

                    response = requests.get(f'http://ec2-107-20-216-26.compute-1.amazonaws.com/pub/reportdata/DownloadCsvFileNow.aspx?'
                                            f'survey={survey}&ds={ds}&startTableName={se[0]}&endTableName={se[1]}&geoName={i}'
                                            f'&filename={survey}_{i}_ACS_part_{str(ind)}.csv&{GUID_vars}mirroredTables=false', timeout=5)

                    if response.status_code == 200:

                        if step == 1:
                            file_name = survey + i + '_' + se[0] + '_' + tab_in_db_id + '_part_' + str(ind) + '.csv'
                        else:
                            file_name = survey + i + '_' + se[0] + '_' + se[1] + '_part_' + str(ind) + '.csv'

                        with open(path_to_out + '\\' + file_name, 'wb') as f:
                            f.write(response.content)

                        finished_vars.append(se)

                        pickle.dump(finished_vars, open('finished_vars.pkl', 'wb'))

                        success = True

                    else:
                        logger.warning(f'Got response {response.status_code}, exiting ...')
                        break

                except ConnectionResetError:

                    if number_of_retries > 0:
                        number_of_retries -= 1
                        delay = 120
                        logger.info(f'Connection broken, starting again in {delay} seconds!')
                        time.sleep(delay)
                    else:
                        logger.warning(f'Maximum number of retries reached, exiting ...')
                        break

            logger.info(f"Done in {int((time.time() - start_time) / 60)} minutes!")


if __name__ == '__main__':
    survey, ds, geoName, metadata_file_location, path_to_out, step, GUID_vars = extract_cmd_arguments()

    list_of_tables_for_download = get_tables_list(metadata_file_location)

    list_of_tables_for_download = chunk_tables_list_by_step(list_of_tables_for_download, step)

    table_names_in_db = get_table_names_from_db(metadata_file_location)

    list_of_finished_vars = get_list_of_finished_variables()

    download_files(geoName, list_of_tables_for_download, table_names_in_db, list_of_finished_vars)

    remove('finished_vars.pkl')