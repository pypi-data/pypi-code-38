"""AJAX user views of composer application
"""
import json
from urlparse import urlparse

from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template import loader

from core_composer_app.components.type import api as type_api
from core_composer_app.components.type.models import Type
from core_composer_app.components.type_version_manager import api as type_version_manager_api
from core_composer_app.components.type_version_manager.models import TypeVersionManager
from core_composer_app.permissions import rights
from core_composer_app.utils import xml as composer_xml_utils
from core_main_app.commons import exceptions
from core_main_app.components.template.models import Template
from core_main_app.components.template_version_manager import api as template_version_manager_api
from core_main_app.components.template_version_manager.models import TemplateVersionManager
from core_main_app.utils import decorators as decorators
from core_main_app.utils import xml as main_xml_utils
from core_main_app.utils.urls import get_template_download_pattern
from xml_utils.xsd_tree.xsd_tree import XSDTree


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def insert_element_sequence(request):
    """Insert the type in the original schema.

    Args:
        request:

    Returns:

    """
    try:
        type_id = request.POST['typeID']
        type_name = request.POST['typeName']
        xpath = request.POST['xpath']
        namespace = request.POST['namespace']
        path = request.POST['path']

        # get link to the type to include
        xsd_string = request.session['newXmlTemplateCompose']

        if type_id == 'built_in_type':
            # insert built-in type into xsd string
            new_xsd_str = composer_xml_utils.insert_element_built_in_type(xsd_string, xpath, type_name)
        else:
            # get type from database
            type_object = type_api.get(type_id)
            # generate include url
            include_url = main_xml_utils._get_schema_location_uri(str(type_id))
            # insert element in xsd string
            new_xsd_str = composer_xml_utils.insert_element_type(xsd_string, xpath, type_object.content, type_name,
                                                                 include_url)
            # add the id of the type if not already present
            if include_url not in request.session['includedTypesCompose']:
                request.session['includedTypesCompose'].append(include_url)

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = new_xsd_str

        template = loader.get_template('core_composer_app/user/builder/new_element.html')
        context = {'namespace': namespace,
                   'path': path,
                   'type_name': type_name}
        new_element_html = template.render(context)
        return HttpResponse(json.dumps({'new_element': new_element_html}), content_type='application/json')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def change_xsd_type(request):
    """Change the type of the element.

    Args:
        request:

    Returns:

    """
    try:
        xpath = request.POST['xpath']
        new_type = request.POST['newType']
        xsd_string = request.session['newXmlTemplateCompose']

        # change type
        xsd_string = composer_xml_utils.change_xsd_element_type(xsd_string, xpath, new_type)

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = xsd_string
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def change_root_type_name(request):
    """Change the name of the root type.

    Args:
        request:

    Returns:

    """
    try:
        type_name = request.POST['typeName']
        xsd_string = request.session['newXmlTemplateCompose']

        # rename root type
        xsd_string = composer_xml_utils.rename_single_root_type(xsd_string, type_name)

        request.session['newXmlTemplateCompose'] = xsd_string
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def rename_element(request):
    """Replace the current name of the element by the new name.

    Args:
        request:

    Returns:

    """
    try:
        xpath = request.POST['xpath']
        new_name = request.POST['newName']
        xsd_string = request.session['newXmlTemplateCompose']

        # rename element
        xsd_string = composer_xml_utils.rename_xsd_element(xsd_string, xpath, new_name)

        # build xsd tree
        xsd_tree = XSDTree.build_tree(xsd_string)
        # validate the schema
        error = main_xml_utils.validate_xml_schema(xsd_tree)

        if error is not None:
            return _error_response("This is not a valid name.")

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = xsd_string

        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def delete_element(request):
    """Delete an element from the xsd string.

    Args:
        request:

    Returns:

    """
    try:
        xpath = request.POST['xpath']
        xsd_string = request.session['newXmlTemplateCompose']

        # delete element from string
        xsd_string = composer_xml_utils.delete_xsd_element(xsd_string, xpath)

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = xsd_string

        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def get_element_occurrences(request):
    """Get the occurrences of the selected element.

    Args:
        request:

    Returns:

    """
    try:
        xpath = request.POST['xpath']
        xsd_string = request.session['newXmlTemplateCompose']

        # get occurrences of xsd element
        min_occurs, max_occurs = composer_xml_utils.get_xsd_element_occurrences(xsd_string, xpath)

        response_dict = {'minOccurs': min_occurs, 'maxOccurs': max_occurs}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, raise_exception=True)
