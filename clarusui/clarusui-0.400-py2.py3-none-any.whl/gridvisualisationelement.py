#superclass for tables and charts
from abc import ABCMeta
import warnings
from six import StringIO, string_types
from pandas import DataFrame, Series
import pandas
from clarusui.layout import Element
from clarus.models import ApiResponse

class GridViz(Element):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        super(GridViz, self).__init__(response, **options)
        if isinstance(self.response, Series):
            self._data_frame = self.response.to_frame()
        if isinstance(self.response, DataFrame):
#reindex to the first actual data column
            self.response = self.response.set_index(self.response.columns[0])
            self._data_frame = self.response
        if isinstance(self.response, ApiResponse):
            results = self.response.results
            data_frame = DataFrame(results)
            data_frame = data_frame.set_index(data_frame.columns[0])
            data_frame.index.name = (self.response.get_col_headers()[0] if
                                     self.response.get_result_title() is None
                                     else self.response.get_result_title())
            self._data_frame = data_frame
        if isinstance(self.response, string_types):
            csv_file = StringIO(self.response)
            data_frame = pandas.read_csv(csv_file)
            data_frame = data_frame.set_index(data_frame.columns[0])
            self._data_frame = data_frame
            
        self.col_filter = self._pop_filter('colFilter')
        self.row_filter = self._pop_filter('rowFilter')
        self.exclude_cols = self._pop_filter('excludeCols')
        self.exclude_rows = self._pop_filter('excludeRows')
            
        pivot = self.options.pop('pivot', False)
        if pivot:
            self.pivot()      

    @classmethod
    def from_apiresponse(cls, api_response, **options):
        return cls(api_response, **options)

    @classmethod
    def from_csv(cls, csv_text, **options):
        return cls(csv_text, **options)
       
    @classmethod
    def from_dataframe(cls, data_frame, **options):
        return cls(data_frame, **options)
    
    def _pop_filter(self, filter_name):
        filter_values = self.options.pop(filter_name, None)
        if filter_values is not None:
            if not isinstance(filter_values, list):
                filter_values = filter_values.split(',')
        return filter_values
    
    def pivot(self):
        self._data_frame = self._data_frame.T
        return self
    
    def _get_filtered_row_headers(self):
        unfiltered = list(self._data_frame.index)
        
        if not self._data_frame.index.is_unique:
            if self.row_filter is not None or self.exclude_rows is not None:
                warnings.warn("Non unique row index, ignoring filter")
                return unfiltered
        
        filtered = []

        for row_header in unfiltered:
            if (self.row_filter is None or row_header in self.row_filter):
                filtered.append(row_header)
        
        if self.exclude_rows is not None:
            filtered = [item for item in filtered if item not in self.exclude_rows]
        return filtered
    
    def _get_filtered_col_headers(self):
        unfiltered = list(self._data_frame)
        filtered = []

        for col_header in unfiltered:
            if (self.col_filter is None or col_header in self.col_filter):
                filtered.append(col_header)
        
        if self.exclude_cols is not None:
            filtered = [item for item in filtered if item not in self.exclude_cols]
            
        return filtered
            
        
    def _get_values(self, col):
        values = []
        rows = self._get_filtered_row_headers()
        for row in rows:
            values.append(self._data_frame.at[row, col])
        return values
    
    def _get_value(self, row, col):
        if self._data_frame.index.is_unique:
            return self._data_frame.at[row, col]
        return self._data_frame.iat[row, col]
