from dataclasses import dataclass, field, fields
from .results_display import *
from typing import List

@dataclass
class NamedLogTable:
    name: str
    dict_list: List[dict] = field(default_factory=list)

    def to_markdown(self):
        return log_markdown_table(self.dict_list)

    def to_panda_dataframe(self):
        return log_dataframe(self.dict_list)


@dataclass
class NamedLogText:
    name: str
    text_list: List[str] = field(default_factory=list)


@dataclass
class Output:
    # log_text: List[str] = field(default_factory=list)
    log_text: NamedLogText = NamedLogText('main output text')
    log_table: NamedLogTable = NamedLogTable('main output table')

    tables: List[NamedLogTable] = field(default_factory=list)
    # Μπορώ να το κάνω να δίνει τα αποτελέσματα αρχικά λίστα από pandas και μετά σε αρχείο excel
    # με sheetname το όνομα κάθε NamedLogTable

    texts: List[NamedLogText] = field(default_factory=list)
    # Ομοίως σε json???

    # def __post_init__(self):


    @property
    def show_log_text(self):
        return '\n'.join(self.log_text)

