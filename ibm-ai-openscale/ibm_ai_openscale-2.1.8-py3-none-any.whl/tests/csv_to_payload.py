# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import json
#import os

def main(args):
    def parse_list(l, sch):

        def parse(x, s):
            if(s=='str'):
                return x
            if(s=='int'):
                return int(x)
            if(s=='float'):
                return float(x)

        l_split = enumerate(l.strip('\n').split(args.csv_sep))
        return [parse(v, sch[i]) for i, v in l_split]

    with open(args.schema_filename, 'r') as f_schema:
        csv_schema = json.load(f_schema)

    json_data = {'fields': [], 'values': []}
    with open(args.csv_filename, 'r') as csv_f:
        head_line = csv_f.readline()
        json_data['fields'] = head_line.strip('\n').split(args.csv_sep)
        for l in csv_f:
            json_data['values'].append(parse_list(l, csv_schema))

    if(args.json_filename==''):
        print(json.dumps(json_data))
    else:
        with open(args.json_filename, 'w') as f_json:
            json.dump(json_data, f_json)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='File format converter')
    parser.add_argument('--csv-filename', metavar='csv_filename', type=str)
    parser.add_argument('--csv-sep', metavar='csv_sep', type=str, default=',')
    parser.add_argument('--schema-filename', metavar='schema_filename', type=str)
    parser.add_argument('--json-filename', metavar='json_filename', type=str, default='')
    args = parser.parse_args()
    main(args)