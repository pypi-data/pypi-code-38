# ================================================================================ #
#   Authors: Fabio Frazao and Oliver Kirsebom                                      #
#   Contact: fsfrazao@dal.ca, oliver.kirsebom@dal.ca                               #
#   Organization: MERIDIAN (https://meridian.cs.dal.ca/)                           #
#   Team: Data Analytics                                                           #
#   Project: ketos                                                                 #
#   Project goal: The ketos library provides functionalities for handling          #
#   and processing acoustic data and applying deep neural networks to sound        #
#   detection and classification tasks.                                            #
#                                                                                  #
#   License: GNU GPLv3                                                             #
#                                                                                  #
#       This program is free software: you can redistribute it and/or modify       #
#       it under the terms of the GNU General Public License as published by       #
#       the Free Software Foundation, either version 3 of the License, or          #
#       (at your option) any later version.                                        #
#                                                                                  #
#       This program is distributed in the hope that it will be useful,            #
#       but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#       GNU General Public License for more details.                               # 
#                                                                                  #
#       You should have received a copy of the GNU General Public License          #
#       along with this program.  If not, see <https://www.gnu.org/licenses/>.     #
# ================================================================================ #

""" Unit tests for the 'annotation' module within the ketos library
"""

import pytest
import numpy as np
from ketos.audio_processing.annotation import AnnotationHandler


def test_can_initialize_empty_annotation_handler():
    _ = AnnotationHandler()

def test_can_initialize_annotation_handler():
    # one label, one 4d box
    _ = AnnotationHandler(labels=[1], boxes=[[0.1, 0.3, 100., 400.]])
    # one label, one 2d box
    _ = AnnotationHandler(labels=[1], boxes=[[0.1, 0.3]])
    # one label, two boxes
    with pytest.raises(AssertionError):
        _ = AnnotationHandler(labels=[1], boxes=[[0.1, 0.3],[0.1, 0.3]])
    # two labels, one box
    with pytest.raises(AssertionError):
        _ = AnnotationHandler(labels=[1,2], boxes=[[0.1, 0.3]])
    # one label, one box
    _ = AnnotationHandler(labels=1, boxes=[0.1, 0.3, 100., 400.])
    # box with wrong dimensions
    with pytest.raises(AssertionError):
        _ = AnnotationHandler(labels=1, boxes=[0.1, 0.3, 100])
        _ = AnnotationHandler(labels=1, boxes=[0.1, 0.3, 100, 333, 1])
    # labels provided as tuples
    _ = AnnotationHandler(labels=(1,2), boxes=[[0.1, 0.3],[0.4,0.7]])
    # labels provided as numpy arrays
    _ = AnnotationHandler(labels=np.array([1,2]), boxes=[[0.1, 0.3],[0.4,0.7]])

def test_add_annotations():
    a = AnnotationHandler()
    a.annotate(labels=1, boxes=[1,2,3,4])
    a.annotate(labels=[2,3], boxes=[[1,2,3,4],[5,6,7,8]])
    assert len(a.labels) == 3
    # two labels, and two boxes
    a = AnnotationHandler()
    labels = [0, 1]
    boxes = [[10.0, 12.2, 110., 700.],[30., 34.]]
    a.annotate(labels, boxes)

def test_delete_annotations():
    labels = [1,2,3]
    boxes = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
    # delete one annotation
    a = AnnotationHandler(labels, boxes)
    assert len(a.labels) == 3
    a.delete_annotations(id=0)
    assert len(a.labels) == 2
    assert a.labels[0] == 2
    # delete two annotations
    a = AnnotationHandler(labels, boxes)
    assert len(a.labels) == 3
    a.delete_annotations(id=[0,1])
    assert len(a.labels) == 1
    assert a.labels[0] == 3
    # delete a non-existing annotation
    a = AnnotationHandler(labels, boxes)
    assert len(a.labels) == 3
    a.delete_annotations(id=77)
    assert len(a.labels) == 3
    assert a.labels[0] == 1
    # delete all annotation
    a = AnnotationHandler(labels, boxes)
    assert len(a.labels) == 3
    a.delete_annotations()
    assert len(a.labels) == 0

def test_get_cropped_annotations():
    labels = [1,2]
    box1 = [14.,17.,0.,29.]
    box2 = [2.1,13.0,1.1,28.5]
    boxes = [box1, box2]
    a = AnnotationHandler(labels=labels, boxes=boxes)
    l, b = a.get_cropped_annotations(t1=2, t2=15, f1=24, f2=27)
    assert len(l) == 2
    assert l[0] == 1
    assert b[0][0] == pytest.approx(14.0, abs=0.001)
    assert b[0][1] == pytest.approx(15.0, abs=0.001)
    assert b[0][2] == pytest.approx(24.0, abs=0.001)
    assert b[0][3] == pytest.approx(27.0, abs=0.001)
    assert l[1] == 2
    assert b[1][0] == pytest.approx(2.1, abs=0.001)
    assert b[1][1] == pytest.approx(13.0, abs=0.001)
    assert b[1][2] == pytest.approx(24.0, abs=0.001)
    assert b[1][3] == pytest.approx(27.0, abs=0.001)

def test_get_cropped_annotations_2():
    labels = [0, 1]
    boxes = [[10.0, 12.2, 110., 700.],[30., 34.]]
    handler = AnnotationHandler(labels, boxes)
    l, b = handler.get_cropped_annotations(t1=10.3, f2=555.)
    assert len(l) == 2
    assert l[0] == 0
    assert l[1] == 1
    assert len(b) == 2
    assert b[0][0] == 10.3
    assert b[0][1] == 12.2
    assert b[0][2] == 110.0
    assert b[0][3] == 555.0
    assert b[1][0] == 30.
    assert b[1][1] == 34.
    assert b[1][2] == 0
    assert b[1][3] == 555.0

def test_shift_annotations():
    labels = [1,2]
    box1 = [14.,17.,0.,29.]
    box2 = [2.1,13.0,1.1,28.5]
    boxes = [box1, box2]
    a = AnnotationHandler(labels=labels, boxes=boxes)
    a._shift_annotations(delay=3.3)
    l = a.labels
    b = a.boxes
    assert len(l) == 2
    assert b[0][0] == pytest.approx(17.3, abs=0.001)
    assert b[0][1] == pytest.approx(20.3, abs=0.001)
    assert b[1][0] == pytest.approx(5.4, abs=0.001)
    assert b[1][1] == pytest.approx(16.3, abs=0.001)
