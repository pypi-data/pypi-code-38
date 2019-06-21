# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/
from PyQt5 import QtCore

import pandas as pd


class PandasDataFrameModel(QtCore.QAbstractTableModel):
    """
    Class implementing a QAbstractTableModel to populate a QTableView from a pandas data frame

    This class was adopted from a post from Edwin Christian Yllanes Cucho under the MIT license:
    https://github.com/eyllanesc/stackoverflow/blob/master/questions/44603119/
    """
    def __init__(self, data_frame=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._data_frame = data_frame

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._data_frame.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return self._data_frame.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._data_frame.ix[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._data_frame.index[index.row()]
        col = self._data_frame.columns[index.column()]
        try:
            value = value.toPyObject()
            self._data_frame.set_value(row, col, value)
            return True
        except ValueError:
            return False

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._data_frame.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._data_frame.columns)

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        return flags
