""" Fancy Tree module view
"""
import re

from core_main_registry_app.components.category import api as category_api
from core_main_registry_app.components.refinement import api as refinement_api
from core_main_registry_app.components.template import api as template_registry_api
from core_module_fancy_tree_registry_app.views.forms import RefinementForm
from core_parser_app.tools.modules.exceptions import ModuleError
from core_parser_app.tools.modules.views.module import AbstractModule
from xml_utils.xsd_tree.xsd_tree import XSDTree

CATEGORY_PREFIX = "_category"


class FancyTreeModule(AbstractModule):
    is_managing_occurrences = True

    def __init__(self):
        AbstractModule.__init__(self,
                                scripts=['core_module_fancy_tree_registry_app/js/fancy_tree.js'])

    def _render_module(self, request):
        # get the xml path of the element on which the module is placed
        xml_xpath = request.GET.get('xml_xpath', None)
        # xml path is provided
        if xml_xpath is not None:
            try:
                # create unique field id from xpath
                field_id = re.sub('[/.:\[\]]', '', xml_xpath)
                # split the xpath
                split_xml_xpath = xml_xpath.split('/')
                # get the last element of the xpath
                xml_element = split_xml_xpath[-1]
                # check if namespace is present
                if ":" in xml_element:
                    # split element name
                    split_xml_element = xml_element.split(":")
                    # only keep element name if namespace is present
                    xml_element = split_xml_element[-1]

                # get registry template
                template = template_registry_api.get_current_registry_template()
                # get all refinements for this template
                refinements = refinement_api.get_all_filtered_by_template_hash(template.hash)
                # get the refinement for the xml element
                refinement = refinements.get(xsd_name=xml_element)

                # initialize reload data for the form
                reload_form_data = {}

                # data to reload were provided
                if self.data != '':
                    # build filed for the refinement form for the current xml element
                    refinement_form_field = "{0}-{1}".format(RefinementForm.prefix, field_id)
                    # get the categories for the current refinement
                    categories = category_api.get_all_filtered_by_refinement_id(refinement.id)
                    # Initialize list of categories id
                    reload_categories_id_list = []
                    # load list of data to reload from XML
                    reload_data = XSDTree.fromstring("<root>" + self.data + "</root>")
                    # Iterate xml elements
                    for reload_data_element in list(reload_data):
                        try:
                            if len(reload_data_element) > 0:
                                # The xml element to be reloaded is the child element
                                child = reload_data_element[0]
                                # get its value
                                selected_value = child.text
                                # find the corresponding category and add its id to the list
                                reload_categories_id_list.append(categories.get(value=selected_value).id)
                        except Exception, e:
                            raise ModuleError("Something went wrong when reloading data from XML." + e.message)

                    # set data to reload in the form
                    reload_form_data[refinement_form_field] = reload_categories_id_list

                return AbstractModule.render_template('core_module_fancy_tree_registry_app/fancy_tree.html',
                                                      {'form': RefinementForm(refinement=refinement,
                                                                              field_id=field_id,
                                                                              data=reload_form_data)})
            except Exception, e:
                raise ModuleError("Something went wrong when rendering the module: " + e.message)
        else:
            raise ModuleError("xml_xpath was not found in request GET parameters.")

    def _retrieve_data(self, request):
        data = ''
        if request.method == 'GET':
            if 'data' in request.GET:
                data = request.GET['data']

        elif request.method == 'POST':
            form = RefinementForm(request.POST)
            if not form.is_valid():
                raise ModuleError('Data not properly sent to server.')

            if 'data[]' in request.POST:
                try:
                    category_id_list = request.POST.getlist('data[]')
                    for category_id in category_id_list:
                        category = category_api.get_by_id(category_id)
                        if not category.value.endswith(CATEGORY_PREFIX):
                            split_category_path = category.path.split('.')

                            data += "<{0}><{1}>{2}</{1}></{0}>".format(split_category_path[-2],
                                                                       split_category_path[-1],
                                                                       category.value)
                except Exception, e:
                    raise ModuleError('Something went wrong during the processing of posted data: ' + e.message)

        return data

    def _render_data(self, request):
        return ''
