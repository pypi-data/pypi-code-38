# -*- coding: utf-8 -*-

from unittest.mock import MagicMock, patch

import pytest

from onemapsg import exceptions, response, status
from onemapsg.client import OneMap


@patch('onemapsg.client.make_request')
def test_client_connect(mock_request):
    """Client should return a OneMap instance with token and
    token_expiry set."""
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        data={
            'access_token': 'sometoken',
            'expiry_timestamp': '123456'
        }
    )
    onemap = OneMap('email@example.com', 'password')
    assert onemap.token == 'sometoken'
    assert onemap.token_expiry == '123456'


@patch('onemapsg.client.make_request')
def test_client_connect_error_bad_request(mock_request):
    """Any client errors during authentication should return
    AuthenticationError."""
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_400_BAD_REQUEST
    )
    with pytest.raises(exceptions.AuthenticationError) as err:
        OneMap('email@example.com', 'password')
        assert str(err) == 'Failed to authenticate.'


@patch('onemapsg.client.make_request')
def test_client_connect_error_server_error(mock_request):
    """Any server errors during authentication should return ServerError."""
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    with pytest.raises(exceptions.ServerError) as err:
        OneMap('email@example.com', 'password')
        assert str(err) == 'OneMap SG server error. Please try again later.'


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_client_search(mock_request, mock_connect):
    """Should return SearchResult instance as response."""
    mock_connect.return_value = None, None
    data = {
        'found': 5,
        'totalNumPages': 1,
        'pageNum': 1,
        'results': [
            {
                'SEARCHVAL': 'INLAND REVENUE AUTHORITY OF SINGAPORE (IRAS)',
                'BLK_NO': '55',
                'ROAD_NAME': 'NEWTON ROAD',
                'BUILDING': 'INLAND REVENUE AUTHORITY OF SINGAPORE (IRAS)',
                'ADDRESS': '55 NEWTON ROAD, SINGAPORE 307987',
                'POSTAL': '307987',
                'X': '28983.7537272647',
                'Y': '33554.4361084122',
                'LATITUDE': '1.31972890510723',
                'LONGITUDE': '103.842158118267',
                'LONGTITUDE': '103.842158118267'
            },
            {
                'SEARCHVAL': 'REVENUE HOUSE',
                'BLK_NO': '55',
                'ROAD_NAME': 'NEWTON ROAD',
                'BUILDING': 'REVENUE HOUSE',
                'ADDRESS': '55 NEWTON ROAD, SINGAPORE 307987',
                'POSTAL': '307987',
                'X': '28977.8507137401',
                'Y': '33547.5712691676',
                'LATITUDE': '1.31966682211667',
                'LONGITUDE': '103.842105076401',
                'LONGTITUDE': '103.842105076401'
            }
        ]
    }
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        data=data
    )
    search_result = OneMap('email@example.com', 'password').search('307987')
    assert isinstance(search_result, response.SearchResult)


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_client_search_bad_request(mock_request, mock_connect):
    mock_connect.return_value = None, None
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_400_BAD_REQUEST,
        data={'error': 'some client error'}
    )
    with pytest.raises(exceptions.BadRequest) as err:
        OneMap('email@example.com', 'password').search('307987')
        assert str(err) == 'some client error'

    mock_request.return_value = MagicMock(
        status_code=status.HTTP_400_BAD_REQUEST,
    )
    with pytest.raises(exceptions.BadRequest) as err:
        OneMap('email@example.com', 'password').search('307987')
        assert str(err) == 'Please ensure request is correct.'


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_client_search_server_error(mock_request, mock_connect):
    mock_connect.return_value = None, None
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    with pytest.raises(exceptions.ServerError) as err:
        OneMap('email@example.com', 'password').search('307987')
        assert str(err) == 'OneMap SG server error. Please try again later.'


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_client_route(mock_request, mock_connect):
    """Should return RouteResult instance."""
    mock_connect.return_value = None, None
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        data={
            'status_message': 'Found route between points',
            'alternative_names': [
                [
                    'COMMONWEALTH AVENUE WEST',
                    'NORTH BUONA VISTA ROAD'
                ]
            ],
            'route_name': [
                'CLEMENTI AVENUE 2',
                'ULU PANDAN ROAD'
            ],
            'route_geometry': (
                'yr`oAm`k{dEksAstD~e@iW`e@{UxtAqr@pd@sVrOmItC}GZ}GJwDeSmWkm@gb@qKuEyCwE}AgHJiH\\'
                'kE{BaRoCoEsGcLiE{N{AmQvB{QbFkN|E}FzMcPtQmTh|A_iBfCcDzHcKpJaMr\\w_@t\\i`@hb@gg@lA'
                'kJRqJg@wJeCoMgQ{f@qHsTuC_FiMsT_S_ViVkPkfAyi@oXiNq{@q_@qn@cU{SsGgEqAiDeAcTsGcd@eM'
                'oF{AoBi@uGkB}d@uMwDoA_EsA{QiG_VyJaSkLkQuN}CgDqJkKqDsFqE_H}CuE}CyEsBsGcDeKuK}f@}'
                'FiJ_FaEkKiEgHcAe~@xMsr@`LqMrB_En@gAy`@kBkVwE{W_^gbAkHg[aFeQaRe^_Nea@iEw'
                'YJkYsAyj@KiRkGglAcDqn@KiUrDkc@nFkY`Lo]lIeQfJgOfcAyhAzJ}KtPsTjIuQxFaQrBcN'
                '|E{u@rDgh@hBuYjDy_@zHoUbI}O|PwSkDuBiP_K{]cTq_Ack@ixAe|@_L}G{LoHynBujAsh@iZi'
                'RqK}|@ig@xg@wo@v{@_gA~q@g}@fUgZp^{`@gDqLv`@oNfTwH~LcIl@gEy@{PqU_V_`@cuAvHw'
                'Jt^_MvXgMxCaD'),
            'route_instructions': [
                [
                    '10',
                    'PANDAN LOOP',
                    853,
                    0,
                    89,
                    '853m',
                    'NE',
                    65,
                    1,
                    'SW',
                    245
                ]
            ],
            'alternative_summaries': [
                {
                    'end_point': 'REBECCA ROAD',
                    'start_point': 'PANDAN LOOP',
                    'total_time': 761,
                    'total_distance': 8133
                }
            ],
            'via_points': [
                [
                    1.311549,
                    103.749657
                ],
                [
                    1.32036,
                    103.800156
                ]
            ],
            'route_summary': {
                'end_point': 'REBECCA ROAD',
                'start_point': 'PANDAN LOOP',
                'total_time': 740,
                'total_distance': 7957
            },
            'found_alternative': True,
            'status': 200,
            'via_indices': [
                0,
                140
            ],
            'hint_data': {
                'locations': [
                    'NzgBANtqAQBRBQAAAAAAAAQAAAAAAAAAuQIAAEOcAABoAAAAPQMUABcYLwYAAAEB',
                    '0OUAAF4zAQChAwAABAAAAAwAAABIAAAAdQAAACx9AABoAAAAqCUUAFndLwYCAAEB'
                ],
                'checksum': 585417468
            },
            'alternative_geometries': [(
                'yr`oAm`k{dEksAstD~e@iW`e@{UxtAqr@pd@sVrOmItC}GZ}GJwDeSmWkm@gb@qKuEyCwE}Ag'
                'HJiH\\kE{BaRoCoEsGcLiE{N{AmQvB{QbFkN|E}FzMcPtQmTh|A_iBfCcDzHcKpJaMr\\w_@'
                't\\i`@hb@gg@lAkJRqJg@wJeCoMgQ{f@qHsTuC_FiMsT_S_ViVkPkfAyi@oXiNq{@q_@qn@cU'
                '{SsGgEqA~@wEzCgOvBiLzAqM\\mG@ad@UoQmC{^eDms@e@uJoAsXgAg^MgEe@sEuD__@qLstB}'
                '@ePIsCmAiq@zA_YjG_b@nB_HpHeWdK}UdkBqqD~A{CnAcCjA{BpIoPhAyBf_@gs@rb@uz@vC'
                '{F`CcFf`@sv@bEeMvGgVzEoQ~AyRrAyRe@mQ_E_XyDuWsJo}@gJsgAwByYcAmN?eDJ}Bh@cPn'
                'DuRtKs]~Ig[g_@oGg[aJqDY{FGkOdAqH`B{VrFok@bMsIlAcJNcJm@sImB{HiDej@ig@yDmD'
                '_CyB}v@qt@_TkQpf@yv@r_@kh@lF{MlDqM`AwN[cN}BqP{Uii@iI~DsFb@ih@cPeQaPaJ_NsI'
                'wEmV}KyMiBmKg@ae@}HkP}RgDoHwCwNkFWaY{E{Hj]uDjJcJhKia@n_@qFpL}g@uHcd@tLoBm'
                '[}GmJe`@eZub@qh@uHsa@_MuMsSiOvXgMxCaD'
            )],
            'alternative_instructions': [
                [
                    [
                        '10',
                        'PANDAN LOOP',
                        853,
                        0,
                        89,
                        '853m',
                        'NE',
                        65,
                        1,
                        'SW',
                        245
                    ],
                    [
                        '8',
                        'JALAN BUROH',
                        217,
                        9,
                        23,
                        '217m',
                        'NE',
                        50,
                        1,
                        'SW',
                        230
                    ],
                    [
                        '1',
                        'WEST COAST HIGHWAY',
                        62,
                        14,
                        7,
                        '61m',
                        'E',
                        92,
                        1,
                        'W',
                        272
                    ]
                ]
            ],
            'alternative_indices': [
                0,
                159
            ]
        }
    )
    route_result = OneMap('email@example.com', 'password').route(
        '1.23,1.01',
        '1.01,1.23',
        'drive'
    )
    assert isinstance(route_result, response.RouteResult)


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_reverse_geocode_svy21(mock_request, mock_connect):
    """Should return GeocodeInfo instance."""
    mock_connect.return_value = None, None
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        data={
            "GeocodeInfo": [
                {
                    "BUILDINGNAME": "NEW TOWN PRIMARY SCHOOL",
                    "BLOCK": "300",
                    "ROAD": "TANGLIN HALT ROAD",
                    "POSTALCODE": "148812",
                    "XCOORD": "24303.327416",
                    "YCOORD": "31333.331116",
                    "LATITUDE": "1.2996418106402365",
                    "LONGITUDE": "103.80011086725216",
                    "LONGTITUDE": "103.80011086725216"
                }
            ]
        }
    )
    geocode_info = OneMap('email@example.com', 'password').reverse_geocode(
        'svy21',
        (24291.97788882387, 31373.0117224489)
    )
    assert isinstance(geocode_info, response.GeocodeInfo)


@patch('onemapsg.client.OneMap._connect')
@patch('onemapsg.client.make_request')
def test_reverse_geocode_wsg84(mock_request, mock_connect):
    """Should return GeocodeInfo instance."""
    mock_connect.return_value = None, None
    mock_request.return_value = MagicMock(
        status_code=status.HTTP_200_OK,
        data={
            "GeocodeInfo": [
                {
                    "BUILDINGNAME": "NEW TOWN PRIMARY SCHOOL",
                    "BLOCK": "300",
                    "ROAD": "TANGLIN HALT ROAD",
                    "POSTALCODE": "148812",
                    "XCOORD": "24303.327416",
                    "YCOORD": "31333.331116",
                    "LATITUDE": "1.2996418106402365",
                    "LONGITUDE": "103.80011086725216",
                    "LONGTITUDE": "103.80011086725216"
                }
            ]
        }
    )
    geocode_info = OneMap('email@example.com', 'password').reverse_geocode(
        'wgs84',
        (1.3, 103.8)
    )
    assert isinstance(geocode_info, response.GeocodeInfo)
