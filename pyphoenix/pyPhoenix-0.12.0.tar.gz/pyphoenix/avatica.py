# Copyright 2015 Lukas Lalinsky
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from future.standard_library import install_aliases
install_aliases()

from .requests_pb2 import *
from .common_pb2 import *
from .responses_pb2 import *
import urllib.parse
import logging
import socket
# import httplib
import http.client
from pyphoenix import errors
import math
import time
from importlib import import_module

__all__ = ['AvaticaClient']

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AVATICA_CLASS_BASE = "org.apache.calcite.avatica.proto"


def get_class(kls):
    """Get class given a fully qualified name of a class"""
    parts = kls.split('$')
    class_ = getattr(import_module("pyphoenix.responses_pb2"), parts[1])
    rv = class_()
    return rv


def parse_url(url):
    url = urllib.parse.urlparse(url)
    if not url.scheme and not url.netloc and url.path:
        netloc = url.path
        if ':' not in netloc:
            netloc = '{}:8765'.format(netloc)
        return urllib.parse.ParseResult('http', netloc, '/', '', '', '')
    return url


class AvaticaClient(object):
    """Client for Avatica's RPC server."""

    def __init__(self, url, max_retries=None, timeout=None, autocommit=None, readonly=None,):
        self.url = parse_url(url)
        self.max_retries = max_retries if max_retries is not None else 3
        self.connection = None
        self.autocommit = autocommit
        self.readonly = readonly
        self.timeout = timeout if timeout is not None else 100000

    def connect(self):
        """Opens a HTTP connection to the RPC server."""
        logger.debug("Opening connection to %s:%s", self.url.hostname, self.url.port)
        try:
            self.connection = http.client.HTTPConnection(self.url.hostname, self.url.port)
            self.connection.connect()
        except (http.client.HTTPException, socket.error) as e:
            raise errors.InterfaceError('Unable to connect to the specified service', e)

    def close(self):
        """Closes the HTTP connection to the RPC server."""
        if self.connection is not None:
            logger.debug("Closing connection to %s:%s", self.url.hostname, self.url.port)
            try:
                self.connection.close()
            except http.client.HTTPException:
                logger.warning("Error while closing connection", exc_info=True)
            self.connection = None

    def _apply(self,  request_data):

        wire_message = WireMessage()
        wire_message.name = AVATICA_CLASS_BASE + ".Requests$" + request_data.__class__.__name__
        wire_message.wrapped_message = request_data.SerializeToString()

        body = wire_message.SerializeToString()
        headers = {'content-type': 'application/x-google-protobuf'}
        response = self._post_request(body, headers)
        response_body = response.read()

        # deserialize WireMessage
        wire_message = WireMessage()
        wire_message.ParseFromString(response_body)

        # deserialize response
        response = get_class(wire_message.name)
        response.ParseFromString(wire_message.wrapped_message)

        if type(response) is ErrorResponse:
            raise errors.InterfaceError(response.error_message, code=response.error_code, sqlstate=response.sql_state,
                                        cause=response.exceptions)
        return response

    def _post_request(self, body, headers):
        retry_count = self.max_retries
        while True:
            logger.debug("POST %s %r %r", self.url.path, body, headers)
            try:
                self.connection.request('POST', self.url.path, body=body, headers=headers)
                response = self.connection.getresponse()
            except http.client.HTTPException as e:
                if retry_count > 0:
                    delay = math.exp(-retry_count)
                    logger.debug("HTTP protocol error, will retry in %s seconds...", delay, exc_info=True)
                    self.close()
                    self.connect()
                    time.sleep(delay)
                    retry_count -= 1
                    continue
                raise errors.InterfaceError('RPC request failed', cause=e)
            else:
                if response.status == http.client.SERVICE_UNAVAILABLE:
                    if retry_count > 0:
                        delay = math.exp(-retry_count)
                        logger.debug("Service unavailable, will retry in %s seconds...", delay, exc_info=True)
                        time.sleep(delay)
                        retry_count -= 1
                        continue
                return response

    def getCatalogs(self, connectionId):
        request = CatalogsRequest(connection_id=connectionId)
        response = self._apply(request)
        return response

    def openConnection(self, connectionId, info=None):
        request = OpenConnectionRequest(connection_id=connectionId)
        self._apply(request)

    def connectionSync(self, connectionId, conn_props=None):

        request = ConnectionSyncRequest(connection_id=connectionId, conn_props=conn_props)
        conn_props = self._apply(request).conn_props
        return conn_props

    def getSchemas(self, connectionId,  catalog=None, schemaPattern=None):
        request = SchemasRequest(connection_id=connectionId,
                                              catalog=catalog,
                                              schema_pattern=schemaPattern)
        response = self._apply(request)
        return response

    def getTables(self, connectionId, catalog=None, schemaPattern=None, tableNamePattern=None, typeList=None):
        request = TablesRequest(connection_id=connectionId,
                                             catalog=catalog,
                                             schema_pattern=schemaPattern,
                                             table_name_pattern=tableNamePattern,
                                             type_list=typeList)
        response = self._apply(request)
        return response

    def getColumns(self, connectionId, catalog=None, schemaPattern=None, tableNamePattern=None, columnNamePattern=None):
        request = ColumnsRequest(connection_id=connectionId,
                                              catalog=catalog,
                                             schema_pattern=schemaPattern,
                                             table_name_pattern=tableNamePattern,
                                              column_name_pattern=columnNamePattern)
        response = self._apply(request)
        return response

    def getTableTypes(self, connectionId):
        request = TableTypesRequest(connection_id=connectionId)
        return self._apply(request)

    def getTypeInfo(self, connectionId):
        request = TypeInfoRequest(connection_id=connectionId)
        return self._apply(request)

    def closeConnection(self, connectionId):
        request = CloseConnectionRequest(connection_id=connectionId)
        self._apply(request)

    def createStatement(self, connectionId):
        request = CreateStatementRequest(connection_id=connectionId)
        return self._apply(request).statement_id

    def closeStatement(self, connectionId, statementId):
        request = CloseStatementRequest(connection_id=connectionId)
        self._apply(request)

    def prepareAndExecute(self, connectionId, statementId, sql, maxRowCount=-1):
        request = PrepareAndExecuteRequest(connection_id=connectionId,
                                                        statement_id=statementId,
                                                        sql=sql,
                                                        max_rows_total=maxRowCount)
        return self._apply(request).results

    def prepare(self, connectionId, sql, maxRowCount=-1):
        request = PrepareRequest(connection_id=connectionId,
                                                        sql=sql,
                                                        max_rows_total=maxRowCount)
        return self._apply(request).statement

    def execute(self, connectionId, statementId, signature, parameterValues=None, maxRowCount=-1):
        statementHandle = StatementHandle(connection_id=connectionId, id=statementId, signature=signature)
        has_parameter_values = True
        if parameterValues is None or len(parameterValues) == 0:
            has_parameter_values = False

        request = ExecuteRequest(statementHandle=statementHandle,
                                 parameter_values=parameterValues,
                                 has_parameter_values=has_parameter_values,
                                 first_frame_max_size=maxRowCount)
        return self._apply(request).results

    def fetch(self, connectionId, statementId, offset=0, fetchMaxRowCount=-1):
        request = FetchRequest(connection_id=connectionId,
                                            statement_id=statementId,
                                            offset=offset,
                                            fetch_max_row_count=fetchMaxRowCount)

        return self._apply(request).frame

    def commitRequest(self, connectionId):
        request = CommitRequest(connection_id=connectionId)

        self._apply(request)

    def supportsExecute(self):
        return True
