"""You need to run the tests here like this:
$ PYTHONWARNINGS=all bin/nosetests -sv
"""

from bob.db.base import Database


def test_database_deprecations():
    database = Database()
    low_level_names = ('train', 'dev')
    high_level_names = ('world', 'dev')
    database.convert_names_to_lowlevel(
        'world', low_level_names, high_level_names)
    database.convert_names_to_highlevel(
        'train', low_level_names, high_level_names)
    database.check_parameter_for_validity(
        'world', 'groups', high_level_names, None)
    database.check_parameters_for_validity(
        'world', 'groups', high_level_names, None)
