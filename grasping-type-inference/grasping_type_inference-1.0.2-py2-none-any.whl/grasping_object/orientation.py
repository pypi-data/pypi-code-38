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

import grasping_type_inference.ground_atom_builder as gab


class Orientation:
    def __init__(self, facing_robot_face, bottom_face):
        self.facing_robot_face = facing_robot_face
        self.bottom_face = bottom_face

    def transform_facing_robot_face_to_ground_atom(self):
        return gab.get_facing_robot_face(self.facing_robot_face)

    def transform_bottom_face_to_ground_atom(self):
        return gab.get_bottom_face(self.bottom_face)

    def __eq__(self, other):
        if (self.facing_robot_face != other.facing_robot_face) or (self.bottom_face != other.bottom_face):
            return False
        else:
            return True

