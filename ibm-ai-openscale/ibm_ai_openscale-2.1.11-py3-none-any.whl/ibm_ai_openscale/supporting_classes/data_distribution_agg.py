# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class Agg:
    @staticmethod
    def count():
        return 'count'

    @staticmethod
    def sum(field):
        return '{}:sum'.format(field)

    @staticmethod
    def min(field):
        return '{}:min'.format(field)

    @staticmethod
    def max(field):
        return '{}:max'.format(field)

    @staticmethod
    def avg(field):
        return '{}:avg'.format(field)

    @staticmethod
    def stddev(field):
        return '{}:stddev'.format(field)

