# -*- coding: utf-8 -*-

"""API configuration parameters
"""

# Default URI
URI = 'http://driftsdata.statnett.no/restapi'

# topics
# name: topic's name
# endpoint: default endpoint
# date_var: name of json timestamp field
# headers: name of json field with headers
# records: list of json record fields
topics = {
    'flow': {
        'name': 'flow',
        'endpoint': 'PhysicalFlowMap/GetFlow',
        'date_var': 'MeasureDate'
    },
    'balance': {
        'name': 'balance',
        'endpoint': 'ProductionConsumption/GetLatestDetailedOverview',
        'date_var': 'MeasuredAt',
        'headers': 'Headers',
        'records': ['ProductionData', 'NuclearData', 'HydroData', 'ThermalData',
                    'WindData', 'NotSpecifiedData', 'ConsumptionData', 'NetExchangeData']
    },
    'frequency': {
        'name': 'frequency',
        'endpoint': 'Frequency/ByMinute',
        'record': 'Measurements',
        'date_start': 'StartPointUTC',
        'date_end': 'EndPointUTC'
    }
}
