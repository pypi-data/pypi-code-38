#inteded to be superclass for tables and charts

from clarusui.layout import Element
from abc import ABCMeta
from clarus.models import ApiResponse
from pandas import DataFrame
from pandas import Series
from six import StringIO
from six import string_types
import pandas
import warnings


#TODO change internal datastructure (self._parsedResponse) to a dataframe
class GridViz(Element):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        super(GridViz, self).__init__(response, **options)
        if isinstance(self.response, Series):
            self._dataFrame = self.response.to_frame()
        if isinstance(self.response, DataFrame):
#reindex to the first actual data column
            self.response = self.response.set_index(self.response.columns[0])
            self._dataFrame = self.response
        if isinstance(self.response, ApiResponse):
            results = self.response.results
            df = DataFrame(results)
            df = df.set_index(df.columns[0])
            df.index.name = self.response.get_col_headers()[0] if self.response.get_result_title() is None else self.response.get_result_title()
            self._dataFrame = df
        if isinstance(self.response, string_types):
            csvFile = StringIO(self.response)
            df = pandas.read_csv(csvFile)
            df = df.set_index(df.columns[0])
            self._dataFrame = df
            
        self.colFilter  = self._pop_filter('colFilter')
        self.rowFilter  = self._pop_filter('rowFilter')
        self.excludeCols  = self._pop_filter('excludeCols')
        self.excludeRows  = self._pop_filter('excludeRows')
            
        pivot = self.options.pop('pivot', False)
        if pivot:
            self.pivot()      

    @classmethod
    def from_apiresponse(cls, apiResponse, **options):
        return cls(apiResponse, **options)

    @classmethod
    def from_csv(cls, csvText, **options):
        return cls(csvText, **options)
       
    @classmethod
    def from_dataframe(cls, dataFrame, **options):
        return cls(dataFrame, **options)
    
    def _pop_filter(self, filterName):
        filter = self.options.pop(filterName, None)
        if filter is not None:
            if not isinstance(filter, list):
                filter = filter.split(',')
        return filter
    
    def pivot(self):
        self._dataFrame = self._dataFrame.T
        return self
    
    def _get_filtered_row_headers(self):
        unfiltered = list(self._dataFrame.index)
        
        if not self._dataFrame.index.is_unique:
            if self.rowFilter is not None or self.excludeRows is not None:
                warnings.warn("Non unique row index, ignoring filter")
                return unfiltered
        
        filtered = []

        for rowHeader in unfiltered:
            if (self.rowFilter==None or rowHeader in self.rowFilter):
                filtered.append(rowHeader)
        
        if self.excludeRows is not None:
            filtered = [item for item in filtered if item not in self.excludeRows]
        return filtered
    
    def _get_filtered_col_headers(self):
        unfiltered = list(self._dataFrame)
        filtered = []

        for colHeader in unfiltered:
            if (self.colFilter==None or colHeader in self.colFilter):
                filtered.append(colHeader)
        
        if self.excludeCols is not None:
            filtered = [item for item in filtered if item not in self.excludeCols]
            
        return filtered
            
        
    def _get_values(self, col):
        values = []
        rows = self._get_filtered_row_headers()
        for row in rows:
            values.append(self._dataFrame.at[row, col])
        return values
    
    def _get_value(self, row, col):
        if self._dataFrame.index.is_unique:
            return self._dataFrame.at[row, col]
        else:
            return self._dataFrame.iat[row, col]
        

