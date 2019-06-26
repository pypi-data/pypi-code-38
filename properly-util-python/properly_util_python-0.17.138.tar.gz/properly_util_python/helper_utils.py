import csv
import decimal
import json
import os
import traceback

from datetime import (
    datetime,
    timezone,
)
from typing import List

import boto3

from properly_util_python.data_utils import ExtendedJsonEncoder


def dynamo_to_dict(dynamo_data):
    if not dynamo_data:
        return dynamo_data
    return json.loads(ExtendedJsonEncoder().encode(dynamo_data))


def dict_to_dynamo(raw_dict):
    dynamo_dict = {}
    for key, val in raw_dict.items():
        if isinstance(val, float):
            dynamo_dict[key] = decimal.Decimal(str(val))
        elif isinstance(val, dict):
            dynamo_dict[key] = dict_to_dynamo(raw_dict[key])
        elif isinstance(val, list):
            new_list = []
            for item in val:
                conversion_dictionary = {'val_to_convert': item}
                result_dictionary = dict_to_dynamo(conversion_dictionary)
                # get + if (new_item) handles dictionary where the items are 'None'
                new_item = result_dictionary.get('val_to_convert')
                if new_item:
                    new_list.append(new_item)
            dynamo_dict[key] = new_list
        elif isinstance(val, datetime):
            if val.tzinfo is None:
                # Timestamps are not required to have timezones.
                # Assume it is in UTC if not specified.
                val = val.replace(tzinfo=timezone.utc)
            milliseconds = int(val.timestamp() * 1000)
            dynamo_dict[key] = milliseconds
        elif val is None:
            # skip null values
            continue
        elif val == "":
            # skip null values
            continue
        else:
            dynamo_dict[key] = val
    return dynamo_dict


def download_files(files=None, bucket_name=None):

    # Without providing explicit keys boto will pick up keys from the environment during dev,
    # and pick up access control from the role in prod
    # local file is ./aws/credentials see: https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html
    s3 = boto3.resource('s3', )
    try:
        if not files:
            files = []
        data_dir = 'data/'
        os.makedirs(data_dir, exist_ok=True)

        local_files = []
        for file in files:
            os.makedirs(os.path.dirname(file), exist_ok=True)

        for file in files:
            local_file = file[file.rfind("/") + 1:]
            local_file = data_dir + local_file

            print('downloading:', file)
            print('local_file:', local_file)
            s3.Bucket(bucket_name).download_file(file, local_file)
            local_files.append(local_file)

        return local_files

    except Exception as e:
        print('exception', e)
        print('traceback', traceback.format_exc())


def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b



def load_csv_data(csv_file_name):
    data = []

    with open(csv_file_name, "rt") as f:
        reader = csv.reader(f, delimiter=",")
        for i, line in enumerate(reader):
            data.append(line)
    return data


def csv_to_json(csv_file_name):
    csv_dict = []
    data = load_csv_data(csv_file_name)

    for i, row in enumerate(data[1:]):
        json_row = {}

        for column, value in zip(data[0], row):
            if not column:
                continue
            # id column must be a string
            if any(x in value for x in ['E+','E-','e+','e-']):
                pass
            elif isint(value):
                value = int(value)
            elif isfloat(value):
                value = float(value)
            json_row[column] = value

        # if 'id' not in data[0] or not json_row.get('id',None):
        #     json_row['id'] = i
        # json_row['id'] = str(i)

        csv_dict.append(json_row)

    return csv_dict


def json_to_csv(json_data: List[dict], csv_file_name):

    json_cols = json_data[0]
    json_cols = [key for key in json_cols.keys()]

    json_data_rows = []

    for row in json_data:
        json_data_rows.append([val for val in row.values()])

    with open(csv_file_name, 'w') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(json_cols)
        wr.writerows(json_data_rows)


if __name__ == '__main__':
    json_data = [
        {'role': 1, 'name': 'Tomiwa'},
        {'role': 2, 'name': 'Craig'},
    ]
    csv_file_name = 'test.csv'
    json_to_csv(json_data, csv_file_name)

    print(csv_to_json(csv_file_name))