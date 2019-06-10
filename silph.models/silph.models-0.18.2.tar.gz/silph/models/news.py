
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    String,
    Text,
    Timestamp,
    Serial,
)

from .base import WebTable


class RedditSubmission(WebTable, table_name='subreddit_submissions'):
    id = Column(Serial, primary_key=True, unique=True)

    name = Column(String(64), nullable=False)
    title = Column(Text, nullable=False)
    upvotes = Column(Integer, nullable=False, default=0)
    url = Column(Text)

    news_team_alerted = Column(SmallInt, nullable=False, default=0)
    mod_team_alerted = Column(SmallInt, nullable=False, default=0)

    posted = Column.with_name('created_utc', Integer, nullable=False)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)
