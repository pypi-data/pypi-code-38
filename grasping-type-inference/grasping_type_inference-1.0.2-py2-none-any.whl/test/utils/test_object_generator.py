from grasping_type_inference.grasping_object import Orientation
from grasping_type_inference.grasping_object import GraspingObject
from grasping_type_inference.grasping_object import RotationallySymmetricalGraspingObject
from markov_logic_network.grasping_type_mln import grasping_type_mln
import markov_logic_network.ground_atom_builder as gab
from markov_logic_network.database import Database

from grasping_type_inference.face import Face

GRASPING_OBJECT_TYPE = 'cup.n.01'
FACING_ROBOT_FACE = Face.FRONT
BOTTOM_FACE = Face.BOTTOM
GRASP_TYPE = 'topGrasp'


def get_test_true_mln_database():
    ground_atoms = get_test_ground_atoms()

    return get_grasping_object_as_true_mln_database(grasping_type_mln, ground_atoms)


def get_test_false_mln_database():
    ground_atoms = get_test_ground_atoms()

    return get_grasping_object_as_false_mln_database(grasping_type_mln, ground_atoms)


def get_test_ground_atoms():
    return [gab.get_bottom_face(BOTTOM_FACE),
            gab.get_facing_robot_face(FACING_ROBOT_FACE),
            gab.get_obj_to_be_grasped(GRASPING_OBJECT_TYPE),
            gab.get_is_rotationally_symmetric(GRASPING_OBJECT_TYPE)]


def get_rotationally_symmetrical_grasping_object():
    orientation = get_orientation_object()
    return RotationallySymmetricalGraspingObject(GRASPING_OBJECT_TYPE, orientation)


def get_grasping_object():
    orientation = get_grasping_object()
    return GraspingObject(GRASPING_OBJECT_TYPE, orientation)


def get_orientation_object():
    return Orientation(FACING_ROBOT_FACE, BOTTOM_FACE)


def get_grasping_object_as_true_mln_database(mln, ground_atoms):
    database = Database(mln)
    map(database.add_true_ground_atom, ground_atoms)

    return database


def get_grasping_object_as_false_mln_database(mln, ground_atoms):
    database = Database(mln)
    map(database.add_false_ground_atom, ground_atoms)

    return database
