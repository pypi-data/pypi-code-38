
from asyncqlio import (
    Column,
    Integer,
    String,
    Timestamp,
)

from .base import WebTable


class MergeLog(WebTable, table_name='merge_logs'):
    source = Column(String, primary_key=True)
    original = Column.with_name('original_id', Integer, primary_key=True)
    destination = Column.with_name('destination_id', Integer, primary_key=True)

    merger = Column(Integer)

    created = Column(Timestamp)
