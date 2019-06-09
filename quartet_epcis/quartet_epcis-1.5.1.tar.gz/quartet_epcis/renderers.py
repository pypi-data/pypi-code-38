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

from rest_framework_xml.renderers import XMLRenderer
from rest_framework.renderers import JSONRenderer

class EPCPyYesXMLRenderer(XMLRenderer):
    '''
    Overrrides the basic XMLRenderer and uses the
    `EPCPyYes.core.v1_2.template_events` Event class's .render() output
    directly since that output is already encoded into XML.
    '''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, str):
            ret = data.encode(self.charset)
        else:
            ret = super().render(data, accepted_media_type, renderer_context)
        return ret

