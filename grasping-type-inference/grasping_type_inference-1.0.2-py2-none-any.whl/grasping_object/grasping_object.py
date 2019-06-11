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

from high_level_markov_logic_network.database import Database
from high_level_markov_logic_network.fuzzy_markov_logic_network.is_a_generator import get_is_a_ground_atoms
import grasping_type_inference.ground_atom_builder as gab
from grasping_type_inference.grasping_type_mln import load_grasping_mln, get_grasping_mln_selector_mln


class GraspingObject(object):
    def __init__(self, object_type, orientation):
        self.type = object_type
        self.orientation = orientation

    def _infer_required_grasping_mln_(self):
        evidence_database = self._create_evidence_database_for_grasping_selector_mln_()
        result = get_grasping_mln_selector_mln.infer(evidence_database)
        most_probable_result = _get_the_most_probable_result(result)

        return _remove_predicate_(most_probable_result)

    def get_grasping_types_probability_distribution(self):
        required_grasping_mln_name = self._infer_required_grasping_mln_()
        required_grasping_mln = '{}.pracmln'.format(required_grasping_mln_name)
        grasping_mln = load_grasping_mln(required_grasping_mln)

        evidence_database = self._create_evidence_database_for_grasping_mln_(grasping_mln)

        return grasping_mln.infer(evidence_database)

    def _create_evidence_database_for_grasping_selector_mln_(self):
        return self._create_grasping_object_related_evidences_with_given_mln_(get_grasping_mln_selector_mln)

    def _create_evidence_database_for_grasping_mln_(self, grasping_mln):
        evidence_database = self._create_grasping_object_related_evidences_with_given_mln_(grasping_mln)
        evidence_database.add_ground_atom(self.orientation.transform_facing_robot_face_to_ground_atom())
        evidence_database.add_ground_atom(self.orientation.transform_bottom_face_to_ground_atom())

        return evidence_database

    def _create_grasping_object_related_evidences_with_given_mln_(self, mln):
        evidence_database = Database(mln)
        evidence_database.add_ground_atom(gab.get_obj_to_be_grasped(self.type))

        learned_objects = mln.domains['learnedObject']
        is_a_ground_atoms = get_is_a_ground_atoms(self.type, learned_objects)
        for ground_atom in is_a_ground_atoms:
            evidence_database.add_ground_atom(ground_atom)

        return evidence_database

    def __eq__(self, other):
        if (self.type != other.type) or (self.orientation != other.orientation):
            return False
        else:
            return True


def _get_the_most_probable_result(result):
    solution = None
    max_prob = 0

    for ground_atom in result.results.keys():
        if result.results[ground_atom] >= max_prob:
            solution = ground_atom
            max_prob = result.results[ground_atom]

    return solution


def _remove_predicate_(atom):
    splited_atom = atom.split('(')[1]

    return splited_atom.split(')')[0]
