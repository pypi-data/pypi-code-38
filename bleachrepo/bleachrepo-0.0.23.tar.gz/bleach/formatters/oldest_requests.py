import pytz
import datetime
from dateutil import parser

from bleach import config


LINE_TEMPLATE = "*{repo}*\n{title}\nopen for {days} days - owner is {user}\n{url}"


def doFormat(data):
    countOfOldest = config.CONFIG['countToDisplay']
    daysOpenThreshold = config.CONFIG['daysOpenThreshold']
    return _listOfOldestRequests(data, countOfOldest, daysOpenThreshold)


def _listOfOldestRequests(data, countOfOldest, daysOpenThreshold):
    assert type(data) == list
    sortedByDate = sorted(data, key=lambda record: record.createdAt)
    recordsToKeep = sortedByDate[:countOfOldest]

    formattedData = []
    for record in recordsToKeep:
        daysAlive = _calculateDaysAlive(record.createdAt)
        if daysAlive < daysOpenThreshold:
            continue

        formattedLine = LINE_TEMPLATE.format(
            repo=record.repo,
            title=record.title,
            days=daysAlive,
            user=record.user,
            url=record.url,
        )
        formattedData.append(formattedLine)

    return "\n\n".join(formattedData)


def _calculateDaysAlive(stringOfDateFrom):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    dateFrom = parser.parse(stringOfDateFrom)

    return (now - dateFrom).days
