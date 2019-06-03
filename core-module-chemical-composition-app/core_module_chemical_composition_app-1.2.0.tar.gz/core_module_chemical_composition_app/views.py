""" Chemical composition module view
"""
import json

from xml_utils.xsd_tree.operations.xml_entities import XmlEntities
from core_module_chemical_composition_app.settings import AUTO_ESCAPE_XML_ENTITIES
from core_module_chemical_composition_app.api import render_chemical_composition, get_chemical_composition_popup_content
from core_parser_app.tools.modules.views.builtin.popup_module import AbstractPopupModule


class ChemicalCompositionModule(AbstractPopupModule):
    def __init__(self):
        AbstractPopupModule.__init__(self, button_label='Select Elements',
                                     styles=['core_module_periodic_table_app/css/periodic.css',
                                             'core_module_chemical_composition_app/css/'
                                             'chemical_element_composition.css'],
                                     scripts=['core_module_chemical_composition_app/js/events.js',
                                              'core_module_chemical_composition_app/js/'
                                              'chemical_element_composition.js'])

    def _retrieve_data(self, request):
        """ Retrieve module's data

        Args:
            request:

        Returns:

        """
        data = ''
        if request.method == 'GET':
            if 'data' in request.GET:
                data = request.GET['data']
        elif request.method == 'POST':
            if 'elementList' in request.POST:
                element_list = json.loads(request.POST['elementList'])
                if len(element_list) > 0:
                    element_list_xml = ""
                    for element in element_list:
                        element_list_xml += '<constituent>'
                        element_list_xml += "<element>" + element['name'] + "</element>"
                        element_list_xml += "<quantity>" + (XmlEntities().escape_xml_entities(element['qty']) if AUTO_ESCAPE_XML_ENTITIES else element['qty']) + "</quantity>"
                        element_list_xml += "<purity>" + (XmlEntities().escape_xml_entities(element['pur']) if AUTO_ESCAPE_XML_ENTITIES else element['pur']) + "</purity>"
                        element_list_xml += "<error>" + (XmlEntities().escape_xml_entities(element['err']) if AUTO_ESCAPE_XML_ENTITIES else element['err']) + "</error>"
                        element_list_xml += '</constituent>'
                    # set the data
                    data = element_list_xml
        return data

    def _render_data(self, request):
        """ Return module's data rendering

        Args:
            request:

        Returns:

        """
        return render_chemical_composition(self.data, True, True,
                                           'core_module_chemical_composition_app/render_data.html')

    def _get_popup_content(self):
        """ Return module's data rendering
        """
        # rendering data in the edit form
        data_template = render_chemical_composition(self.data, True, True,
                                                    'core_module_chemical_composition_app/edit_data.html')

        return get_chemical_composition_popup_content(self.data, data_template)
