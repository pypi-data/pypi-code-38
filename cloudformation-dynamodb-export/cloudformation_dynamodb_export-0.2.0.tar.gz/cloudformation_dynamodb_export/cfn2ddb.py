import argparse
import sys
import json
import os
from collections import defaultdict

from . import cfn_parser


class ParameterProcessor(argparse.Action):
    def __call__(self, parser, namespace, values, option_strings=None):
        param_dict = getattr(namespace, self.dest, [])
        if param_dict is None:
            param_dict = defaultdict(lambda: "")

        k, v = values.split("=")
        param_dict[k] = v
        setattr(namespace, self.dest, param_dict)


def export_tables(args):
    base = os.path.abspath(args.output)
    os.makedirs(base, exist_ok=True)

    parser = cfn_parser.CFNParser(args.filename, args.param)

    for table in parser.all_dynamodb_tables():
        file = os.path.join(base, f"{table.tableName()}.json")
        with open(file, "w") as fout:
            json.dump(table.properties(), fout, ensure_ascii=False,
                      indent=4, sort_keys=True, separators=(',', ': '))
        print(f"Wrote {file}")


def export():
    parser = argparse.ArgumentParser(
        description='Translate AWS Cloud Formation template to AWS CLI Input json')
    parser.add_argument('filename', metavar='<filename>',
                        help='The cloud formation template')
    parser.add_argument('-o', '--output', metavar='<path>', required=True,
                        help='Directory to export JSON files')
    parser.add_argument("--param", action=ParameterProcessor,
                        default=defaultdict(lambda: ""))
    export_tables(args=parser.parse_args())


if __name__ == '__main__':
    export()
