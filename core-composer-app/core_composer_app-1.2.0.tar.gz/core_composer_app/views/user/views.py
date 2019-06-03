"""Composer app user views
"""
from os.path import join

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.urlresolvers import reverse_lazy

from core_composer_app.components.bucket import api as bucket_api
from core_composer_app.components.type_version_manager import api as type_version_manager_api
from core_composer_app.permissions import rights
from core_main_app.components.template import api as template_api
from core_main_app.components.template_version_manager import api as template_version_manager_api
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.utils import decorators as decorators
from core_main_app.utils.file import read_file_content, get_file_http_response
from core_main_app.utils.rendering import render
from core_main_app.utils.xml import xsl_transform
from core_main_app.views.user.views import get_context_manage_template_versions
from xml_utils.commons.constants import LXML_SCHEMA_NAMESPACE
from xml_utils.xsd_tree.operations.annotation import remove_annotations
from xml_utils.xsd_tree.xsd_tree import XSDTree
from xml_utils.xsd_types.xsd_types import get_xsd_types


# TODO: see if sessions are problematic


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, login_url=reverse_lazy("core_main_app_login"))
def index(request):
    """ Page that allows to select a template to start composing.

    Args:
        request:

    Returns:

    """
    assets = {
        "js": [],
    }

    global_active_template_list = template_version_manager_api.get_active_global_version_manager(_cls=True)
    user_active_template_list = template_version_manager_api.get_active_version_manager_by_user_id(request.user.id,
                                                                                                   _cls=True)

    global_active_type_list = type_version_manager_api.get_active_global_version_manager()
    user_active_type_list = type_version_manager_api.get_active_version_manager_by_user_id(request.user.id)

    context = {
        'global_templates': global_active_template_list,
        'global_types': global_active_type_list,
        'user_templates': user_active_template_list,
        'user_types': user_active_type_list,
    }

    return render(request,
                  'core_composer_app/user/index.html',
                  assets=assets,
                  context=context)


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, login_url=reverse_lazy("core_main_app_login"))
def build_template(request, template_id):
    """View that allows to build the Template.

    Args:
        request:
        template_id:

    Returns:

    """
    if template_id == "new":
        base_template_path = finders.find(join('core_composer_app', 'user', 'xsd', 'new_base_template.xsd'))
        xsd_string = read_file_content(base_template_path)
    else:
        template = template_api.get(template_id)
        xsd_string = template.content

    request.session['newXmlTemplateCompose'] = xsd_string
    request.session['includedTypesCompose'] = []

    # store the current includes/imports
    xsd_tree = XSDTree.build_tree(xsd_string)
    includes = xsd_tree.findall("{}include".format(LXML_SCHEMA_NAMESPACE))
    for el_include in includes:
        if 'schemaLocation' in el_include.attrib:
            request.session['includedTypesCompose'].append(el_include.attrib['schemaLocation'])
    imports = xsd_tree.findall("{}import".format(LXML_SCHEMA_NAMESPACE))
    for el_import in imports:
        if 'schemaLocation' in el_import.attrib:
            request.session['includedTypesCompose'].append(el_import.attrib['schemaLocation'])

    # remove annotations from the tree
    remove_annotations(xsd_tree)
    xsd_string = XSDTree.tostring(xsd_tree)

    # loads XSLT
    xslt_path = finders.find(join('core_composer_app', 'user', 'xsl', 'xsd2html.xsl'))
    # reads XSLT
    xslt_string = read_file_content(xslt_path)
    # transform XML to HTML
    xsd_to_html_string = xsl_transform(xsd_string, xslt_string)

    # 1) Get user defined types
    user_types = type_version_manager_api.get_version_managers_by_user(str(request.user.id))
    # 2) Get buckets
    buckets = bucket_api.get_all()

    # 3) no_buckets_types: list of types that are not assigned to a specific bucket
    no_buckets_types = type_version_manager_api.get_no_buckets_types()

    # 4) Build list of built-in types
    built_in_types = []
    for built_in_type in get_xsd_types():
        built_in_types.append({'current': 'built_in_type', 'title': built_in_type})

    assets = {
        "js": [
            {
                "path": 'core_composer_app/user/js/build_template.js',
                "is_raw": False
            },
            {
                "path": 'core_composer_app/user/js/build_template.raw.js',
                "is_raw": True
            },
            {
                "path": 'core_composer_app/user/js/xpath.js',
                "is_raw": False
            },
            {
                "path": 'core_composer_app/user/js/menus.js',
                "is_raw": False
            },
            {
                "path": 'core_composer_app/user/js/xsd_tree.js',
                "is_raw": False
            },
        ],
        "css": ['core_main_app/common/css/XMLTree.css',
                'core_composer_app/common/css/bucket.css',
                'core_composer_app/user/css/menu.css',
                'core_composer_app/user/css/style.css',
                'core_composer_app/user/css/xsd_tree.css']
    }
    context = {
        'buckets': buckets,
        'built_in_types': built_in_types,
        'no_buckets_types': no_buckets_types,
        'user_types': user_types,
        'xsd_form': xsd_to_html_string,
        'template_id': template_id,
    }

    modals = [
        'core_composer_app/user/builder/menus/sequence.html',
        'core_composer_app/user/builder/menus/element.html',
        'core_composer_app/user/builder/menus/element_root.html',

        'core_composer_app/user/builder/modals/root_type_name.html',
        'core_composer_app/user/builder/modals/element_name.html',
        'core_composer_app/user/builder/modals/insert_element.html',
        'core_composer_app/user/builder/modals/delete_element.html',
        'core_composer_app/user/builder/modals/change_type.html',
        'core_composer_app/user/builder/modals/save_template.html',
        'core_composer_app/user/builder/modals/save_type.html',
        'core_composer_app/user/builder/modals/save_success.html',
        'core_composer_app/user/builder/modals/occurrences.html',
        'core_composer_app/user/builder/modals/errors.html',
    ]

    return render(request,
                  'core_composer_app/user/build_template.html',
                  assets=assets,
                  context=context,
                  modals=modals)


