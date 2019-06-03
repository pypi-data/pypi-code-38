"""Explore Example app Ajax views
"""
import json

from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.generic import View

import core_explore_example_app.permissions.rights as rights
import core_main_app.utils.decorators as decorators
from core_explore_common_app.components.query import api as query_api
from core_explore_common_app.views.user.ajax import CreatePersistentQueryUrlView
from core_explore_example_app.apps import ExploreExampleAppConfig
from core_explore_example_app.commons.exceptions import MongoQueryException
from core_explore_example_app.components.explore_data_structure import api as explore_data_structure_api
from core_explore_example_app.components.persistent_query_example.models import PersistentQueryExample
from core_explore_example_app.components.saved_query import api as saved_query_api
from core_explore_example_app.components.saved_query.models import SavedQuery
from core_explore_example_app.utils.displayed_query import sub_elements_to_pretty_query, fields_to_pretty_query
from core_explore_example_app.utils.mongo_query import get_parent_name, sub_elements_to_query, \
    check_query_form
from core_explore_example_app.utils.parser import generate_element_absent, \
    generate_choice_absent, remove_form_element
from core_explore_example_app.utils.query_builder import render_initial_form, \
    render_new_query, render_new_criteria, render_sub_elements_query, prune_html_tree, get_user_inputs
