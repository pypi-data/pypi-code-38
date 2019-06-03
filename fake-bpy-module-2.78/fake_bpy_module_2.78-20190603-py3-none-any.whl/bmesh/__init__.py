import sys
import typing
import bpy

from . import utils
from . import geometry
from . import ops
from . import types


def from_edit_mesh(mesh: 'bpy.types.Mesh') -> 'types.BMesh':
    '''Return a BMesh from this mesh, currently the mesh must already be in editmode. 

    :param mesh: The editmode mesh. 
    :type mesh: 'bpy.types.Mesh'
    :return:  the BMesh associated with this mesh. 
    '''

    pass


def new(use_operators: bool = True) -> 'types.BMesh':
    '''

    :param use_operators: Support calling operators in bmesh.ops (uses some extra memory per vert/edge/face). 
    :type use_operators: bool
    :return:  Return a new, empty BMesh. 
    '''

    pass


def update_edit_mesh(mesh: 'bpy.types.Mesh',
                     tessface: bool = True,
                     destructive: bool = True):
    '''Update the mesh after changes to the BMesh in editmode, optionally recalculating n-gon tessellation. 

    :param mesh: The editmode mesh. 
    :type mesh: 'bpy.types.Mesh'
    :param tessface: Option to recalculate n-gon tessellation. 
    :type tessface: bool
    :param destructive: Use when geometry has been added or removed. 
    :type destructive: bool
    '''

    pass
