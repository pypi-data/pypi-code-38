import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict
from tabulate import tabulate


@dataclass
class OutputString:
    """ An output given as a list of strings

    Attributes:
        data (List[str]): A list of strings

    """
    data: List[str] = field(default_factory=list)
    # name: str = None

    def __str__(self):
        return '\n'.join(self.data)


@dataclass
class OutputTable:
    """ An output table given as a list of dictionaries.

    It can be presented (and used) as a pandas dataframe or a markdown table

    Attributes:
        data (List[dict]): A list of dictionaries

    """
    data: List[dict] = field(default_factory=list)

    @property
    def to_markdown(self):
        """str: converts data to a markdown table using tabulate."""
        return self.convert_data_to_markdown_table(self.data)

    @property
    def to_panda_dataframe(self):
        return self.convert_data_to_dataframe(self.data)

    @property
    def to_quantity_value(self):
        out = OutputTable()
        out.data = self.change_dict_to_quantity_value_data(self.data[0])
        return out

    def retrieve(self, search_field, search_value, find_field):
        res = [d[find_field] for d in self.data if d[search_field] == search_value]
        return res[0]

    def retrieve_column_to_list(self, column_name):
        return self.to_panda_dataframe[column_name].tolist()

    @staticmethod
    def change_dict_to_quantity_value_data(dict):
        # out = OutputTable()
        out = []
        for d in dict:
            out.append({'quantity': d, 'value': dict[d]})
            # out.data.append({'quantity': d, 'value': dict[d]})
        return out

    @staticmethod
    def convert_data_to_dataframe(list_of_dicts):
        res = pd.DataFrame(list_of_dicts,
                           columns=list(list_of_dicts[0].keys()))
        return res

    @staticmethod
    def convert_data_to_markdown_table(list_of_dicts, table_format="pipe", float_fmt=".3E"):
        ftm_tbl = tabulate(list_of_dicts,
                           headers='keys',
                           tablefmt=table_format,
                           floatfmt=float_fmt)
        return ftm_tbl

    def __str__(self):
        return self.to_markdown

@dataclass
class OutputExtended:
    OutputTables: Dict[str, OutputTable] = field(default_factory=dict)
    OutputStrings: Dict[str, OutputString] = field(default_factory=dict)
