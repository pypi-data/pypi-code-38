# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.arguments import String
from suanpan.dw import dw
from suanpan.tools import ToolComponent as tc
from suanpan.utils import csv


@tc.param(String(key="action", required=True))
@tc.param(String(key="file"))
@tc.param(String(key="table"))
def SPDWTools(context):
    args = context.args

    if args.action == "upload":
        data = csv.load(args.file)
        dw.writeTable(args.table, data)
    elif args.action == "download":
        data = dw.readTable(args.table)
        csv.dump(data, args.file)
    else:
        raise Exception("Unsupport action: {}".format(args.action))


if __name__ == "__main__":
    SPDWTools()  # pylint: disable=no-value-for-parameter
