# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['UserStateSchemaTestCase::test_create 1'] = {
    'data': {
        'createUserState': {
            'userState': {
                'data': {
                    'userRegions': [
                        {
                            'mapbox': {
                                'viewport': {
                                    'latitude': 50.5915,
                                    'longitude': 2.0165,
                                    'zoom': 7
                                }
                            },
                            'region': {
                                'data': {
                                    'locations': {
                                    }
                                },
                                'geojson': {
                                    'features': [
                                        {
                                            'geometry': {
                                                'coordinates': [
                                                    [
                                                        [
                                                            49.5294835476,
                                                            2.51357303225
                                                        ],
                                                        [
                                                            51.4750237087,
                                                            2.51357303225
                                                        ],
                                                        [
                                                            51.4750237087,
                                                            6.15665815596
                                                        ],
                                                        [
                                                            49.5294835476,
                                                            6.15665815596
                                                        ],
                                                        [
                                                            49.5294835476,
                                                            2.51357303225
                                                        ]
                                                    ]
                                                ],
                                                'type': 'Polygon'
                                            },
                                            'type': 'Feature'
                                        }
                                    ],
                                    'type': 'FeatureCollection'
                                },
                                'key': 'belgium',
                                'name': 'Belgium'
                            }
                        }
                    ]
                },
                'user': {
                    'firstName': 'Upa',
                    'isActive': True,
                    'lastName': 'Tree',
                    'username': 'margay'
                }
            }
        }
    }
}
