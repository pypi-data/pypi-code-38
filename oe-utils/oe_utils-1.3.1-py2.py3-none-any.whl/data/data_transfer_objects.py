# -*- coding: utf-8 -*-


class ResultDTO:
    '''
    A DTO for returning results
    '''

    def __init__(self, data, total, aggregations=None):
        self.data = data
        self.total = total
        self.aggregations = aggregations
