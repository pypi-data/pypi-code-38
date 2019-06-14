# /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modul is used for GUI of Lisa
"""
from loguru import logger
# problem is loading lxml together with openslide
# from lxml import etree
import os
import json
import os.path as op
import glob
import matplotlib.pyplot as plt
import numpy as np

__version__ = "0.8.1"


def get_one_annotation(viewstate):
    titles_list = viewstate.xpath(".//title/text()")
    if len(titles_list) == 0:
        an_title = ""
    elif len(titles_list) == 1:
        an_title = titles_list[0]
    else:
        raise ValueError("More than one title in viewstate")
    details_list = viewstate.xpath(".//details/text()")
    if len(details_list) == 0:
        an_details = ""
    elif len(details_list) == 1:
        an_details = details_list[0]
    else:
        raise ValueError("More than one details in viewstate")

    annotations = viewstate.xpath(".//annotation")
    if len(annotations) > 1:
        raise ValueError("More than one annotation found")
    annot = annotations[0]
    an_color = annot.get("color")
    #     display(len(annotation))
    an_x = list(map(int, annot.xpath(".//pointlist/point/x/text()")))
    an_y = list(map(int, annot.xpath(".//pointlist/point/y/text()")))
    return dict(title=an_title, color=an_color, x=an_x, y=an_y, details=an_details)


def _ndpa_file_to_json(pth):

    # problem is loading lxml together with openslide
    from lxml import etree

    tree = etree.parse(pth)
    viewstates = tree.xpath("//ndpviewstate")
    all_anotations = list(map(get_one_annotation, viewstates))
    fn = pth + ".json"
    with open(fn, "w") as outfile:
        json.dump(all_anotations, outfile)


def ndpa_to_json(path):
    """
    :param path: path to file or dir contaning .ndpa files
    """
    print(os.getenv("PATH"))
    if op.isfile(path):
        fn, ext = op.splitext(path)
        if ext == ".ndpi":
            path = path + ".ndpa"
        _ndpa_file_to_json(path)
    else:
        extended_path = op.join(path, "*.ndpa")
        #         print(extended_path)
        files = glob.glob(extended_path)
        for fl in files:
            _ndpa_file_to_json(fl)


def read_annotations(pth):
    """
    Read the ndpa annotations. Annotation is converted to json if it is not done before. This step
    works on Linux but not on Windows.
    :param pth: path to .ndpi file
    :return: readed annotatios
    """

    import platform

    if platform.system() == "Windows":
        import subprocess
        import sys

        # output = subprocess.check_output(["pwd"])
        # print(output)
        # output = subprocess.check_output(["where", "python"])
        # print(output)

        cwd = op.dirname(op.dirname(__file__))
        try:
            output = subprocess.check_output(
                [sys.executable, "-m", "scaffan.ann_to_json", pth], cwd=cwd, stderr=subprocess.STDOUT

            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        logger.debug("windows annotation output:" + str(output))
        # print(output)
    else:
        # if not op.exists(fn):
        ndpa_to_json(pth)

    fn = pth + ".ndpa.json"
    with open(fn) as f:
        data = json.load(f)
    return data


def plot_annotations(annotations, x_key="x", y_key="y", in_region=False, factor=[1, 1]):
    if type(annotations) is dict:
        annotations = [annotations]

    if in_region:
        x_key = "region_x_px"
        y_key = "region_y_px"

    for annotation in annotations:
        x = np.asarray(annotation[x_key]) * factor[0]
        y = np.asarray(annotation[y_key]) * factor[1]
        # plt.hold(True)
        plt.plot(x, y, c=annotation["color"])


def adjust_xy_to_image_view(imsl, x_px, y_px, center, level, size):
    x_px_view = ((x_px - center[0]) / imsl.level_downsamples[level]) + (size[0] / 2)
    y_px_view = ((y_px - center[1]) / imsl.level_downsamples[level]) + (size[1] / 2)
    return x_px_view, y_px_view


def adjust_annotation_to_image_view(imsl, annotations, center, level, size):
    output = []
    for annotation in annotations:
        ann_out = annotation
        x_px_view, y_px_view = adjust_xy_to_image_view(
            imsl, annotation["x_px"], annotation["y_px"], center, level, size
        )
        ann_out["region_x_px"] = x_px_view
        ann_out["region_y_px"] = y_px_view
        ann_out["region_center"] = center
        ann_out["region_level"] = level
        ann_out["region_size"] = size
        output.append(ann_out)

    return output


def annotations_to_px(imsl, annotations):
    from scaffan.image import get_offset_px, get_pixelsize

    offset_px = get_offset_px(imsl)
    pixelsize, pixelunit = get_pixelsize(imsl)
    for annotation in annotations:
        x_nm = np.asarray(annotation["x"])
        y_nm = np.asarray(annotation["y"])
        x_mm = x_nm * 0.000001
        y_mm = y_nm * 0.000001
        x_px = x_mm / pixelsize[0] + offset_px[0]
        y_px = y_mm / pixelsize[1] + offset_px[1]
        annotation["x_nm"] = x_nm
        annotation["y_nm"] = y_nm
        annotation["x_mm"] = x_mm
        annotation["y_mm"] = y_mm
        annotation["x_px"] = x_px
        annotation["y_px"] = y_px
    return annotations


def annotation_titles(annotations):
    titles = {}
    for i, an in enumerate(annotations):
        title = an["title"]
        if title in titles:
            titles[title].append(i)
        else:
            titles[title] = [i]

    return titles


def annotation_colors(annotations):
    # titles = {}
    colors = {}
    for i, an in enumerate(annotations):
        title = an["color"]
        title = title.upper()
        if title in colors:

            colors[title].append(i)
        else:
            colors[title] = [i]

    return colors

def annotation_details(annotations):
    return _get_annotation_elements(annotations, "details")


def _get_annotation_elements(annotations, element_keyword):
    colors = {}
    for i, an in enumerate(annotations):
        title = an[element_keyword]
        title = title.upper()
        if title in colors:

            colors[title].append(i)
        else:
            colors[title] = [i]

    return colors
