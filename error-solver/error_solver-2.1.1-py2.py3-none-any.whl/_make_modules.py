import os
from data import get_file_path, get_data_folder
from solvers import ErrorSolver


if __name__ == '__main__':
    modules = ('cylinder', 'wire_load')

    for mod in modules:
        solver = ErrorSolver.from_file(get_file_path(mod))
        solver.write_python(os.path.join(get_data_folder(), '_{}.py'.format(mod)))