@decorators.permission_required(content_type=rights.composer_content_type,
                                permission=rights.composer_access, login_url=reverse_lazy("core_main_app_login"))
def download_xsd(request):
    """Make the current XSD available for download.

    Args:
        request:

    Returns:

    """
    xsd_string = request.session['newXmlTemplateCompose']

    # return the file
    return get_file_http_response(file_content=xsd_string,
                                  file_name="schema.xsd",
                                  content_type="application/xsd",
                                  extension=".xsd")


def manage_type_versions(request, version_manager_id):
    """View that allows type versions management.

    Args:
        request:
        version_manager_id:

    Returns:

    """
    try:
        # get the version manager
        version_manager = version_manager_api.get(version_manager_id)
        context = get_context_manage_template_versions(version_manager, "Type")
        if 'core_parser_app' in settings.INSTALLED_APPS:
            context.update({"module_url": "core_composer_app_type_modules"})

        assets = {
                    "js": [
                        {
                            "path": 'core_main_app/common/js/templates/versions/set_current.js',
                            "is_raw": False
                        },
                        {
                            "path": 'core_main_app/common/js/templates/versions/restore.js',
                            "is_raw": False
                        },
                        {
                            "path": 'core_main_app/common/js/templates/versions/modals/disable.js',
                            "is_raw": False
                        }
                    ]
                }

        modals = ["core_main_app/admin/templates/versions/modals/disable.html"]

        return render(request,
                      'core_composer_app/user/types/versions.html',
                      assets=assets,
                      modals=modals,
                      context=context)
    except Exception, e:
        return render(request,
                      'core_main_app/common/commons/error.html',
                      context={'error': e.message})