def set_element_occurrences(request):
    """Set the occurrences of the selected element.

    Args:
        request:

    Returns:

    """
    try:
        xpath = request.POST['xpath']
        min_occurs = request.POST['minOccurs']
        max_occurs = request.POST['maxOccurs']
        xsd_string = request.session['newXmlTemplateCompose']

        # set element occurrences
        xsd_string = composer_xml_utils.set_xsd_element_occurrences(xsd_string, xpath, min_occurs, max_occurs)

        # save the tree in the session
        request.session['newXmlTemplateCompose'] = xsd_string
        return HttpResponse(json.dumps({}), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_save_template, raise_exception=True)
def save_template(request):
    """Save the current template in the database.

    Args:
        request:

    Returns:

    """
    try:
        template_name = request.POST['templateName']
        xsd_string = request.session['newXmlTemplateCompose']

        response_dict = {}

        try:
            # Build XSD tree
            xsd_tree = XSDTree.build_tree(xsd_string)

            # validate the schema
            error = main_xml_utils.validate_xml_schema(xsd_tree)

            if error is not None:
                return _error_response('This is not a valid XML schema. ' + error)
        except Exception, e:
            return _error_response('This is not a valid XML schema. ' + e.message)

        # get list of dependencies
        dependencies = _get_dependencies_ids(request.session["includedTypesCompose"])

        try:
            # create template version manager
            template_version_manager = TemplateVersionManager(title=template_name, user=str(request.user.id))
            # create template
            template = Template(filename=template_name, content=xsd_string, dependencies=dependencies)
            # save template in database
            template_version_manager_api.insert(template_version_manager, template)
        except exceptions.NotUniqueError:
            return HttpResponseBadRequest("A template with the same name already exists. Please choose another name.")
        except Exception, e:
            return _error_response(e.message)

        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_save_type, raise_exception=True)
def save_type(request):
    """Save the current type in the database.

    Args:
        request:

    Returns:

    """
    try:
        type_name = request.POST['typeName']
        template_id = request.POST['templateID']
        xsd_string = request.session['newXmlTemplateCompose']

        response_dict = {}

        # can save as type if new type or from existing type
        if template_id != "new":
            try:
                # check if the type exists, raises exception otherise
                type_api.get(template_id)
            except:
                # the type does not exist
                return _error_response("Unable to save an existing template as a type.")

        try:
            # remove root from tree if present
            xsd_string = composer_xml_utils.remove_single_root_element(xsd_string)
            # build xsd tree
            xsd_tree = XSDTree.build_tree(xsd_string)
            # validate the schema
            error = main_xml_utils.validate_xml_schema(xsd_tree)

            if error is not None:
                return _error_response('This is not a valid XML schema. ' + error)
        except Exception, e:
            return _error_response('This is not a valid XML schema. ' + e.message)

        dependencies = _get_dependencies_ids(request.session["includedTypesCompose"])

        try:
            # create type version manager
            type_version_manager = TypeVersionManager(title=type_name, user=str(request.user.id))
            # create type
            type_object = Type(filename=type_name, content=xsd_string, dependencies=dependencies)
            # save type in database
            type_version_manager_api.insert(type_version_manager, type_object)
        except exceptions.NotUniqueError, e:
            return HttpResponseBadRequest("A type with the same name already exists. Please choose another name.")
        except Exception, e:
            return _error_response(e.message)

        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')


def _get_dependencies_ids(list_dependencies):
    """Return list of type ids from list of dependencies.

    Args:
        list_dependencies:

    Returns:

    """
    # declare list of dependencies
    dependencies = []
    # get pattern to match a template download
    pattern = get_template_download_pattern()
    # get all type ids
    for uri in list_dependencies:
        # parse dependency url
        url = urlparse(uri)
        try:
            # get object id from url
            object_id = pattern.match(url.path).group('pk')
            # get type by id, exception raised if not found
            type_object = type_api.get(object_id)
            # add id to list of internal dependencies
            dependencies.append(type_object)
        except:
            # id not found, don't add it to list of dependencies
            pass

    return dependencies


def _error_response(error):
    """Return HttpResponse containing the error message.

    Args:
        error:

    Returns:

    """
    return HttpResponseBadRequest(error.replace("'", ""), content_type='application/javascript')
