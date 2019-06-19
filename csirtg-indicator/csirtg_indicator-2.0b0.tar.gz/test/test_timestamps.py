from csirtg_indicator import Indicator
import arrow
import json
from csirtg_indicator.utils.ztime import parse_timestamp

TIMESTAMPS = {
    '2018-12-29 15:32:27 UTC'
}


def test_timestamps():
    for t in TIMESTAMPS:
        assert parse_timestamp(t)


def test_indicator_timestamps():
    f = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    l = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    r = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    i = Indicator('192.168.1.1', first_at=f, last_at=l, reported_at=r)

    assert i.first_at == arrow.get(f).datetime
    assert i.last_at == arrow.get(l).datetime
    assert i.reported_at == arrow.get(r).datetime

    s = str(i)
    i = json.loads(s)

    assert i['first_at'].upper() == f
    assert i['last_at'].upper() == l
    assert i['reported_at'].upper() == r


def test_indicator_timezones():
    t = '2017-03-06T11:41:48-06:00'
    a = arrow.get('2017-03-06T17:41:48Z').datetime

    i = Indicator('example.com', first_at=t, last_at=t, reported_at=t)

    assert i.first_at == a
    assert i.last_at == a
    assert i.reported_at == a


def test_last_at_only():
    l = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    i = Indicator('192.168.1.1', last_at=l)

    assert i.last_at == arrow.get(l).datetime

    s = str(i)
    i = json.loads(s)

    assert i.get('first_at') is None


def test_first_at_only():
    l = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    i = Indicator('192.168.1.1', first_at=l)

    assert i.first_at == arrow.get(l).datetime

    s = str(i)
    i = json.loads(s)

    assert i.get('last_at') is None


