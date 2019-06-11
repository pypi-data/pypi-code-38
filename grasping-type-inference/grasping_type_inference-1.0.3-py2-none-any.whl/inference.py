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

from grasping_type_inference.grasping_object.grasping_object import GraspingObject
from grasping_type_inference.grasping_object.orientation import Orientation


class Inference(object):
    def __init__(self, *evidences):
        self._facing_robot_face, self._bottom_face, self._object_type = evidences

    def get_storted_list_of_grasping_types_based_on_probability(self):
        result = self._get_grasping_types_probability_distribution()
        unsorted_results = result.results
        sorted_results = sorted(unsorted_results.items(), key=lambda x: x[1], reverse=True)
        solutions = []

        for sorted_result in sorted_results:
            solutions.append(sorted_result[0])

        return map(_remove_grasping_type_predicate, solutions)

    def get_most_probable_result(self):
        result = self._get_grasping_types_probability_distribution()

        solution = None
        max_prob = 0

        for ground_atom in result.results.keys():
            if result.results[ground_atom] >= max_prob:
                solution = ground_atom
                max_prob = result.results[ground_atom]

        return _remove_grasping_type_predicate(solution)

    def _get_grasping_types_probability_distribution(self):
        orientation = Orientation(self._facing_robot_face, self._bottom_face)
        grasping_object = GraspingObject(self._object_type, orientation)

        return grasping_object.get_grasping_types_probability_distribution()


def _remove_grasping_type_predicate(atom):
    splited_atom = atom.split('(')[1]

    return splited_atom.split(')')[0]