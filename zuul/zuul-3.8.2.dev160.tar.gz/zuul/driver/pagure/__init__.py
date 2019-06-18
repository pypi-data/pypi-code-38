# Copyright 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from zuul.driver import Driver, ConnectionInterface, TriggerInterface
from zuul.driver import SourceInterface, ReporterInterface
from zuul.driver.pagure import pagureconnection
from zuul.driver.pagure import paguresource
from zuul.driver.pagure import pagurereporter
from zuul.driver.pagure import paguretrigger


class PagureDriver(Driver, ConnectionInterface, TriggerInterface,
                   SourceInterface, ReporterInterface):
    name = 'pagure'

    def getConnection(self, name, config):
        return pagureconnection.PagureConnection(self, name, config)

    def getTrigger(self, connection, config=None):
        return paguretrigger.PagureTrigger(self, connection, config)

    def getSource(self, connection):
        return paguresource.PagureSource(self, connection)

    def getReporter(self, connection, pipeline, config=None):
        return pagurereporter.PagureReporter(
            self, connection, pipeline, config)

    def getTriggerSchema(self):
        return paguretrigger.getSchema()

    def getReporterSchema(self):
        return pagurereporter.getSchema()

    def getRequireSchema(self):
        return paguresource.getRequireSchema()

    def getRejectSchema(self):
        return paguresource.getRejectSchema()
