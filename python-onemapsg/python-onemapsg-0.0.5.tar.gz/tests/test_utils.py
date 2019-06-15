# -*- coding: utf-8 -*-

from unittest.mock import MagicMock, patch

import pytest

from onemapsg import status
from onemapsg.response import GeocodeInfo, Response, RouteResult, SearchResult
from onemapsg.utils import (
    coerce_response,
    construct_reverse_geocode_svy21_query,
    construct_route_query, construct_search_query,
    get_route_class,
    get_search_class,
    get_reverse_geocode_svy21_class,
    make_request, to_dict,
    validate_address_type
)


def test_coerce_response():
    """Should correctly create a class object from dictionary."""
    class TestClass:
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c
    instance = coerce_response(TestClass, {'a': 1, 'b': 2, 'c': 3})
    assert instance.a == 1
    assert instance.b == 2
    assert instance.c == 3


def test_to_dict():
    """Should return correctly constructed dictionary from class."""
    class TestClass:
        def __init__(self, a, b, c):
            self.a = a
            self.b = b
            self.c = c

    obj = TestClass([1, 2, 3], {'nest': {'dictionary': 'object'}}, 'string')
    d = to_dict(obj)
    assert isinstance(d['a'], list)
    assert d['a'] == [1, 2, 3]
    assert isinstance(d['b'], dict)
    assert d['b']['nest'] == {'dictionary': 'object'}
    assert d['c'] == 'string'


@patch('requests.get')
def test_make_get_request(mock_get):
    """Should return Response instance."""
    mock_json = MagicMock()
    mock_json.return_value = {'detail': 'some data'}
    mock_get.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        json=mock_json
    )
    response = make_request('https://testendpoint.com/api/test')
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'detail': 'some data'}


@patch('requests.post')
def test_make_post_request(mock_post):
    """Should return Response instance."""
    mock_json = MagicMock()
    mock_json.return_value = {'detail': 'some data'}
    mock_post.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        json=mock_json
    )
    response = make_request(
        'https://testendpoint.com/api/test',
        method='post',
        data={'data': 'some data'}
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {'detail': 'some data'}


@patch('requests.post')
def test_make_post_request_without_data(mock_post):
    """Should return ValueError."""
    with pytest.raises(ValueError) as err:
        make_request('https://testendpoint.com/api/test', method='post')
        assert str(err) == str(ValueError(
            'Data must be provided for POST, PUT and PATCH requests.'))


def test_construct_search_query():
    """Should construct correct search query."""
    url = construct_search_query('some address', True, True, 1)
    assert url == ('https://developers.onemap.sg/'
                   'commonapi/search?'
                   'searchVal=some+address&'
                   'returnGeom=Y&'
                   'getAddrDetails=Y&'
                   'pageNum=1')


def test_get_search_class():
    """Should return SearchResult class."""
    klass = get_search_class()
    assert klass == SearchResult


def test_construct_route_query():
    """Should construct correct route query."""
    url = construct_route_query('1.12,3.21', '1.02,1.05', 'drive',
                                None, 'sometoken')
    assert url == ('https://developers.onemap.sg/'
                   'privateapi/routingsvc/route?'
                   'start=1.12,3.21&'
                   'end=1.02,1.05&'
                   'routeType=drive&'
                   'token=sometoken')
    opts = {
        'date': '2018-09-01',
        'time': '15:30:00',
        'mode': 'BUS'
    }
    url = construct_route_query('1.12,3.21', '1.02,1.05', 'pt',
                                opts, 'sometoken')
    assert url == ('https://developers.onemap.sg/'
                   'privateapi/routingsvc/route?'
                   'start=1.12,3.21&'
                   'end=1.02,1.05&'
                   'routeType=pt&'
                   'date=2018-09-01&'
                   'time=15:30:00&'
                   'mode=BUS&'
                   'token=sometoken')


def test_get_route_class():
    """Should return RouteResult class."""
    klass = get_route_class()
    assert klass == RouteResult


def test_validate_address_type():
    """Should correctly validate address type for reverse geocode."""
    with pytest.raises(ValueError) as err:
        validate_address_type('badtype')
        assert str(err) == 'Invalid `addressType` value - can only be `HDB` or `All`'
    validated = validate_address_type('all')
    assert validated == 'all'
    validated = validate_address_type('hdb')
    assert validated == 'hdb'
    validated = validate_address_type('ALL')
    assert validated == 'all'
    validated = validate_address_type('HDB')
    assert validated == 'hdb'


def test_construct_reverse_geocode_svy21_query():
    """Should construct correct reverse geocode query."""
    location = (24291.97788882387, 31373.0117224489)
    token = 'sometoken'
    url = construct_reverse_geocode_svy21_query(location, token, other_features=True)
    assert url == ('https://developers.onemap.sg/'
                   'privateapi/commonsvc/revgeocodexy?'
                   'location=24291.97788882387,31373.0117224489&'
                   'token=sometoken&'
                   'buffer=10&'
                   'addressType=all&'
                   'otherFeatures=Y')


def test_get_reverse_geocode_svy21_class():
    """Should return GeocodeInfo class."""
    klass = get_reverse_geocode_svy21_class()
    assert klass == GeocodeInfo
