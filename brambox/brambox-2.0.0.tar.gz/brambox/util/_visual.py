#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#   Visualization functionality
#

import os
import logging
import collections
from pathlib import Path
from enum import Enum
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)   # noqa
default = None                      # noqa

try:
    import cv2
    default = 0
except ModuleNotFoundError:
    log.debug('OpenCV not installed')
    cv2 = None

try:
    from PIL import Image, ImageDraw, ImageFont
    default = 1

    try:
        font = ImageFont.truetype('DejaVuSansMono', 10)
    except IOError:
        font = ImageFont.load_default()
except ModuleNotFoundError:
    log.debug('Pillow not installed')
    Image = None

if Image is None and cv2 is None:
    log.error('Neither Pillow nor OpenCV installed, visualization functions will not work')


__all__ = ['BoxDrawer', 'draw_boxes', 'DrawMethod']


class DrawMethod(Enum):
    """ Which library to use for drawing """
    CV = 0 if cv2 is not None else None     #: Use OpenCV
    PIL = 1 if Image is not None else None  #: Use Pillow


def draw_boxes(img, boxes, label=False, color=None, size=None, method=default):
    """ Draws bounding boxes on an image.

    Args:
        img (OpenCV image or PIL image or filename): Image to draw on
        boxes (pandas.DataFrame): Bounding boxes to draw
        label (pandas.Series, optional): Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional): Thickness of the border of the bounding boxes; Default **3**
        method (DrawMethod, optional): Whether to use OpenCV or Pillow for opening the image (only useful when filename given); Default: **DrawMethod.PIL**

    Returns:
        OpenCV or PIL image: Image with bounding boxes drawn

    Note:
        The `label`, `color` and `size` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

    Note:
        The default drawing method depends on whichever library is installed (cv2 or PIL) and is only used if the image passed is a string or Path object.
        If both are installed, Pillow is the default choice.
    """
    if DrawMethod(method).value is None:
        raise ImportError(f'Could not find the correct library for the chosen drawing method [{DrawMethod(method)}]')

    # Open image
    if isinstance(img, str) or isinstance(img, Path):
        if method == DrawMethod.CV:
            img = cv2.imread(img)
        else:
            method = DrawMethod.PIL
            original = Image.open(img)
            if original.mode == 'L':
                original = original.convert('RGB')
            img = ImageDraw.Draw(original)
    elif Image is not None and isinstance(img, Image.Image):
        img = img.copy()
        if img.mode == 'L':
            original = img.convert('RGB')
        else:
            original = img
        img = ImageDraw.Draw(original)
        method = DrawMethod.PIL
    elif cv2 is not None and isinstance(img, np.ndarray):
        img = img.copy()
        method = DrawMethod.CV
    else:
        raise TypeError(f'Unkown image type [{type(img)}]')

    boxes = setup_boxes(boxes, label, color, size)

    # Draw
    if method == DrawMethod.CV:
        draw = draw_cv
    else:
        draw = draw_pil

    for box in boxes.itertuples():
        draw(img, box)

    if method == DrawMethod.PIL:
        return original
    else:
        return img


class BoxDrawer:
    """ This class allows to iterate over all images in a dataset and draw their respective bounding boxes.

    Args:
        images (callable or dict-like object): A way to get the image or path to the image from the image labels in the dataframe
        boxes (pandas.DataFrame): Bounding boxes to draw
        label (pandas.Series, optional): Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional): Thickness of the border of the bounding boxes; Default **3**
        show_empty (boolean, optional): Whether to also show images without bounding boxes; Default **True**
        method (DrawMethod, optional): Whether to use OpenCV or Pillow for opening the image (only useful when filename given); Default: **DrawMethod.PIL**

    Note:
        If the `images` argument is callable, the image or path to the image will be retrieved in the following way:
        >>> image = self.images(image_label)

        Otherwise the image or path is retrieved as:
        >>> image = self.images[image_label]

    Note:
        The `label`, `color` and `size` arguments can also be tacked on to the `boxes` dataframe as columns.
        They can also be a single value, which will then be used for each bounding box. |br|
        Basically, as long as you can assign the value as a new column to the dataframe, it will work.

    Note:
        The default drawing method depends on whichever library is installed (cv2 or PIL) and is only used if the images passed are string or Path objects.
        If both are installed, Pillow is the default choice.
    """
    methods = DrawMethod

    def __init__(self, images, boxes, label=False, color=None, size=None, show_empty=True, method=default):
        self.images = images
        self.boxes = setup_boxes(boxes, label, color, size)

        self.method = method
        if DrawMethod(self.method).value is None:
            raise ImportError(f'Could not find the correct library for the chosen drawing method [{DrawMethod(method)}]')

        if show_empty:
            self.image_labels = list(self.boxes.image.cat.categories)
        else:
            self.image_labels = list(self.boxes.image.cat.remove_unused_categories().cat.categories)

    def __len__(self):
        return len(self.image_labels)

    def __getitem__(self, idx):
        """ Get image with boxes drawn onto it.

        Args:
            idx (str or int): Numerical index or image string

        Returns:
            OpenCV or PIL image: Image with bounding boxes drawn
        """
        if isinstance(idx, int):
            lbl = self.image_labels[idx]
        else:
            lbl = idx

        if callable(self.images):
            img = self.images(lbl)
        else:
            img = self.images[lbl]

        if isinstance(img, str) or isinstance(img, Path):
            if self.method == DrawMethod.CV:
                img = cv2.imread(img)
                method = DrawMethod.CV
            else:
                original = Image.open(img)
                if original.mode == 'L':
                    original = original.convert('RGB')
                img = ImageDraw.Draw(original)
                method = DrawMethod.PIL
        elif Image is not None and isinstance(img, Image.Image):
            if img.mode == 'L':
                original = img.convert('RGB')
            else:
                original = img
            img = ImageDraw.Draw(original)
            method = DrawMethod.PIL
        elif cv2 is not None and isinstance(img, np.ndarray):
            method = DrawMethod.CV
        else:
            raise TypeError(f'Unkown image type [{type(img)}]')

        # Draw
        if method == DrawMethod.CV:
            draw = draw_cv
        else:
            draw = draw_pil

        for box in self.boxes[self.boxes.image == lbl].itertuples():
            draw(img, box)

        if method == DrawMethod.PIL:
            return original
        else:
            return img


