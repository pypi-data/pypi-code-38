"""AJAX views for the Curate app
"""
import json

from django.contrib import messages
from django.contrib.messages.storage.base import Message
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseBadRequest, HttpResponse
from django.template import loader
from lxml.etree import XMLSyntaxError

import core_curate_app.common.exceptions as exceptions
import core_curate_app.components.curate_data_structure.api as curate_data_structure_api
import core_curate_app.permissions.rights as rights
import core_curate_app.views.user.forms as users_forms
import core_main_app.utils.decorators as decorators
from core_curate_app.components.curate_data_structure.models import CurateDataStructure
from core_curate_app.utils.parser import get_parser
from core_curate_app.views.user.views import generate_form, render_form, render_xml
from core_main_app.components.data import api as data_api
from core_main_app.components.data.models import Data
from core_main_app.components.lock import api as lock_api
from core_main_app.utils.xml import validate_xml_data, is_well_formed_xml
from core_parser_app.components.data_structure_element import api as data_structure_element_api
from core_parser_app.tools.parser.parser import remove_child_element
from core_parser_app.tools.parser.renderer.list import ListRenderer
from xml_utils.xsd_tree.xsd_tree import XSDTree
from core_main_app.utils.labels import get_data_label, get_form_label

# FIXME: delete_branch not deleting all elements
# FIXME: generate element not testing max occurrences


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def start_curate(request):
    """ Load forms to start curating.

    Args:
        request:

    Returns:

    """
    try:
        if request.method == 'POST':
            return _start_curate_post(request)
        else:
            return _start_curate_get(request)
    except Exception as e:
        return HttpResponseBadRequest(e.message)


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def generate_choice(request, curate_data_structure_id):
    """Generate a choice branch absent from the form.

    Args:
        request:
        curate_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)
        xsd_parser = get_parser()
        html_form = xsd_parser.generate_choice_absent(request, element_id, curate_data_structure.template.content)
    except Exception, e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def generate_element(request, curate_data_structure_id):
    """Generate an element absent from the form.

    Args:
        request:
        curate_data_structure_id:

    Returns:

    """
    try:
        element_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)
        xsd_parser = get_parser()
        html_form = xsd_parser.generate_element_absent(request, element_id, curate_data_structure.template.content)
    except Exception, e:
        return HttpResponseBadRequest()

    return HttpResponse(html_form)


# TODO: need to be reworked
@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def remove_element(request):
    """Remove an element from the form.

    Args:
        request:

    Returns:

    """
    element_id = request.POST['id']
    element_list = data_structure_element_api.get_all_by_child_id(element_id)

    if len(element_list) == 0:
        raise ValueError("No Data Structure Element found")
    elif len(element_list) > 1:
        raise ValueError("More than one Data Structure Element found")

    # Removing the element from the data structure
    data_structure_element = element_list[0]
    data_structure_element_to_pull = data_structure_element_api.get_by_id(element_id)

    # number of children after deletion
    children_number = len(data_structure_element.children) - 1

    data_structure_element = remove_child_element(data_structure_element,
                                                  data_structure_element_to_pull)

    response = {
        'code': 0,
        'html': ""
    }

    if children_number > data_structure_element.options['min']:
        return HttpResponse(json.dumps(response))
    else:  # len(schema_element.children) == schema_element.options['min']
        if data_structure_element.options['min'] != 0:
            response['code'] = 1
        else:  # schema_element.options['min'] == 0
            renderer = ListRenderer(data_structure_element, request)
            html_form = renderer.render(True)

            response['code'] = 2
            response['html'] = html_form

        return HttpResponse(json.dumps(response))


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def clear_fields(request):
    """Clear fields of the current form.

    Args:
        request:

    Returns:

    """
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)

        # generate form
        root_element = generate_form(curate_data_structure.template.content)

        # save the root element in the data structure
        curate_data_structure_api.update_data_structure_root(curate_data_structure, root_element)

        # renders the form
        xsd_form = render_form(request, root_element)

        return HttpResponse(json.dumps({'xsdForm': xsd_form}), content_type='application/javascript')
    except:
        return HttpResponseBadRequest()


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def cancel_changes(request):
    """Cancel changes of the current form.

    Args:
        request:

    Returns:

    """
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)

        if curate_data_structure.data is not None:
            # data already saved, reload from data
            xml_data = curate_data_structure.data.xml_content
        elif curate_data_structure.form_string is not None:
            # form already saved, reload from saved form
            xml_data = curate_data_structure.form_string
        else:
            # no saved data, load new form
            xml_data = None

        # generate form
        root_element = generate_form(curate_data_structure.template.content, xml_data)

        # save the root element in the data structure
        curate_data_structure_api.update_data_structure_root(curate_data_structure, root_element)

        # renders the form
        xsd_form = render_form(request, root_element)

        return HttpResponse(json.dumps({'xsdForm': xsd_form}), content_type='application/javascript')
    except:
        return HttpResponseBadRequest()


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def cancel_form(request):
    """Cancel current form.

    Args:
        request:

    Returns:

    """
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)
        # unlock from database
        if curate_data_structure.data is not None:
            lock_api.remove_lock_on_object(curate_data_structure.data, request.user)
        curate_data_structure_api.delete(curate_data_structure)

        # add success message
        messages.add_message(request, messages.SUCCESS, get_form_label().capitalize() + ' deleted with success.')

        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except:
        return HttpResponseBadRequest()


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def save_form(request):
    """Save the current form in data base. Converts it to XML format first.

    Args:
        request:

    Returns:

    """
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)

        # generate xml data
        xml_data = render_xml(curate_data_structure.data_structure_element_root)

        # update curate data structure data
        curate_data_structure.form_string = xml_data

        # save data structure
        curate_data_structure_api.upsert(curate_data_structure)

        # add success message
        message = Message(messages.SUCCESS, get_form_label().capitalize() + ' saved with success.')

        return HttpResponse(json.dumps({'message': message.message, 'tags': message.tags}),
                            content_type='application/json')
    except:
        return HttpResponseBadRequest()


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def validate_form(request):
    """Validate data present in the form via XML validation.

    Args:
        request:

    Returns:

    """
    response_dict = {}
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)

        # generate the XML
        xml_data = render_xml(curate_data_structure.data_structure_element_root)

        # build trees
        xsd_tree = XSDTree.build_tree(curate_data_structure.template.content)
        xml_tree = XSDTree.build_tree(xml_data)

        # validate XML document
        errors = validate_xml_data(xsd_tree, xml_tree)

        if errors is not None:
            response_dict['errors'] = errors

    except XMLSyntaxError as xml_syntax_error:
        response_dict['errors'] = "Your XML data is not well formatted. " + xml_syntax_error.message
    except Exception, e:
        message = e.message.replace('"', '\'') if e.message is not None else "The current document cannot be validated."
        response_dict['errors'] = message

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


@decorators.permission_required(content_type=rights.curate_content_type,
                                permission=rights.curate_access, raise_exception=True)
def save_data(request):
    """Save data - delete curate data structure.

    Args:
        request:

    Returns:

    """
    try:
        # get curate data structure
        curate_data_structure_id = request.POST['id']
        curate_data_structure = curate_data_structure_api.get_by_id(curate_data_structure_id)

        # unlock from database
        if curate_data_structure.data is not None:
            lock_api.remove_lock_on_object(curate_data_structure.data, request.user)

        # generate the XML
        xml_data = render_xml(curate_data_structure.data_structure_element_root)

        if curate_data_structure.data is not None:
            # update existing data
            data = curate_data_structure.data
        else:
            # create new data
            data = Data()
            data.title = curate_data_structure.name
            data.template = curate_data_structure.template
            data.user_id = str(request.user.id)

        # set content
        data.xml_content = xml_data
        # save data
        data_api.upsert(data, request.user)

        curate_data_structure_api.delete(curate_data_structure)

        messages.add_message(request, messages.SUCCESS, get_data_label().capitalize() + ' saved with success.')
    except Exception, e:
        message = e.message.replace('"', '\'')
        return HttpResponseBadRequest(message, content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


def _start_curate_post(request):
    """Start curate POST request.

    Args:
        request:

    Returns:

    """
    try:
        template_id = str(request.POST['hidden_value'])
        selected_option = request.POST['curate_form']
        user_id = str(request.user.id)
        if selected_option == "new" or selected_option == "upload":
            if selected_option == "new":
                new_form = users_forms.NewForm(request.POST)
                if new_form.is_valid():
                    name = new_form.data['document_name']
                    curate_data_structure = CurateDataStructure(user=user_id,
                                                                template=template_id,
                                                                name=name)
                else:
                    raise exceptions.CurateAjaxError('Error occurred during the validation ' + get_form_label())
            else:
                try:  # check XML data or not?
                    upload_form = users_forms.UploadForm(request.POST, request.FILES)
                    if upload_form.is_valid():
                        xml_file = request.FILES['file']
                        xml_file.seek(0)  # put the cursor at the beginning of the file
                        xml_data = xml_file.read()  # read the content of the file
                        well_formed = is_well_formed_xml(xml_data)
                        name = xml_file.name
                        if not well_formed:
                            raise exceptions.CurateAjaxError('Uploaded File is not well formed XML')
                        else:
                            curate_data_structure = CurateDataStructure(user=user_id,
                                                                        template=template_id,
                                                                        name=name,
                                                                        form_string=xml_data)
                    else:
                        raise exceptions.CurateAjaxError('Error occurred during the validation ' + get_form_label())
                except Exception as e:
                    raise exceptions.CurateAjaxError('Error during file uploading : ' + e.message)

            curate_data_structure_api.upsert(curate_data_structure)
        else:
            open_form = users_forms.OpenForm(request.POST)
            curate_data_structure = curate_data_structure_api.get_by_id(open_form.data['forms'])
        url = reverse("core_curate_enter_data", args=(curate_data_structure.id,))
        return HttpResponse(url)
    except Exception as e:
        raise exceptions.CurateAjaxError(e.message)


def _start_curate_get(request):
    """Start curate GET request.

    Args:
        request:

    Returns:

    """
    try:
        context_params = dict()
        template_id = request.GET['template_id']
        template = loader.get_template('core_curate_app/user/curate_start.html')

        open_form = users_forms.OpenForm(
            forms=curate_data_structure_api.get_all_by_user_id_and_template_id_with_no_data(
                str(request.user.id),
                template_id))
        new_form = users_forms.NewForm()
        upload_form = users_forms.UploadForm()
        hidden_form = users_forms.HiddenFieldsForm(hidden_value=template_id)
        context_params['new_form'] = new_form
        context_params['open_form'] = open_form
        context_params['upload_form'] = upload_form
        context_params['hidden_form'] = hidden_form
        context = {}
        context.update(request)
        context.update(context_params)
        return HttpResponse(json.dumps({'template': template.render(context)}),
                            content_type='application/javascript')
    except Exception as e:
        raise exceptions.CurateAjaxError('Error occurred during the ' + get_form_label() + ' display.')
