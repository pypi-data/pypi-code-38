from __future__ import absolute_import
import os
import shutil

import pytest
import dockerdb.influxdb


CONTAINER_CACHE = {}


class PyTestFixtureHelper:
    service_cls = dockerdb.influxdb.InfluxDB

    def __init__(self):
        self.containers = []
        self.in_use = []
    
    def find_container(self, version):
        pass

    def get_service(version):
        service = CONTAINER_CACHE[version]
        service.wait()
        service.factory_reset()
        return service

    def fixture(self, scope='function', versions=['latest'], reuse=False, exposed_port=27017):
        """create ficture for py.test

        Attributes:
            scope (str): py.test scope for this fixture
            versions (list): mongodb versions that should be tested
            
        """

        # parallelized start of different versions
        if reuse:
            for version in versions:
                ensure_service(version, port)

        @pytest.fixture(scope=scope, params=versions)
        def influxdb(request):
            if reuse:
                service = get_service(request.param)
            else:
                service = self.service_cls(request.param, wait=True,
                                        exposed_port=exposed_port)
            
            service.wait()

            # if data:
            #     insert_data(client, data)

            # if restore:
            #     mongorestore(service, restore)

            yield service

            if not reuse:
                service.remove()

        return influxdb


instance = PyTestFixtureHelper()
fixture = instance.fixture
