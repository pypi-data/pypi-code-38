from rest_framework.test import APIClient
from chibi_user.tests import get_user_test as helper_get_user_test
from chibi import madness
from unittest import TestCase
from chibi.snippet.string import decode
from pprint import pformat
from chibi.parser import link_header
from chibi.fancy.is_type import is_iter
import json


tc = TestCase( '__init__' )
default_client = APIClient()


def change_user( user_pk=None ):
    default_client = APIClient()
    user_test, token_test = helper_get_user_test( user_pk )
    default_client.credentials( HTTP_AUTHORIZATION=str( token_test ) )

try:
    change_user()
except Exception as e:
    print( e )


def request_get_abs( url, filters=None, client=None, ):
    if client is None:
        client = default_client
    return client.get( url, filters )


def get_location( response, filters=None, client=None ):
    location = response[ 'location' ]
    return request_get_abs( location, filters, client )


def get_url_of_response( response ):
    return response.request[ 'PATH_INFO' ]


def get_link_header( response ):
    return link_header( response[ 'link' ] )


def assert_has_pages( response ):
    tc.assertTrue(
        response.has_header( 'link' ), 'should have links for the pages' )


def assert_has_next_page( response ):
    links = get_link_header( response )
    tc.assertIn(
        'next', links,
        "\nEl header link no tiene siguiente pagina\n{}".format( links ) )


def assert_has_prev_page( response ):
    links = get_link_header( response )
    tc.assertIn(
        'prev', links,
        "\nEl header link no tiene anterior pagina\n{}".format( links ) )


def assert_status_code( response, status_ok, print_headers=False ):
    try:
        response_data = response.data
    except AttributeError:
        response_data = madness.string.decode( response.content )
        response_data = json.loads( response_data )
    if print_headers:
        msg = ( "\nthe status code should be '{}' but is '{}'\n"
                "url: {}\n"
                "the data of the response is:\n{}"
                ).format( status_ok, response.status_code,
                          get_url_of_response( response ),
                          pformat( response_data ) )
    else:
        msg = ( "\nthe status code should be '{}' but is '{}'\n"
                "url: {}\n"
                "the data of the response is:\n{}"
                ).format( status_ok, response.status_code,
                          get_url_of_response( response ),
                          pformat( response_data ) )
    if is_iter( status_ok ):
        tc.assertIn( response.status_code, status_ok, msg )
    else:
        tc.assertEqual( response.status_code, status_ok, msg )


def assert_data( response, data, print_headers=False ):
    try:
        response_data = response.data
    except AttributeError:
        response_data = decode( response.content )
        response_data = json.loads( response_data )
    if print_headers:
        msg = (
            "\nthe data of the aswer is not the expected\n"
            "status code: {}\ndata:\n{}\n"
            "expected data:\n{}").format(
                response.status_code, pformat( response_data ),
                pformat( data ) )
    else:
        msg = (
            "\nthe data of the aswer is not the expected\n"
            "status code: {}\ndata:\n{}\n"
            "expected data:\n{}").format(
                response.status_code, pformat( response_data ),
                pformat( data ) )
    tc.assertEqual( response_data, data, msg )


def assert_data_subset( response, data, print_headers=False ):
    try:
        response_data = response.data
    except AttributeError:
        response_data = decode( response.content )
        response_data = json.loads( response_data )
    if print_headers:
        msg = (
            "\nthe data of the aswer is not the expected\n"
            "status code: {}\ndata:\n{}\n"
            "expected data:\n{}").format(
                response.status_code, pformat( response_data ),
                pformat( data ) )
    else:
        msg = (
            "\nthe data of the aswer is not the expected\n"
            "status code: {}\ndata:\n{}\n"
            "expected data:\n{}").format(
                response.status_code, pformat( response_data ),
                pformat( data ) )
    tc.assertDictContainsSubset( data, response_data, msg )
