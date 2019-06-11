# -*- coding: utf-8 -*-

# Copyright © 2018 Institute for Artificial Intelligence - University of Bremen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from grasping_type_inference.face import Face
from high_level_markov_logic_network.ground_atom import GroundAtom

__FACING_ROBOT_FACE__ = 'facing_robot_face'
__BOTTOM_FACE__ = 'bottom_face'
__OBJ_TO_BE_GRASPED__ = 'obj_to_be_grasped'
__IS_ROTATIONALLY_SYMMETRIC__ = 'is_rotationally_symmetric'
__GRASP_TYPE__ = 'grasp_type'


def get_facing_robot_face(arg):
    ground_atom_value = arg

    if type(arg) is Face:
        ground_atom_value = arg.value

    return GroundAtom(__FACING_ROBOT_FACE__, [ground_atom_value])


def get_bottom_face(arg):
    ground_atom_value = arg

    if type(arg) is Face:
        ground_atom_value = arg.value

    return GroundAtom(__BOTTOM_FACE__, [ground_atom_value])


def get_obj_to_be_grasped(arg):
    return GroundAtom(__OBJ_TO_BE_GRASPED__, [arg])


def get_is_rotationally_symmetric(arg):
    return GroundAtom(__IS_ROTATIONALLY_SYMMETRIC__, [arg])


def get_grasp_type(arg):
    return GroundAtom(__GRASP_TYPE__, [arg])