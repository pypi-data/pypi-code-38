"""Default settings for the Split.IO SDK Python client."""
from __future__ import absolute_import, division, print_function, unicode_literals
import os.path

DEFAULT_CONFIG = {
    'connectionTimeout': 1500,
    'splitSdkMachineName': None,
    'splitSdkMachineIp': None,
    'featuresRefreshRate': 5,
    'segmentsRefreshRate': 60,
    'metricsRefreshRate': 60,
    'impressionsRefreshRate': 10,
    'impressionsBulkSize': 5000,
    'impressionsQueueSize': 10000,
    'eventsPushRate': 10,
    'eventsBulkSize': 5000,
    'eventsQueueSize': 10000,
    'labelsEnabled': True,
    'impressionListener': None,
    'redisHost': 'localhost',
    'redisPort': 6379,
    'redisDb': 0,
    'redisPassword': None,
    'redisSocketTimeout': None,
    'redisSocketConnectTimeout': None,
    'redisSocketKeepalive': None,
    'redisSocketKeepaliveOptions': None,
    'redisConnectionPool': None,
    'redisUnixSocketPath': None,
    'redisEncoding': 'utf-8',
    'redisEncodingErrors': 'strict',
    'redisCharset': None,
    'redisErrors': None,
    'redisDecodeResponses': False,
    'redisRetryOnTimeout': False,
    'redisSsl': False,
    'redisSslKeyfile': None,
    'redisSslCertfile': None,
    'redisSslCertReqs': None,
    'redisSslCaCerts': None,
    'redisMaxConnections': None,
    'machineName': None,
    'machineIp': None,
    'splitFile': os.path.join(os.path.expanduser('~'), '.split')
}
