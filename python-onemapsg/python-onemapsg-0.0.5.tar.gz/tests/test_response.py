# -*- coding: utf-8 -*-

import polyline

from onemapsg import status
from onemapsg.response import (
    BaseResource, GeocodeInfo, GeocodeInfoItem,
    Response, RouteResult, SearchResult, SearchResultItem
)


def test_response():
    """Should construct a Response instance with status_code and data."""
    response = Response(status.HTTP_200_OK, {'detail': 'example response.'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['detail'] == 'example response.'


def test_base_resource():
    """BaseResource instance should set any dictionary to attrs and
    to_dict should call to_dict utility helper."""
    class BaseClass(BaseResource):
        field1 = None
        field2 = None
    data = {'field1': 'a', 'field2': 'b'}
    base_resource = BaseClass(**data)
    assert base_resource.field1 == 'a'
    assert base_resource.field2 == 'b'
    assert base_resource.to_dict() == data


def test_search_result():
    """SearchResult should parse data properly into instance."""
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
                'LONGITUDE': '103.842158118267'
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
                'LONGITUDE': '103.842105076401'
            }
        ]
    }
    search_result = SearchResult(**data)
    assert search_result.found == 5
    assert search_result.total_num_pages == 1
    assert search_result.page_num == 1
    assert len(search_result.results) == 2
    for i, result in enumerate(search_result.results):
        assert isinstance(result, SearchResultItem)


def test_search_result_item():
    """SearchResultItem should parse data properly into instance."""
    data = {
        'SEARCHVAL': 'REVENUE HOUSE',
        'BLK_NO': '55',
        'ROAD_NAME': 'NEWTON ROAD',
        'BUILDING': 'REVENUE HOUSE',
        'ADDRESS': '55 NEWTON ROAD, SINGAPORE 307987',
        'POSTAL': '307987',
        'X': '28977.8507137401',
        'Y': '33547.5712691676',
        'LATITUDE': '1.31966682211667',
        'LONGITUDE': '103.842105076401'
    }
    result_item = SearchResultItem(**data)
    for k, v in data.items():
        if k == 'SEARCHVAL':
            assert result_item.search_value == data[k]
        elif k == 'X' or k == 'Y':
            assert result_item.coordinates == (data['X'], data['Y'])
        elif k == 'LATITUDE' or k == 'LONGITUDE':
            assert result_item.lat_long == (data['LATITUDE'], data['LONGITUDE'])
        else:
            assert getattr(result_item, k.lower()) == data[k]


