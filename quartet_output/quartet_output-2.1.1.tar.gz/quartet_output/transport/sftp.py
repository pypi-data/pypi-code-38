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
import paramiko
from urllib.parse import urlparse
from os.path import join
from quartet_capture import models
from io import StringIO, BytesIO
from logging import getLogger
from quartet_output.models import EndPoint, EPCISOutputCriteria
from quartet_capture.rules import Step, RuleContext

logger = getLogger(__name__)


class SftpTransportMixin:
    '''
    Add to steps that need to support sending over files via SFTP.
    '''

    def sftp_put(self, data, rule_context: RuleContext,
                  output_criteria: EPCISOutputCriteria,
                  content_type='application/xml',
                  file_extension='xml'):
        '''
        :param data: Data passed as bytes.
        :param output_criteria: The output criteria containing the connection
        info.
        :return: The response.
        '''
        logger.debug('Using context key %s to PUT data over SFTP.', data)
        data_stream = BytesIO(data)
        file_name = '{0}.{1}'.format(rule_context.task_name, file_extension)
        files = {'file': (file_name, data_stream)}
        logger.debug('Posting data with urn %s and file_name %s and '
                     'extension %s.',
                     output_criteria.end_point.urn,
                     file_name,
                     file_extension)
        parsed_urn = urlparse(output_criteria.end_point.urn)
        sftp_client = None
        result = None
        try:
            sftp_client = paramiko.SSHClient()
            sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            auth = self.sftp_get_auth(output_criteria)
            remote_path = join(parsed_urn.path, file_name)
            sftp_client.connect(parsed_urn.hostname, parsed_urn.port, **auth, timeout=60)
            sftp = sftp_client.open_sftp()
            result = sftp.putfo(data_stream, remote_path, confirm=False)
        finally:
            if sftp_client:
                sftp_client.close()
        return result

    def sftp_get_auth(self, output_criteria):
        auth_info = output_criteria.authentication_info
        if auth_info:
            auth_type = auth_info.type or ''
            if auth_info.private_key:
                key_file = StringIO.StringIO(auth_info.private_key)
                return {"username": auth_info.username,
                        "pkey": paramiko.RSAKey.from_private_key(key_file)}
            else:
                return {"username": auth_info.username,
                        "password": auth_info.password}
        return None
