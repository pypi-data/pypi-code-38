# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
from quartet_capture import models
from io import StringIO
from logging import getLogger
import requests
from requests.auth import HTTPBasicAuth, HTTPDigestAuth, HTTPProxyAuth
from quartet_output.models import EndPoint, EPCISOutputCriteria
from quartet_capture.rules import Step, RuleContext
from quartet_output import __version__
logger = getLogger(__name__)

user_agent = 'quartet-output/{0}'.format(
    __version__
)

class HttpTransportMixin:
    '''
    Add to steps that need to support sending http messages.
    '''

    def post_data(self, data: str, rule_context: RuleContext,
                  output_criteria: EPCISOutputCriteria,
                  content_type='application/xml',
                  file_extension='xml',
                  http_put=False,
                  body_raw=True):
        '''
        :param data_context_key: The key within the rule_context that contains
         the data to post.  If being invoked from the internals of this
         module this is usually the OUTBOUND_EPCIS_MESSSAGE_KEY value of the
         `quartet_output.steps.ContextKeys` Enum.
        :param output_criteria: The output criteria containing the connection
        info.
        :param body_raw: Whether or not the data should be sent as raw body. Defaults to True.
        :return: The response.
        '''
        data_stream = data
        file_name = '{0}.{1}'.format(rule_context.task_name, file_extension)
        logger.debug('Posting data with urn %s and file_name %s and '
                     'extension %s.',
                     output_criteria.end_point.urn,
                     file_name,
                     file_extension)
        if not http_put:
            func = requests.post
            if body_raw:
                files = data_stream
            else:
                files = {'file': data_stream}
        else:
            func = requests.put
            file_name = '{0}.{1}'.format(rule_context.task_name,
                                         file_extension)
            if body_raw:
                files = data_stream
            else:
                files = {'file': (file_name, data_stream)}
        response = func(
            output_criteria.end_point.urn,
            files,
            auth=self.get_auth(output_criteria),
            headers={'content-type': content_type, 'user-agent': user_agent}
        )
        return response

    def put_data(self, data: str, rule_context: RuleContext,
                 output_criteria: EPCISOutputCriteria,
                 content_type='application/xml',
                 file_exension='xml',
                 body_raw=True):
        '''
        :param data: The data to PUT.
        :param output_criteria: The output criteria containing the connection
        info.
        :param body_raw: Whether or not the data should be sent as raw body. Defaults to True.
        :return: The response.
        '''
        return self.post_data(data, rule_context, output_criteria,
                              content_type, file_exension, http_put=True, body_raw=body_raw)

    def get_auth(self, output_criteria):
        """
        Get's the authentication method and credentials from the
        EPCISOutputCriteria record.
        :param output_criteria: An EPCISOutputCriteria model instance.
        :return: A `requests.auth.HTTPBasicAuth` or `HTTPProxyAuth`
        """
        auth_info = output_criteria.authentication_info
        auth = None
        if auth_info:
            auth_type = auth_info.type or ''
            if 'digest' in auth_type.lower():
                auth = HTTPBasicAuth
            elif 'proxy' in auth_type.lower():
                auth = HTTPProxyAuth
            else:
                auth = HTTPBasicAuth
            auth = auth(auth_info.username, auth_info.password)
        return auth
