import pytest
import pygass as pya
from pygass import constants as st
from tests.test_helper import valid_state, valid_url, valid_message, assert_result

pya.ANALYTICS_URL = "https://www.google-analytics.com/debug/collect"
st.ANALYTICS_CODE = "UA-10000000-1"
CLIENT_ID = 1337


TEST_PROXY_VALUES = {"ip": "111.111.111.111", "user_agent": "Test Agent"}
TEST_CAMPAIGN_VALUES = {"campaign_source": "google", "campaign_medium": "organic"}
TEST_NON_INTERACTION_VALUES = {"non_interaction_hit": "1"}
TEST_QUEUE_TIME = {"queue_time": "560"}


def test_add_ip_user_agent():
    results = pya.global_params({})
    assert results["uip"] is None
    assert results["ua"] is None

    results = pya.global_params({}, ip="127.0.0.1")
    assert results["uip"] == "127.0.0.1"
    assert results["ua"] is None

    results = pya.global_params({}, user_agent="Test Agent")
    assert results["uip"] is None
    assert results["ua"] == "Test Agent"

    results = pya.global_params({}, ip="127.0.0.1", user_agent="Test Agent")
    assert results["uip"] == "127.0.0.1"
    assert results["ua"] == "Test Agent"


TEST_PAGEVIEW = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview",
    ),
    (
        TEST_CAMPAIGN_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview&cs=google&cm=organic",
    ),
    (
        TEST_PROXY_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview&uip=111.111.111.111&ua=Test+Agent?_anon_uip=111.111.111.0",
    ),
    (
        TEST_NON_INTERACTION_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview&ni=1",
    ),
    (
        TEST_QUEUE_TIME,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview&qt=560",
    ),
    (
        {'document_referrer': 'http://example.com'},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview&dr=http%3A%2F%2Fexample.com",
    ),
]


@pytest.mark.parametrize("extra_params,expected", TEST_PAGEVIEW)
def test_pageview(extra_params, expected):
    params = dict(
        {"client_id": CLIENT_ID, "page": "/test/client/pageview"},
        **extra_params
    )
    assert_result(pya.track_pageview(**params), expected)

TEST_EVENT = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=event&ec=click&ea=start",
    ),
    (
        TEST_PROXY_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=event&ec=click&ea=start&uip=111.111.111.111&ua=Test+Agent?_anon_uip=111.111.111.0",
    ),
    (
        TEST_NON_INTERACTION_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=event&ec=click&ea=start&ni=1",
    ),
    (
        TEST_QUEUE_TIME,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=event&ec=click&ea=start&qt=560",
    ),
]


@pytest.mark.parametrize("extra_params,expected", TEST_EVENT)
def test_event(extra_params, expected):
    params = dict(
        {"client_id": CLIENT_ID, "action": "start", "category": "click"},
        **extra_params
    )
    assert_result(pya.track_event(**params), expected)


TEST_TRANSACTION = [
    ({}, "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=transaction&ti=1"),
    (
        TEST_PROXY_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=transaction&ti=1&uip=111.111.111.111&ua=Test+Agent?_anon_uip=111.111.111.0",
    ),
    (
        TEST_NON_INTERACTION_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=transaction&ti=1&ni=1",
    ),
    (
        TEST_QUEUE_TIME,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=transaction&ti=1&qt=560",
    ),
]


@pytest.mark.parametrize("extra_params,expected", TEST_TRANSACTION)
def test_transaction(extra_params, expected):
    params = dict(
        {"client_id": CLIENT_ID, "transaction_id": "1"}, **extra_params
    )
    assert_result(pya.track_transaction(**params), expected)


TEST_ITEM = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=item&ti=1&in=item+1&iq=1",
    ),
    (
        TEST_PROXY_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=item&ti=1&in=item+1&iq=1&uip=111.111.111.111&ua=Test+Agent?_anon_uip=111.111.111.0",
    ),
    (
        TEST_NON_INTERACTION_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=item&ti=1&in=item+1&iq=1&ni=1",
    ),
    (
        TEST_QUEUE_TIME,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=item&ti=1&in=item+1&iq=1&qt=560",
    ),

]


@pytest.mark.parametrize("extra_params,expected", TEST_ITEM)
def test_item(extra_params, expected):
    params = dict(
        {"client_id": CLIENT_ID, "transaction_id": 1, "name": "item 1"},
        **extra_params
    )
    assert_result(pya.track_item(**params), expected)


TEST_SOCIAL = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=social&sa=like&sn=facebook&st=%2Fhome",
    ),
    (
        TEST_PROXY_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=social&sa=like&sn=facebook&st=%2Fhome&uip=111.111.111.111&ua=Test+Agent?_anon_uip=111.111.111.0",
    ),
    (
        TEST_NON_INTERACTION_VALUES,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=social&sa=like&sn=facebook&st=%2Fhome&ni=1",
    ),
    (
        TEST_QUEUE_TIME,
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=social&sa=like&sn=facebook&st=%2Fhome&qt=560",
    ),
]



@pytest.mark.parametrize("extra_params,expected", TEST_SOCIAL)
def test_social(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "action": "like",
            "network": "facebook",
            "target": "/home",
        },
        **extra_params
    )
    assert_result(pya.track_social(**params), expected)
