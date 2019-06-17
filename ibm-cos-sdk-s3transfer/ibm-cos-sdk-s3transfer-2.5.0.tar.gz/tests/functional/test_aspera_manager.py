# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License'). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the 'license' file accompanying this file. This file is
# distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from tests import StubbedClientTest

from ibm_s3transfer.aspera.manager import AsperaTransferManager
from ibm_s3transfer.aspera.manager import AsperaManagerConfig
from ibm_s3transfer.aspera.manager import AsperaConfig

class TestAsperaTransferManager(StubbedClientTest):

    def verify_cache_info(self, cache_info, hits, misses, current_size):
        self.assertEqual(cache_info.hits, hits)
        self.assertEqual(cache_info.misses, misses)
        self.assertEqual(cache_info.currsize, current_size)

    def test_get_object_metadata_response(self):
        # The purpose of this test is to validate the basic call
        # and parsing client response for the _get_aspera_metadata

        access_key = 'aspera-access-key-id'
        secret_key = 'aspera-secret-key'
        ats_endpoint = 'aspera-ats-endpoint'

        self.stubber.add_response('get_bucket_aspera', {'AccessKey': {'Id': access_key,
                                                                      'Secret': secret_key},
                                                        'ATSEndpoint': ats_endpoint
                                                        })

        manager = AsperaTransferManager(self.client)
        response = manager._get_aspera_metadata('foo')

        self.assertEqual(response[0], access_key)
        self.assertEqual(response[1], secret_key)
        self.assertEqual(response[2], ats_endpoint)

    def test_default_max_cache_size(self):
        # The purpose of this test is to validate the default max cache size.
        manager = AsperaTransferManager(self.client)
        max_cache_size = manager._config.max_fasp_cache_size

        access_key = 'aspera-access-key-id'
        secret_key = 'aspera-secret-key'
        ats_endpoint = 'aspera-ats-endpoint'

        # Build stubbed responses
        for i in range(0, max_cache_size):
            self.stubber.add_response('get_bucket_aspera', {'AccessKey': {'Id': access_key + str(i),
                                                                          'Secret': secret_key + str(i)},
                                                            'ATSEndpoint': ats_endpoint + str(i)
                                                            })

            # Load cache
            manager._get_aspera_metadata('foo' + str(i))

        self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                               hits=0,
                               misses=max_cache_size,
                               current_size=max_cache_size)

        # Validate contents in cache
        for i in range(0, max_cache_size):
            response = manager._get_aspera_metadata('foo' + str(i))

            self.assertEqual(response[0], access_key + str(i))
            self.assertEqual(response[1], secret_key + str(i))
            self.assertEqual(response[2], ats_endpoint + str(i))

        self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                               hits=max_cache_size,
                               misses=max_cache_size,
                               current_size=max_cache_size)

    def test_lru_cache_eviction(self):
        # The purpose of this test is to validate the cache is
        # bounded by the max_fasp_cache_size, and that the cache
        # size is configurable via AsperaManagerConfig
        aspera_transfer_configs = [None,
                                   AsperaManagerConfig(max_fasp_cache_size=10),
                                   AsperaManagerConfig(max_fasp_cache_size=100)]

        for aspera_transfer_config in aspera_transfer_configs:
            manager = AsperaTransferManager(self.client, config=aspera_transfer_config)
            max_cache_size = manager._config.max_fasp_cache_size

            access_key = 'aspera-access-key-id'
            secret_key = 'aspera-secret-key'
            ats_endpoint = 'aspera-ats-endpoint'

            # Build stubbed responses
            for i in range(0, max_cache_size + 2):
                self.stubber.add_response('get_bucket_aspera', {'AccessKey': {'Id': access_key + str(i),
                                                                              'Secret': secret_key + str(i)},
                                                                'ATSEndpoint': ats_endpoint + str(i)
                                                                })

            for i in range(0, max_cache_size):
                # Fill cache, max cache is reached
                manager._get_aspera_metadata('foo' + str(i))

            self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                                   hits=0,
                                   misses=max_cache_size,
                                   current_size=max_cache_size)

            # Perform 1 more request that doesn't hit the cache,
            # this will replace the first entry (foo0)
            manager._get_aspera_metadata('newbucket')
            self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                                   hits=0,
                                   misses=max_cache_size + 1,
                                   current_size=max_cache_size)

            # Get aspera metadata for foo0 after its been removed
            # from cache, this will replace foo1
            response = manager._get_aspera_metadata('foo0')
            self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                                   hits=0,
                                   misses=max_cache_size + 2,
                                   current_size=max_cache_size)

            # Metadata is now different than what it was before
            self.assertNotEqual(response[0], access_key + str(0))
            self.assertNotEqual(response[1], secret_key + str(0))
            self.assertNotEqual(response[2], ats_endpoint + str(0))

            # All other cache entries still remain
            for i in range(2, max_cache_size):
                response = manager._get_aspera_metadata('foo' + str(i))
                self.assertEqual(response[0], access_key + str(i))
                self.assertEqual(response[1], secret_key + str(i))
                self.assertEqual(response[2], ats_endpoint + str(i))

            self.verify_cache_info(manager._get_aspera_metadata.cache_info(),
                                   hits=max_cache_size - 2,
                                   misses=max_cache_size + 2,
                                   current_size=max_cache_size)
