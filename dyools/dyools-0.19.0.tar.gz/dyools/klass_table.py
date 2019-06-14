from __future__ import (absolute_import, division, print_function, unicode_literals)

from operator import itemgetter

from past.builtins import basestring


class Table(object):
    def __init__(self, data):
        self.data = data
        self.col_idx = []
        self.row_idx = []
        self.nrows = len(data)
        self.ncols = len(data[0]) if data else 0
        self.index_rows = [[x for x in range(self.nrows)]]
        self.index_cols = [[x for x in range(self.ncols)]]

    def _normalize_idx(self, idx):
        if not isinstance(idx, (list, tuple)):
            idx = [idx]
        return idx

    def remove_rows(self, idx):
        idx = self._normalize_idx(idx)
        idx = sorted(list(set(idx)), reverse=True)
        for line_idx in idx:
            del self.data[line_idx]
        self._reindex()

    def remove_cols(self, idx):
        idx = self._normalize_idx(idx)
        idx = sorted(list(set(idx)), reverse=True)
        for col_idx in idx:
            for line in self.data:
                del line[col_idx]
        self._reindex()

    def set_col_index(self, idx):
        idx = self._normalize_idx(idx)
        self.col_idx = idx
        self._reindex()

    def set_row_index(self, idx):
        idx = self._normalize_idx(idx)
        self.row_idx = idx
        self._reindex()

    def get_rows(self, idx):
        idx = self._normalize_idx(idx)
        return [self.data[item_idx] for item_idx in idx]

    def get_columns(self, idx):
        idx = self._normalize_idx(idx)
        return [list(map(itemgetter(item_idx), self.data)) for item_idx in idx]

    def _reindex(self):
        self.index_rows = self.get_rows(self.row_idx)
        self.index_cols = self.get_columns(self.col_idx)
        self.nrows = len(self.data)
        self.ncols = len(self.data[0]) if self.data else 0

    def get_value_by_idx(self, row_idx, col_idx):
        assert isinstance(row_idx, int) and isinstance(col_idx, int), "the index should be an integer"
        assert row_idx < self.nrows, "the index is out of range"
        assert col_idx < self.ncols, "the index is out of range"
        return self.data[row_idx][col_idx]

    def get_value_by_row_col(self, row_idx=[], col_idx=[]):
        if isinstance(row_idx, basestring):
            row_idx = row_idx.split(';')
        if isinstance(col_idx, basestring):
            col_idx = col_idx.split(';')
        row_idx = self._normalize_idx(row_idx)
        col_idx = self._normalize_idx(col_idx)
        assert len(row_idx) == len(self.index_rows), "please provide the same number of rows indexes"
        assert len(col_idx) == len(self.index_cols), "please provide the same number of columns indexes"
        row_tuples = list(zip(row_idx, self.index_rows))
        col_tuples = list(zip(col_idx, self.index_cols))
        row_indices = []
        for i, line in row_tuples:
            _row_indices = [x for x, y in enumerate(line) if y == i]
            if row_indices:
                row_indices = list(set(row_indices) & set(_row_indices))
            else:
                row_indices = _row_indices
        col_indices = []
        for i, line in col_tuples:
            _col_indices = [x for x, y in enumerate(line) if y == i]
            if col_indices:
                col_indices = list(set(col_indices) & set(_col_indices))
            else:
                col_indices = _col_indices
        assert col_indices and row_indices, "can not found the indexes for col=%s and row=%s" % (col_idx, row_idx)
        row_indices, col_indices = row_indices[0], col_indices[0]
        for i, row in enumerate(self.data):
            for j, col in enumerate(self.data[i]):
                if i == col_indices and j == row_indices:
                    return self.data[i][j]
        return None

    def get_flat(self, empty=True):
        tables = []
        for i, row_tuple in enumerate(zip(*self.index_rows)):
            for j, col_tuple in enumerate(zip(*self.index_cols)):
                if i in self.row_idx or j in self.col_idx:
                    continue
                value = self[row_tuple:col_tuple]
                if not empty:
                    if isinstance(value, basestring):
                        if not value.strip():
                            continue
                    if not value:
                        continue
                line = list(row_tuple) + list(col_tuple) + [value]
                tables.append(line)
        return tables

    def get_dict(self):
        return dict(self.data)

    def get_data(self):
        return self.data

    def __getitem__(self, item):
        if isinstance(item, slice):
            if isinstance(item.start, int) and isinstance(item.stop, int):
                return self.get_value_by_idx(item.start, item.stop)
            else:
                return self.get_value_by_row_col(item.start, item.stop)
        elif isinstance(item, int):
            return self.get_columns(item)
        for col_line in self.index_cols:
            if item in col_line:
                return self.get_columns(col_line.index(item))
        for row_line in self.index_rows:
            if item in row_line:
                return self.get_columns(row_line.index(item))
        raise IndexError()
