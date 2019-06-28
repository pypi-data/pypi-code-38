from typing import List

import pandas as pd

from treelab.consts import FieldType


class TableContent:
    def __init__(self, field_types: List[FieldType], df: pd.DataFrame):
        self.field_types = field_types
        self.field_names = df.columns
        self.df = df


class ColumnConfig:
    def __init__(self, field_name: str, field_type: FieldType = FieldType.TEXT, order: int = 0, foreign_table_id: str = ''):
        self.field_name = field_name
        self.order = order
        self.foreign_table_id = foreign_table_id
        self.field_type = field_type


class CellUpdateConfig:
    """
    the object of the specified data
    """
    
    def __init__(self, cell_value: str = "", foreign_key: str = None, field_type: FieldType = FieldType.TEXT):
        self.cell_value = cell_value
        self.field_type = field_type
        self.foreign_key = foreign_key
