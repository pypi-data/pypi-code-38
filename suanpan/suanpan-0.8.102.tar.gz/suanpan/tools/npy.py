# coding=utf-8
from __future__ import absolute_import, division, print_function

import os
import time
import webbrowser

from suanpan.arguments import Bool, String
from suanpan.components import Component as c
from suanpan.utils import image, npy


def showAsImage(data, temp="tmp", flag=None):
    imageType = "gif" if flag == "animated" else "png"
    filepath = os.path.join(temp, "{}.{}".format(time.time(), imageType))
    image.save(filepath, data, flag=flag)
    showImage(filepath)


def showImage(filepath):
    url = "file://" + os.path.abspath(filepath)
    webbrowser.open(url)


@c.input(String(key="npy", required=True))
@c.param(String(key="toImage"))
@c.param(String(key="flag"))
@c.param(Bool(key="show", default=False))
def SPNpyTools(context):
    args = context.args

    data = npy.load(args.npy)
    if args.toImage:
        filepath = image.save(args.toImage, data, flag=args.flag)
        if args.show:
            showImage(filepath)
    else:
        import pdb

        pdb.set_trace()


if __name__ == "__main__":
    SPNpyTools()  # pylint: disable=no-value-for-parameter
