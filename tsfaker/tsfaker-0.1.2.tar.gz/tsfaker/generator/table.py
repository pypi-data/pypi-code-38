from typing import Optional, Union

import numpy as np
import pandas as pd
from tableschema import Schema

from tsfaker.generator import column


class TableGenerator:
    def __init__(self, source_descriptor: Union[str, dict], nrows: int):
        self.schema = Schema(source_descriptor)
        self.nrows = nrows

    def get_array(self) -> np.array:
        columns = []
        for field in self.schema.fields:
            column_generator_class = getattr(column, field.type.capitalize())
            column_generator = column_generator_class(self.nrows)
            columns.append(column_generator.get_2d_array())

        if len(columns) == 1:
            return columns[0]
        else:
            return np.concatenate(columns, axis=1)

    def get_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(data=self.get_array(), columns=self.schema.field_names)

    def get_string(self, **kwargs) -> Optional[str]:
        df = self.get_dataframe()
        return df.to_string(**kwargs)

    def get_csv(self, **kwargs) -> Optional[str]:
        df = self.get_dataframe()
        index = kwargs.pop('index', False)
        return df.to_csv(index=index, **kwargs)
