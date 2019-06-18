# -*- coding: utf-8 -*-


"""gitcher test suite"""

import contextlib
import shutil
import unittest
import tempfile
from os import makedirs
from os.path import join
from typing import Callable
from unittest import TestCase

# Authorship
__author__ = 'Borja González Seoane'
__copyright__ = 'Copyright 2019, Borja González Seoane'
__credits__ = 'Borja González Seoane'
__license__ = 'LICENSE'
__version__ = '2.1'
__maintainer__ = 'Borja González Seoane'
__email__ = 'dev@glezseoane.com'
__status__ = 'Production'


class TestModelDevelopment(TestCase):
    """Test container class for model_development package."""

    def test_print_current_on_prof(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_set_prof(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_set_prof_global(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_add_prof(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_add_prof_fast(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_update_prof(self):
        """Simulate the order tu check the correct operative effect."""
        pass

    def test_delete_prof(self):
        """Simulate the order tu check the correct operative effect."""
        pass


if __name__ == '__main__':
    unittest.main()


# ===============================================
# =         Test general util functions         =
# ===============================================
@contextlib.contextmanager
def use_tmp_directory():
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)


def generate_well_formed_devdir_structure(root_dir: str) -> [str]:
    """Creates a well formed directory path structure."""
    paths = [join(root_dir, 'Projects', 'ACME', 'roadrunner-final-trap'),
             join(root_dir, 'Projects', 'Personal', 'free-project'),
             join(root_dir, 'Projects', 'Personal', 'my-own-jarvis'),
             join(root_dir, 'Projects', 'University', 'logical-project'),
             join(root_dir, 'Projects', 'University', 'parser-project'),
             join(root_dir, 'Projects', 'University', 'Compilers',
                  'mips-project'),
             join(root_dir, 'Projects', 'University', 'Compilers',
                  'intel-project'),
             join(root_dir, 'Reference', 'ACME',
                  'roadrunner-previous-trap'),
             join(root_dir, 'Reference', 'University',
                  'my-classmate-project')]

    return paths


def generate_bad_formed_devdir_structure(root_dir: str) -> [str]:
    """Creates a bad formed directory path structure."""
    paths = [join(root_dir, 'projects', 'ACME', 'Roadrunner_final_trap'),
             join(root_dir, 'projects', 'Personal', 'free_project'),
             join(root_dir, 'projects', 'Personal', 'my_own_jarvis'),
             join(root_dir, 'projects', 'University', 'logical_project'),
             join(root_dir, 'projects', 'University', 'parser_project'),
             join(root_dir, 'projects', 'University', 'Compilers',
                  'mips_project'),
             join(root_dir, 'projects', 'University', 'Compilers',
                  'intel_project'),
             join(root_dir, 'Reference', 'ACME',
                  'Roadrunner_previous_trap'),
             join(root_dir, 'Reference', 'University',
                  'my_classmate_project')]

    return paths


@contextlib.contextmanager
def create_mock_devdir(path_generator: Callable) -> str:
    """Creates a temporal directory attending to passed path structure
    generator reply and simulate a repository inside."""
    root_dir = tempfile.mkdtemp()
    paths = path_generator(root_dir)

    for path in paths:
        makedirs(path, exist_ok=True)

    '''Final structure:

    Projects
        ACME
            * roadrunner-final-trap
        Personal
            * free-project
            * my-own-jarvis
        University
            Compilers
                * mips-project
                * intel-project
            * logical-project
            * parser-project
    Reference
        ACME
            * roadrunner-previous-trap
        University
            * my-classmate-project
    '''

    project_paths = paths

    # Now inits a sample repo in every project
    commiter = 'jane <janedoe@home>'

    for p_path in project_paths:

        repo = git.Repo.init(p_path)

        for i in range(1, 5):
            open(join(p_path, str(i) + '.py'), "w+").close()

        repo.git.add('--all')
        repo.git.commit('-m', 'Commit test effects #1', author=commiter)

        with open(join(p_path, 'coffee.md'), "w+") as f:
            f.writelines("The best coffee in the world is prepared in "
                         "Italy.")
            f.close()

        repo.git.add('--all')
        repo.git.commit('-m', 'Commit test effects #2', author=commiter)

        with open(join(p_path, 'serradura.txt'), "w+") as f:
            f.writelines("My favourite Portuguese dessert is the "
                         "'serradura'. Prove it! It is delicious.")
            f.close()

        repo.git.add('--all')
        repo.git.commit('-m', 'Commit test effects #3', author=commiter)

    try:
        yield root_dir
    finally:
        shutil.rmtree(root_dir)
