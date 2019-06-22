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

from EPCPyYes.core.SBDH import sbdh
from EPCPyYes.core.v1_2.template_events import TemplateMixin
from EPCPyYes.core.v1_2 import json_encoders


class StandardBusinessDocumentHeader(sbdh.StandardBusinessDocumentHeader,
                                     TemplateMixin):
    '''
    The SBDH header as defined in the GS1 protocol.
    '''

    def __init__(
            self,
            namespace: str = 'sbdh',
            schema_location: str = ('http://www.unece.org/cefact/'
                                    'namespaces/'
                                    'StandardBusinessDocumentHeader'),
            document_identification: sbdh.DocumentIdentification = None,
            partners: sbdh.PartnerList = None,
            header_version: str = '1.0'
    ):
        super().__init__(namespace, schema_location, document_identification,
                         partners, header_version)
        TemplateMixin.__init__(self)
        self.template = 'epcis/sbdh.xml'
        self.encoder = json_encoders.StandardBusinessDocumentHeaderEncoder()

    def render(self):
        self._context = {"header": self}
        return super().render()
