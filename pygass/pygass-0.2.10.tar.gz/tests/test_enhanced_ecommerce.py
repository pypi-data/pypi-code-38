import pytest
import pygass.enhanced_ecommerce as pya
from pygass import constants as st
from tests.test_helper import (
    valid_state,
    valid_url,
    valid_message,
    assert_result,
)


pya.ANALYTICS_URL = "https://www.google-analytics.com/debug/collect"
st.ANALYTICS_CODE = "UA-10000000-1"
CLIENT_ID = 1337


TEST_PROXY_VALUES = {"ip": "111.111.111.111", "user_agent": "Test Agent"}
TEST_NON_INTERACTION_VALUES = {"non_interaction_hit": "1"}
TEST_QUEUE_TIME = {"queue_time": "560"}


TEST_ENHANCED_ECOMMERCE_IMPRESSION = [
    (
        {},
        "/debug/collect?il1pi1id=1337&il1pi1nm=Test+Product+3&v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fclient%2Fpageview",
    )
]


@pytest.mark.parametrize(
    "extra_params, expected", TEST_ENHANCED_ECOMMERCE_IMPRESSION
)
def test_enhanced_ecommerce_impression_data(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "page": "/test/client/pageview",
            "product_id": 1337,
            "product_name": "Test Product 3",
        },
        **extra_params
    )
    assert_result(pya.track_enhanced_ecommerce_impression(**params), expected)


TEST_ENHANCED_ECOMMERCE_ACTION = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fpage&pa=detail&pr1id=1337&pr1nm=Test+Product+3&pr1ca=Product+Test+Category&pr1qt=1",
    )
]


@pytest.mark.parametrize(
    "extra_params, expected", TEST_ENHANCED_ECOMMERCE_ACTION
)
def test_enhanced_ecommerce_action_data(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "action": "view",
            "category": "click",
            "page": "/test/page",
            "product_id": 1337,
            "product_name": "Test Product 3",
            "product_action": "detail",
            "product_category": "Product Test Category",
        },
        **extra_params
    )
    assert_result(pya.track_enhanced_ecommerce_action(**params), expected)


TEST_ENHANCED_ECOMMERCE_PURCHASE = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fpage&pa=purchase&pr1id=1337&pr1nm=Test+Product+3&pr1ca=Product+Test+Category&pr1br=product+brand&pr1qt=1&ti=20",
    )
]


@pytest.mark.parametrize(
    "extra_params, expected", TEST_ENHANCED_ECOMMERCE_PURCHASE
)
def test_enhanced_ecommerce_purchase(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "action": "click",
            "category": "cat01",
            "page": "/test/page",
            "transaction_id": "20",
            "product_id": 1337,
            "product_name": "Test Product 3",
            "product_category": "Product Test Category",
            "product_brand": "Product Brand",
        },
        **extra_params
    )
    assert_result(pya.track_enhanced_ecommerce_purchase(**params), expected)


TEST_ENHANCED_ECOMMERCE_CHECKOUT = [
    (
        {},
        "/Debug/Collect?V=1&Tid=UA-10000000-1&Cid=1337&T=Pageview&Dp=%2ftest%2fpage&Pa=Checkout&Pr1id=1337&Pr1nm=Test+Product+3&Pr1ca=Product+Test+Category&pr1qt=1",
    )
]


@pytest.mark.parametrize(
    "extra_params, expected", TEST_ENHANCED_ECOMMERCE_CHECKOUT
)
def test_enhanced_ecommerce_checkout(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "action": "click",
            "category": "cat01",
            "page": "/test/page",
            "transaction_id": "20",
            "product_id": 1337,
            "product_name": "Test Product 3",
            "product_category": "Product Test Category",
        },
        **extra_params
    )
    assert_result(pya.track_enhanced_ecommerce_checkout(**params), expected)


TEST_ENHANCED_ECOMMERCE_CHECKOUT_ADD = [
    (
        {},
        "/debug/collect?v=1&tid=UA-10000000-1&cid=1337&t=pageview&dp=%2Ftest%2Fpage&pa=add&pr1id=1337&pr1nm=Test+Product+3&pr1ca=Product+Test+Category&pr1qt=1",
    )
]


@pytest.mark.parametrize(
    "extra_params, expected", TEST_ENHANCED_ECOMMERCE_CHECKOUT_ADD
)
def test_enhanced_ecommerce_checkout_add(extra_params, expected):
    params = dict(
        {
            "client_id": CLIENT_ID,
            "action": "click",
            "category": "cat01",
            "page": "/test/page",
            "transaction_id": "20",
            "product_id": 1337,
            "product_name": "Test Product 3",
            "product_category": "Product Test Category",
        },
        **extra_params
    )
    assert_result(
        pya.track_enhanced_ecommerce_add_to_basket(**params), expected
    )


# @pytest.mark.parametrize("extra_params, expected", TEST_ENHANCED_ECOMMERCE_ACTION_IMPRESSION)
# def test_enhanced_ecommerce_action_impression_data(extra_params, expected):
#     params = dict(
#         {
#             "client_id": CLIENT_ID,
#             "action": "view",
#             "category": "click",
#             "product_id": 1337,
#             "product_name": "Test Product 3",
#             "product_action": "detail",
#         },
#         **extra_params
#     )
#     assert_result(pya.track_enhanced_ecommerce_action(**params), expected)