from core_main_app.commons import exceptions
from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.components.template import api as template_api
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from xml_utils.html_tree import parser as html_tree_parser
from xml_utils.xsd_tree.operations.namespaces import get_namespaces, get_default_prefix


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def generate_element(request, explore_data_structure_id):
    """ Generate an element absent from the form.

    Args:
        request:
        explore_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        explore_data_structure = explore_data_structure_api.get_by_id(explore_data_structure_id)
        html_form = generate_element_absent(request, element_id, explore_data_structure.template.content)
    except Exception, e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def generate_choice(request, explore_data_structure_id):
    """Generate a choice branch absent from the form.

    Args:
        request:
        explore_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        explore_data_structure = explore_data_structure_api.get_by_id(explore_data_structure_id)
        html_form = generate_choice_absent(request, element_id, explore_data_structure.template.content)
    except Exception, e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def remove_element(request):
    """Remove an element from the form.

    Args:
        request:

    Returns:

    """
    element_id = request.POST['id']
    code, html_form = remove_form_element(request, element_id)
    return HttpResponse(json.dumps({'code': code, 'html': html_form}))


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def save_fields(request):
    """Saves the fields selected by the user

    Args:
        request:

    Returns:

    """
    try:
        # get parameters form request
        form_content = request.POST['formContent']
        template_id = request.POST['templateID']

        # modify the form string to only keep the selected elements
        html_tree = html_tree_parser.from_string(form_content)
        any_checked = prune_html_tree(html_tree)

        # get explore data structure
        explore_data_structure = explore_data_structure_api.get_by_user_id_and_template_id(str(request.user.id),
                                                                                           template_id)

        # if checkboxes were checked
        if any_checked:
            # save html form
            explore_data_structure.selected_fields_html_tree = html_tree_parser.to_string(html_tree)
        else:
            # otherwise, empty any previously saved html form
            explore_data_structure.selected_fields_html_tree = None

        # update explore data structure
        explore_data_structure_api.upsert(explore_data_structure)

        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest("An error occurred while saving the form.")


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def select_element(request):
    """Select an element in the custom tree

    Args:
        request:

    Returns:

    """
    # get element id
    element_id = request.POST['elementID']

    # get schema element
    schema_element = data_structure_element_api.get_by_id(element_id)

    response_dict = {
        "elementName": schema_element.options['label'],
        "elementID": element_id,
    }

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def get_sub_elements_query_builder(request):
    """Build the form for queries on sub elements

    Args:
        request:

    Returns:

    """
    leaves_id = request.POST['leavesID']
    template_id = request.POST['templateID']

    # get list of ids from string
    list_leaves_id = leaves_id.split(" ")

    # get template
    template = template_api.get(template_id)

    # get template namespaces
    namespaces = get_namespaces(template.content)
    # get default prefix
    default_prefix = get_default_prefix(namespaces)

    # get the parent name using the first schema element of the list
    parent_name = get_parent_name(list_leaves_id[0], namespaces)

    form_fields = []
    for leaf_id in list_leaves_id:
        data_structure_element = data_structure_element_api.get_by_id(leaf_id)
        element_type = data_structure_element.options['type']
        element_name = data_structure_element.options['name']

        user_inputs = get_user_inputs(element_type, data_structure_element, default_prefix)

        form_fields.append({'element_id': leaf_id,
                            'element_name': element_name,
                            'element_type': element_type,
                            'html': user_inputs})

    response_dict = {'subElementQueryBuilder': render_sub_elements_query(parent_name, form_fields)}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def insert_sub_elements_query(request):
    """Inserts a query for a sub element in the query builder

    Args:
        request:

    Returns:

    """
    form_values = json.loads(request.POST['formValues'])
    template_id = request.POST['templateID']
    criteria_id = request.POST['criteriaID']

    # get template
    template = template_api.get(template_id)

    # get template namespaces
    namespaces = get_namespaces(template.content)
    # get default prefix
    default_prefix = get_default_prefix(namespaces)

    # keep only selected fields
    form_values = [field for field in form_values if field['selected'] is True]
    errors = check_query_form(form_values, template_id)

    if len(errors) == 0:
        query = sub_elements_to_query(form_values, namespaces, default_prefix)
        displayed_query = sub_elements_to_pretty_query(form_values, namespaces)
        ui_id = "ui" + criteria_id[4:]
        temporary_query = SavedQuery(user_id=ExploreExampleAppConfig.name,
                                     template=template,
                                     query=json.dumps(query),
                                     displayed_query=displayed_query)
        saved_query_api.upsert(temporary_query)
        response_dict = {'criteriaID': criteria_id,
                         'prettyQuery': displayed_query,
                         'uiID': ui_id,
                         'queryID': str(temporary_query.id)}
    else:
        return HttpResponseBadRequest("<br/>".join(errors), content_type='application/javascript')

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def update_user_input(request):
    """Updates the user input of the query builder according to the type of the selected element

    Args:
        request:

    Returns:

    """
    from_element_id = request.POST['elementID']
    template_id = request.POST['templateID']

    # get schema element
    data_structure_element = data_structure_element_api.get_by_id(from_element_id)
    # get template
    template = template_api.get(template_id)

    # convert xml path to mongo dot notation
    namespaces = get_namespaces(template.content)
    default_prefix = get_default_prefix(namespaces)

    element_type = data_structure_element.options['type']
    user_inputs = get_user_inputs(element_type, data_structure_element, default_prefix)

    response_dict = {'userInputs': user_inputs, 'element_type': element_type}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def add_criteria(request):
    """Adds an empty criteria to the query builder

    Args:
        request:

    Returns:

    """
    tag_id = request.POST['tagID']
    new_criteria_html = render_new_criteria(tag_id)

    response_dict = {'criteria': new_criteria_html}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


def _render_errors(errors):
    """Renders a list of errors in a paragraph

    Args:
        errors:

    Returns:

    """
    return '<br/>'.join(errors)


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def clear_criteria(request):
    """Clears the Query Builder

    Args:
        request:

    Returns:

    """
    new_form = render_initial_form()
    response_dict = {'queryForm': new_form}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_delete_query, raise_exception=True)
def clear_queries(request):
    """Deletes all saved queries

    Args:
        request:

    Returns:

    """
    template_id = request.POST['templateID']
    saved_queries = saved_query_api.get_all_by_user_and_template(user_id=str(request.user.id),
                                                                 template_id=template_id)
    for saved_query in saved_queries:
        saved_query_api.delete(saved_query)

    return HttpResponse(json.dumps({}), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_delete_query, raise_exception=True)
