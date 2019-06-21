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
# Copyright 2019 SerialLab Corp.  All rights reserved.
import traceback
import logging

from lxml import etree
from django.template import loader
from rest_framework.response import Response
from rest_framework import views
from rest_framework.negotiation import DefaultContentNegotiation
from rest_framework import status
from quartet_integrations.rocit.query import RocItQuery
from django.conf import settings

logger = logging.getLogger(__name__)

class DefaultXMLContent(DefaultContentNegotiation):

    def select_renderer(self, request, renderers, format_suffix):
        """
        Use the XML renderer as default.
        """
        # Allow URL style format override.  eg. "?format=json
        format_query_param = self.settings.URL_FORMAT_OVERRIDE
        format = format_suffix or request.query_params.get(format_query_param)
        request.query_params.get(format_query_param)
        header = request.META.get('HTTP_ACCEPT', '*/*')
        if format is None and header == '*/*':
            for renderer in renderers:
                if renderer.media_type == "application/xml":
                    return (renderer, renderer.media_type)
        return DefaultContentNegotiation.select_renderer(self, request,
                                                         renderers, format)


class RocItBaseView(views.APIView):
    """
    Base class for ROC IT Views.
    """
    permission_classes = []

    content_negotiation_class = DefaultXMLContent

    def get_tag_text(self, root, match_string):
        try:
            return root.find(match_string).text
        except:
            # All elements are optional just return none
            return None


class RetrievePackagingHierarchyView(RocItBaseView):
    """

    """

    def post(self, request):
        """

        :param request:
        :param format:
        :return:
        """
        try:
            if len(request.body) == 0:
                raise Exception('Request was empty')
            root = etree.fromstring(request.body)
            body = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
            query = body.find('{http://xmlns.oracle.com/oracle/apps/pas/serials/serialsService/applicationModule/common/types/}retrievePackagingHierarchy')
            row = query.find('{http://xmlns.oracle.com/oracle/apps/pas/serials/serialsService/applicationModule/common/types/}voRow')
            tag_id = self.get_tag_text(row,
                                       '{http://xmlns.oracle.com/oracle/apps/pas/serials/serialsService/view/common/}TagId')
            send_children = self.get_tag_text(row,
                                       '{http://xmlns.oracle.com/oracle/apps/pas/serials/serialsService/view/common/}SendChildren')
            send_product_info = self.get_tag_text(row,
                                       '{http://xmlns.oracle.com/oracle/apps/pas/serials/serialsService/view/common/}SendProductInformation')


            if tag_id is None:
               # Have to have the Tag Id
               raise Exception('Missing TagId in Request')
            data =  RocItQuery.RetrievePackagingHierarchy(tag_id, send_children, send_product_info)


            template = loader.get_template("rocit/rocit-search-response.xml")
            xml = template.render(data)

            ret_val = Response(xml, status.HTTP_200_OK, content_type="application/xml")

        except Exception:
            # Unexpected error, return HTTP 500 Server Error and log the exception
            data = traceback.format_exc()
            logger.error('Exception in qu4rtet_integrations.rocit.RetrievePackagingHierarchyView.post().\r\n%s' % data)
            ret_val = Response({"error": "A Server Error occurred servicing this request"},
                               status.HTTP_500_INTERNAL_SERVER_ERROR, content_type="application/xml")

        return ret_val




