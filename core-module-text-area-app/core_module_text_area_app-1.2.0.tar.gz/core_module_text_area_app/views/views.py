""" Text Area module
"""
import re
from django.template import loader
from core_module_text_area_app.settings import AUTO_ESCAPE_XML_ENTITIES
from core_parser_app.tools.modules.views.builtin.textarea_module import AbstractTextAreaModule
from xml_utils.xsd_tree.operations.xml_entities import XmlEntities


class TextAreaModule(AbstractTextAreaModule):

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        data = ''
        self.data_xml_entities = XmlEntities()

        if request.method == 'GET':
            if 'data' in request.GET:
                data = request.GET['data']
        elif request.method == 'POST':
            if 'data' in request.POST:
                data = request.POST['data']

        data = self.data_xml_entities.escape_xml_entities(data) if AUTO_ESCAPE_XML_ENTITIES else data

        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        # search the XML predefined entities, to display warning if it needed / we add pre escaped search too
        if self.data_xml_entities.number_of_subs_made > 0 or len(re.findall(r'((&amp;)|(&gt;)|(&lt;)|(&apos;)|(&quot;))', self.data)) > 0:
            return loader.get_template('core_module_text_area_app/predefined_entities_warning.html').template.source
        else:
            return ''
