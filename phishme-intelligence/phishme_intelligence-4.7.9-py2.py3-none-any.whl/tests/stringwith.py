import re


class StringWith(str):
    """
    This class is meant to be use by the 'assert_called_with' mock functions
    it allows you to specify a regular expression to match a string.

    For example if you want to make sure a function sends 'INSERT INTO' you
    can try something like:

        sqlite.sqlite3.connect().execute.assert_called_with(StringWith('INSERT INTO'))

    This will match on any string that contains the phrase INSERT INTO leaving
    the developer free to change other parts of the query without having to
    change the test
    """
    def __eq__(self, other):
        return re.search(str(self), str(other)) is not None
