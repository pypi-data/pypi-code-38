# -*- coding: utf-8 -*-
__author__ = 'Daniel Scheffler'

import sqlite3
import os
from typing import Union  # noqa F401  # flake8 issue
import csv
from six import PY3


def data_DB_updater(gms_obj_dict, path_db):
    # type: (dict) -> None
    """Updates the table "scenes_proc" or "mgrs_tiles_proc within a postgreSQL or an SQL database
    according to the given dictionary of a GMS object.

    :param gms_obj_dict:    <dict> a copy of the dictionary of the respective GMS object
    """

    assert isinstance(gms_obj_dict, dict), 'The input for data_DB_updater() has to be a dictionary.'

    def list2str(list2convert): return ''.join([str(val) for val in list2convert])

    if not os.path.isfile(path_db):
        print('No internal database found. Creating a new one...')
    connection = sqlite3.connect(path_db)
    cursor = connection.cursor()
    fullColumnList = ['job_ID', 'job_CPUs', 'image_type', 'satellite', 'sensor', 'subsystem', 'sensormode',
                      'acquisition_date', 'entity_ID', 'georef', 'proc_level', 'LayerBandsAssignment',
                      'path_procdata']
    cursor.execute('''CREATE TABLE IF NOT EXISTS processed_data (%s)''' % ', '.join(fullColumnList))
    currentColumnList = [i[1] for i in cursor.execute("PRAGMA table_info('processed_data')").fetchall()]
    missingColumns = [col for col in fullColumnList if col not in currentColumnList]
    if missingColumns:  # automatic adding of missing columns
        cursor.execute('''CREATE TABLE IF NOT EXISTS processed_data_temp (%s)''' % ', '.join(fullColumnList))
        cursor.execute("SELECT " + ','.join(currentColumnList) + " FROM processed_data")
        [cursor.execute("INSERT INTO processed_data_temp (%(cols)s) VALUES (%(vals)s)" % {'cols': ','.join(
            currentColumnList), 'vals': ','.join(['?'] * len(currentColumnList))}, row) for row in
         cursor.fetchall()]
        cursor.execute("DROP TABLE processed_data")
        cursor.execute("ALTER TABLE processed_data_temp RENAME TO processed_data")
    cursor.execute("SELECT EXISTS(SELECT 1 FROM processed_data WHERE entity_ID=? AND sensor=? AND subsystem=?)",
                   [gms_obj_dict['entity_ID'], gms_obj_dict['sensor'], gms_obj_dict['subsystem']])
    if cursor.fetchone()[0] == 0:  # create new entry
        new_record = [gms_obj_dict[key] for key in fullColumnList]
        new_record = [(''.join([str(val[li]) for li in range(len(val))])) if isinstance(val, list) else val
                      for val in new_record]  # e.g. converts list of LayerBandsAssignment to string
        cursor.execute("INSERT INTO processed_data VALUES (%s)" % ','.join(['?'] * len(new_record)), new_record)
    else:  # udate existing entry
        values2update = [gms_obj_dict[key] for key in
                         ['job_ID', 'job_CPUs', 'proc_level', 'path_procdata', 'LayerBandsAssignment']]
        values2update = [(''.join([str(val[li]) for li in range(len(val))])) if isinstance(val, list) else val
                         for val in values2update]  # e.g. converts list of LayerBandsAssignment to string
        connection.execute("UPDATE processed_data set job_ID=?, job_CPUs=?, proc_level=?,path_procdata=?, \
                            LayerBandsAssignment=? WHERE entity_ID=? AND sensor=? AND subsystem=?",
                           values2update + [gms_obj_dict['entity_ID']] + [gms_obj_dict['sensor'],
                                                                          gms_obj_dict['subsystem']])


def get_info_from_SQLdb(path_db, tablename, vals2return, cond_dict, records2fetch=0):
    # type: (str,str,list,dict,int) -> Union[list, str]
    """Queries an SQL database for the given parameters.

    :param path_db:         <str> the physical path of the SQL database on disk
    :param tablename:       <str> name of the table within the database to be queried
    :param vals2return:     <list or str> a list of strings containing the column titles of the values to be returned
    :param cond_dict:       <dict> a dictionary containing the query conditions in the form {'column_name':<value>}
    :param records2fetch:   <int> number of records to be fetched (default=0: fetch unlimited records)
    """

    if not isinstance(vals2return, list):
        vals2return = [vals2return]
    assert isinstance(records2fetch, int), \
        "get_info_from_SQLdb: Expected an integer for the argument 'records2return'. Got %s" % type(records2fetch)
    if not os.path.isfile(path_db):
        return 'database connection fault'
    connection = sqlite3.connect(path_db)
    cursor = connection.cursor()
    condition = "WHERE " + " AND ".join(["%s=?" % (list(cond_dict.keys())[i]) for i in range(len(cond_dict))])
    cursor.execute("SELECT " + ','.join(vals2return) + " FROM " + tablename + " " + condition, list(cond_dict.values()))
    records2return = cursor.fetchall() if records2fetch == 0 else [cursor.fetchone()] if records2fetch == 1 else \
        cursor.fetchmany(size=records2fetch)  # e.g. [('LE71950282003121EDC00',), ('LE71950282003105ASN00',)]
    cursor.close()
    connection.close()
    return records2return


def SQL_DB_to_csv(path_db):
    if not os.path.exists(path_db) or not os.path.getsize(path_db) > 0:
        print('No database conversion to CSV performed, because DB does not exist or DB is empty.')
    else:
        connection = sqlite3.connect(path_db)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM processed_data")

        with open(os.path.join(os.path.dirname(path_db), 'data_DB.csv'), 'w' if PY3 else 'wb') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([i[0] for i in cursor.description])
            csvwriter.writerows(cursor)
