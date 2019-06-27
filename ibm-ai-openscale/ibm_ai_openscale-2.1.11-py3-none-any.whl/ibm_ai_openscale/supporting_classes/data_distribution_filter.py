# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2019
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


class Filter:
    @staticmethod
    def eq(field, value):
        return '{}:eq:{}'.format(field, value)

    @staticmethod
    def gt(field, value):
        return '{}:gt:{}'.format(field, value)

    @staticmethod
    def gte(field, value):
        return '{}:gte:{}'.format(field, value)

    @staticmethod
    def lt(field, value):
        return '{}:lt:{}'.format(field, value)

    @staticmethod
    def lte(field, value):
        return '{}:lte:{}'.format(field, value)

    @staticmethod
    def isin(field, value):
        return '{}:in:[{}]'.format(field, ','.join(value))