"""
test atomtools
"""
import os
import numpy as np
import atomtools
import ase.build


BASEDIR= os.path.dirname(os.path.abspath(__file__))
np.set_printoptions(precision=3, suppress=True, linewidth=100)

class Test_Atoms(object):
    """docstring for Test_Atoms"""
    def __init__(self, positions, cell):
        super(Test_Atoms, self).__init__()
        self.positions = positions
        self.cell = cell

def test_get_distance_matrix():
    test_cases = [
        {
            'positions' : np.array([
               [ 0.  ,  0.  ,  0.  ],
               [ 0.  ,  0.  , -1.11],
               [ 0.92, -0.61, -0.11],
               [-0.99, -0.49, -0.11],
               [ 0.07,  1.1 , -0.11],
               [ 0.  ,  0.  ,  1.76]])
        },
        {
            'positions' : np.array([
               [ 0.7579,  0.    ,  0.    ],
               [ 1.8679,  0.    ,  0.    ],
               [ 0.8679, -0.8569, -0.6959],
               [ 0.8679,  1.0326, -0.3922],
               [ 0.8679, -0.1758,  1.0881],
               [-1.0021,  0.    ,  0.    ]]),
        },
        {
            'positions' : Test_Atoms(positions=np.array([
               [ 0.7579,  0.    ,  0.    ],
               [ 1.8679,  0.    ,  0.    ],
               [ 0.8679, -0.8569, -0.6959],
               [ 0.8679,  1.0326, -0.3922],
               [ 0.8679, -0.1758,  1.0881],
               [-1.0021,  0.    ,  0.    ]])+np.array([1.5, 1.5, 1.5]), cell=np.array([
               [3,0,0], [0, 3, 0], [0, 0, 3]]))
        },
    ]

    for case in test_cases:
        case.update({'debug' : True})
        print(atomtools.geo.get_distance_matrix(**case))

    print(atomtools.geo.dist_change_matrix(test_cases[0]['positions'], 1))

def test_zmat():
    """
    test zmat
    def input_standard_pos_transform(inp_pos, std_pos, t_vals,
        std_to_inp=True, is_coord = False, debug=False):

    """
    test_cases = [
        {
            'inp_pos' : np.array([
               [ 0.  ,  0.  ,  0.  ],
               [ 0.  ,  0.  , -1.11],
               [ 0.92, -0.61, -0.11],
               [-0.99, -0.49, -0.11],
               [ 0.07,  1.1 , -0.11],
               [ 0.  ,  0.  ,  1.76]]),
            'std_pos' : np.array([
               [ 0.7579,  0.    ,  0.    ],
               [ 1.8679,  0.    ,  0.    ],
               [ 0.8679, -0.8569, -0.6959],
               [ 0.8679,  1.0326, -0.3922],
               [ 0.8679, -0.1758,  1.0881],
               [-1.0021,  0.    ,  0.    ]]),

        },
        {
            'inp_pos' : np.array([
               [-1.4951,  0.7264,  0.    ],
               [-1.5688, -0.6965,  0.    ],
               [-2.6259, -0.0039,  0.    ],
               [-0.868 ,  1.8174,  0.    ]]),
            'std_pos' : np.array([
               [-0.0018,  0.475 ,  0.    ],
               [ 0.6433,  1.7454,  0.    ],
               [-0.6183,  1.6716,  0.    ],
               [-0.0018, -0.7834,  0.    ]]),
        },
        {
            'inp_pos' : np.array([[ 0.493 ,  0.    ,  0.    ],
                       [-0.6573,  0.    ,  0.    ]]),
            'std_pos' : np.array([[ 0.    ,  0.    ,  0.493 ],
               [ 0.    ,  0.    , -0.6573]]),
        },
    ]

    for case in test_cases:
        case.update({'debug' : True, 'std_vec' : case['inp_pos'][0:2]})
        print(atomtools.geo.input_standard_pos_transform(**case))

def test_get_contact_matrix():
    # import atomse.io
    test_cases = [
        {
            'positions' : ase.build.molecule('CH4')
        },
        {
            'positions' : ase.build.molecule('HCN')
        },
        {
            'positions' : ase.build.molecule('C6H6')
        },
        {
            'positions' : ase.build.molecule('H2CO')
        },
        # {
        #     'positions' : atomse.io.read(BASEDIR+'/../test_cases/6.log')
        # },
    ]
    for case in test_cases:
        case.update({'debug' : True,})
        print('get_contact_matrix', atomtools.geo.get_contact_matrix(**case))

def test_get_atoms_name():
    x = ase.build.molecule("CH4")
    print(atomtools.name.get_atoms_name(x))


def test_get_atoms_size():
    x = ase.build.molecule("CH4")
    print(atomtools.geo.get_atoms_size(x))



def test():
    print(atomtools.__file__)
    print(atomtools.version())
    test_get_distance_matrix()
    test_get_contact_matrix()
    test_get_atoms_name()
    test_get_atoms_size()
    # test_zmat()



if __name__ == '__main__':
    test()