def test_route_result():
    """RouteResult should parse data into instance."""
    
    # for routeType in ['walk', 'drive', 'cycle']
    data = {
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
        ],
        'debug_output': {
            'pathCalculationTime': 51,
            'pathTimes': [29, 16, 6],
            'precalculationTime': 87,
            'renderingTime': 1,
            'timedOut': False,
            'totalTime': 139
        },
        'elevation_metadata': {
            'ellipsoidToGeoidDifference': 7.473137315529,
            'geoidElevation': False
        },
        'plan': {
            'date': 1560468900000,
            'from': {
                'lat': 1.320981,
                'lon': 103.84415,
                'name': 'Origin',
                'orig': '',
                'vertexType': 'NORMAL'
            },
            'itineraries': [
                {
                    'duration': 1023,
                    'elevationGained': 0,
                    'elevationLost': 0,
                    'endTime': 1560470172000,
                    'fare': '0.83',
                    'legs': [
                        {
                            'agencyTimeZoneOffset': 28800000,
                            'arrivalDelay': 0,
                            'departureDelay': 0,
                            'distance': 441.086,
                            'duration': 396,
                            'endTime': 1560469545000,
                            'from': {
                                'departure': 1560469149000,
                                'lat': 1.320981,
                                'lon': 103.84415,
                                'name': 'Origin',
                                'orig': '',
                                'vertexType': 'NORMAL'
                            },
                            'interlineWithPreviousLeg': False,
                            'intermediateStops': [],
                            'legGeometry': {
                                'length': 49,
                                'points': 'i~`GsayxRCCPUMMMM@CFEHIPOBC@CA?@A\\Y@CnAmAHIBCDEDEDCDCJGFCJCFAHAFAD?FA`@Cl@GXCXCF?TCAGC[?EB?JCPA@A@A?AEa@UaAAMB?'
                            },
                            'mode': 'WALK',
                            'numIntermediateStops': 1,
                            'pathway': False,
                            'realTime': False,
                            'rentedBike': False,
                            'route': '',
                            'startTime': 1560469149000,
                            'steps': [
                                {
                                    'absoluteDirection': 'SOUTHEAST',
                                    'area': False,
                                    'bogusName': False,
                                    'distance': 441.086,
                                    'elevation': [],
                                    'lat': 1.3208561836374,
                                    'lon': 103.84426705983,
                                    'relativeDirection': 'DEPART',
                                    'stayOn': False,
                                    'streetName': 'path'
                                }
                            ],
                            'to': {
                                'arrival': 1560469545000,
                                'departure': 1560469546000,
                                'lat': 1.31875759946,
                                'lon': 103.846554541,
                                'name': 'REVIVAL CTR CH',
                                'stopId': 'FERRY:50111',
                                'stopIndex': 36,
                                'stopSequence': 38,
                                'vertexType': 'TRANSIT'
                            },
                            'transitLeg': False
                        }
                    ],
                    'startTime': 1560469149000,
                    'tooSloped': False,
                    'transfers': 0,
                    'transitTime': 538,
                    'waitingTime': 2,
                    'walkDistance': 545.83289472691,
                    'walkLimitExceeded': False,
                    'walkTime': 483
                }
            ],
            'to': {
                'lat': 1.326762,
                'lon': 103.8559,
                'name': 'Destination',
                'orig': '',
                'vertexType': 'NORMAL'
            }
        },
        'request_parameters': {
            'arriveBy': 'false',
            'date': '06-14-2019',
            'fromPlace': '1.320981,103.844150',
            'maxTransfers': '3',
            'maxWalkDistance': '1000',
            'mode': 'TRANSIT,WALK',
            'numItineraries': '3',
            'otherThanPreferredRoutesPenalty': '0',
            'preferredRoutes': '1__CC,1__DT,1__EW,1__NE,1__NS,1__PE,1__PW,1__SE,1__SS,1__SW,1__CG,1__BP',
            'showIntermediateStops': 'true',
            'time': '7:35am',
            'toPlace': '1.326762,103.8559',
            'transferPenalty': '7200',
            'waitAtBeginningFactor': '0.5',
            'walkReluctance': '2'
        }
    }
    route_result = RouteResult(**data)
    attrs = [x for x in dir(route_result) if not x.startswith('__')]
    for attr in attrs:
        if attr != 'lat_longs' and attr != 'to_dict':
            assert getattr(route_result, attr) == data[attr]
    assert route_result.lat_longs == polyline.decode(route_result.route_geometry)
    route_result.route_geometry = None
    assert route_result.lat_longs is None


def test_geocode_info_item():
    """GeocodeInfoItem should parse data into instance."""
    data = {
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
    geocode_info_item = GeocodeInfoItem(**data)
    assert geocode_info_item.block == data['BLOCK']
    assert geocode_info_item.building_name == data['BUILDINGNAME']
    assert geocode_info_item.coordinates == (data['XCOORD'], data['YCOORD'])
    assert geocode_info_item.lat_long == (data['LATITUDE'], data['LONGITUDE'])


def test_geocode_info():
    """GeocodeInfo should parse data into instance."""
    data = {
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
    geocode_info = GeocodeInfo(**data)
    assert len(geocode_info.results) == 1
    assert isinstance(geocode_info.results[0], GeocodeInfoItem)
