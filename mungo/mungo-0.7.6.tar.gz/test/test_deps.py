import unittest

from mungo.cli import create_environment
from mungo.repositorydata import RepositoryData


def packages(nodes):
    return set(map(lambda x: (x.name, x.version), nodes))


# TODO: tear down, do not print and open DAG
class TestDependencies(unittest.TestCase):

    def setUp(self):
        repodata = RepositoryData._from_file("fakerepo/linux-64", "fakerepo/linux-64/repodata.json",
                                             cache=True,
                                             remote_mtime=0)
        repodata = RepositoryData._from_file("fakerepo/noarch", "fakerepo/noarch/repodata.json",
                                             cache=True,
                                             remote_mtime=0)

    def test_simple_dependency_BA(self):
        p = packages(create_environment("foo", ["fakerepo"], {"B"},
                                        [], jobs=1, dag=True, ask_for_confirmation=True, offline=True,
                                        force_download=False))
        self.assertEqual(p, {("A", ("0.1.0", "py37")), ("B", ("0.3.0", "py37"))})

    def test_simple_dependency_CAB(self):
        p = packages(create_environment("foo", ["fakerepo"], {"C"},
                                        [], jobs=1, dag=True, ask_for_confirmation=True, offline=True,
                                        force_download=False))
        self.assertEqual(p, {("C", ("0.2.0", "py37")), ("B", ("0.2.0", "py37")), ("A", ("0.1.0", "py37"))})

    def test_or_dependency_DB(self):
        p = packages(create_environment("foo", ["fakerepo"], {"D"},
                                        [], jobs=1, dag=True, ask_for_confirmation=True, offline=True,
                                        force_download=False))
        self.assertEqual(p, {("D", ("0.1.0", "py37")), ("B", ("0.3.0", "py37")), ("A", ("0.1.0", "py37"))})

    def test_buildname_dependency_FG(self):
        p = packages(create_environment("foo", ["fakerepo"], {"F"},
                                        [], jobs=1, dag=True, ask_for_confirmation=True, offline=True,
                                        force_download=False))
        self.assertEqual(p, {("F", ("0.1.0", "py37")), ("G", ("0.1.0", "foo"))})

    def test_cyclic_dependency_HI(self):
        p = packages(create_environment("foo", ["fakerepo"], {"H"},
                                        [], jobs=1, dag=True, ask_for_confirmation=True, offline=True,
                                        force_download=False))
        self.assertEqual(p, {("H", ("0.1.0", "py37")), ("I", ("0.1.0", "py37"))})


if __name__ == '__main__':
    unittest.main()