def delete_query(request):
    """Deletes a query and update the HTML display

    Args:
        request:

    Returns:

    """
    saved_query_id = request.POST['savedQueryID']
    try:
        saved_query = saved_query_api.get_by_id(saved_query_id[5:])
    except DoesNotExist:
        return HttpResponseBadRequest("The saved query does not exist anymore.")
    saved_query_api.delete(saved_query)
    return HttpResponse(json.dumps({}), content_type='application/javascript')


@decorators.permission_required(content_type=rights.explore_example_content_type,
                                permission=rights.explore_example_access, raise_exception=True)
def add_query_criteria(request):
    """Adds the selected query to query builder

    Args:
        request:

    Returns:

    """
    tag_id = request.POST['tagID']
    saved_query_id = request.POST['savedQueryID']

    # check if first criteria
    is_first = True if int(tag_id) == 1 else False

    # get saved query number from id
    try:
        saved_query = saved_query_api.get_by_id(saved_query_id)
    except DoesNotExist:
        return HttpResponseBadRequest("The saved query does not exist anymore.")

    new_query_html = render_new_query(tag_id, saved_query, is_first)
    response_dict = {'query': new_query_html, 'first': is_first}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


class GetQueryView(View):
    fields_to_query_func = None

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_access, raise_exception=True))
    def post(self, request):
        """Get a query

        Args:
            request:

        Returns:

        """
        try:
            template_id = request.POST['templateID']
            query_id = request.POST['queryID']
            form_values = json.loads(request.POST['formValues'])

            # save current query builder in session to restore it when coming back to the page
            query_form = request.POST['queryForm']
            request.session['savedQueryFormExplore'] = query_form

            errors = check_query_form(form_values, template_id)
            query_object = query_api.get_by_id(query_id)
            if len(query_object.data_sources) == 0:
                errors.append("Please select at least 1 data source.")

            if len(errors) == 0:
                query_content = self.fields_to_query_func(form_values, template_id)
                query_object.content = json.dumps(query_content)
                query_api.upsert(query_object)
            else:
                return HttpResponseBadRequest(_render_errors(errors), content_type='application/javascript')

            return HttpResponse(json.dumps({}), content_type='application/javascript')
        except exceptions.ModelError:
            return HttpResponseBadRequest('Invalid input.', content_type='application/javascript')
        except Exception:
            return HttpResponseBadRequest('An unexpected error occurred.', content_type='application/javascript')


class SaveQueryView(View):
    fields_to_query_func = None

    @method_decorator(decorators.
                      permission_required(content_type=rights.explore_example_content_type,
                                          permission=rights.explore_example_save_query,
                                          raise_exception=True))
    def post(self, request):
        """Save a query and update the html display

        Args:
            request:

        Returns:

        """
        form_values = json.loads(request.POST['formValues'])
        template_id = request.POST['templateID']

        # Check that the user can save a query
        if '_auth_user_id' not in request.session:
            error = 'You have to login to save a query.'
            return HttpResponseBadRequest(error, content_type='application/javascript')

        # Check that the query is valid
        errors = check_query_form(form_values, template_id)
        if len(errors) == 0:
            try:
                query = self.fields_to_query_func(form_values, template_id)
                displayed_query = fields_to_pretty_query(form_values)

                # save the query in the data base
                saved_query = SavedQuery(user_id=str(request.user.id),
                                         template=template_api.get(template_id),
                                         query=json.dumps(query),
                                         displayed_query=displayed_query)
                saved_query_api.upsert(saved_query)
            except MongoQueryException, e:
                errors = [e.message]
                return HttpResponseBadRequest(_render_errors(errors),
                                              content_type='application/javascript')
        else:
            return HttpResponseBadRequest(_render_errors(errors),
                                          content_type='application/javascript')

        return HttpResponse(json.dumps({}), content_type='application/javascript')


class CreatePersistentQueryExampleUrlView(CreatePersistentQueryUrlView):
    """ Create the persistent url from a Query
    """
    view_to_reverse = "core_explore_example_results_redirect"

    @staticmethod
    def _create_persistent_query(query):
        # create the persistent query
        return PersistentQueryExample(user_id=query.user_id,
                                      content=query.content,
                                      templates=query.templates,
                                      data_sources=query.data_sources)