def setup_boxes(boxes, label=False, color=None, size=None):
    """ Setup the boxes dataframe with the correct metadata columns to draw them.
    This function basically adds on 3 columns ['label', 'color', 'size'] if they are not yet on the dataframe.

    Args:
        boxes (pandas.DataFrame): Bounding boxes to draw
        label (pandas.Series, optional): Label to write above the boxes; Default **nothing**
        color (pandas.Series, optional): Color to use for drawing; Default **every class_label will get its own color, up to 10 labels**
        size (pandas.Series, optional): Thickness of the border of the bounding boxes; Default **3**

    Returns:
        pandas.DataFrame: brambox dataframe with 3 extra columns ['label', 'color', 'size']
    """
    default_colors = [
        (31, 119, 180),
        (255, 127, 14),
        (44, 160, 44),
        (214, 39, 40),
        (148, 103, 189),
        (140, 86, 75),
        (227, 119, 194),
        (127, 127, 127),
        (188, 189, 34),
        (23, 190, 207),
    ]
    boxes = boxes.copy()

    if 'color' not in boxes.columns:
        if color is not None:
            if isinstance(color, collections.Sequence) and len(color) == 3 and isinstance(color[0], int):
                boxes['color'] = [color] * len(boxes)
            else:
                boxes['color'] = color
        else:
            labels = boxes.class_label.unique()
            boxes['color'] = boxes.class_label.map(dict((v, i) for i, v in enumerate(labels)))
            boxes.color %= len(default_colors)
            boxes.color = boxes.color.map(dict((i, v) for i, v in enumerate(default_colors)))

    if 'size' not in boxes.columns:
        if size is not None:
            boxes['size'] = size
            boxes['size'] = boxes['size'].astype(int)
        else:
            boxes['size'] = 3

    if 'label' not in boxes.columns:
        if label is True:
            boxes['label'] = boxes.apply(lambda b: f'{b.class_label}{" "+str(b.id) if not np.isnan(b.id) else ""}', axis=1)
            if 'confidence' in boxes.columns:
                boxes.label += ' [' + (boxes.confidence * 100).round(2).astype(str) + '%]'
        else:
            boxes['label'] = label

    return boxes


def draw_pil(img, box):
    """ Draw a bounding box on a Pillow image """
    pt1 = (int(box.x_top_left), int(box.y_top_left))
    pt2 = (int(box.x_top_left + box.width), int(box.y_top_left))
    pt3 = (int(box.x_top_left + box.width), int(box.y_top_left + box.height))
    pt4 = (int(box.x_top_left), int(box.y_top_left + box.height))
    img.line([pt1, pt2, pt3, pt4, pt1], box.color, box.size)

    if box.label:
        offset = 12 + box.size
        img.text((pt1[0], pt1[1]-offset), box.label, box.color, font)


def draw_cv(img, box):
    """ Draw a bounding box on an OpenCV image """
    color = box.color
    if isinstance(color, collections.Sequence):
        color = color[::-1]
    pt1 = (int(box.x_top_left), int(box.y_top_left))
    pt2 = (int(box.x_top_left + box.width), int(box.y_top_left + box.height))
    cv2.rectangle(img, pt1, pt2, color, box.size)

    if box.label:
        cv2.putText(img, box.label, (pt1[0], pt1[1]-5), cv2.FONT_HERSHEY_PLAIN, .75, color, 1, cv2.LINE_AA)


draw_boxes.methods = DrawMethod
