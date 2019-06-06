# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['RegionSchemaTestCase::test_create 1'] = {
    'data': {
        'locations': {
            'params': {
                'city': 'Luxembourg City'
            }
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
    'id': '2',
    'key': 'luxembourg',
    'name': 'Luxembourg'
}

snapshots['RegionSchemaTestCase::test_update 1'] = {
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
                                49.4426671413,
                                5.67405195478
                            ],
                            [
                                50.1280516628,
                                5.67405195478
                            ],
                            [
                                50.1280516628,
                                6.24275109216
                            ],
                            [
                                49.4426671413,
                                6.24275109216
                            ],
                            [
                                49.4426671413,
                                5.67405195478
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
    'id': '6',
    'key': 'luxembourg',
    'name': 'Luxembourg'
}
