from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse

from core_main_app.utils.rendering import admin_render
from core_main_app.views.common.ajax import AddObjectModalView, EditObjectModalView, \
    DeleteObjectModalView
from core_oaipmh_provider_app import settings
from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as oai_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_set import api as oai_provider_set_api
from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.components.oai_xsl_template import api as oai_xsl_template_api


@staff_member_required
def identity_view(request):
    assets = {
        "js": [
            {
                "path": "core_oaipmh_provider_app/admin/js/registry/identity/check_registry.js",
                "is_raw": False
            },
            EditObjectModalView.get_modal_js_path()
        ],
        "css": [
            "core_oaipmh_provider_app/admin/css/registry/identity/table_info.css"
        ]
    }

    modals = [
        EditObjectModalView.get_modal_html_path()
    ]

    info = oai_settings_api.get()
    data_provider = {
        'id': info.id,
        'name': info.repository_name,
        'baseURL': request.build_absolute_uri(reverse("core_oaipmh_provider_app_server_index")),
        'protocol_version': settings.OAI_PROTOCOL_VERSION,
        'admins': (email for name, email in settings.OAI_ADMINS),
        'deleted': settings.OAI_DELETED_RECORD,
        'granularity': settings.OAI_GRANULARITY,
        'identifier_scheme': settings.OAI_SCHEME,
        'repository_identifier': info.repository_identifier,
        'identifier_delimiter': settings.OAI_DELIMITER,
        'sample_identifier': settings.OAI_SAMPLE_IDENTIFIER,
        'enable_harvesting': info.enable_harvesting,
    }

    context = {
        "data_provider": data_provider,
        "object_name": info.repository_name
    }

    return admin_render(request, "core_oaipmh_provider_app/admin/registry/identity.html", assets=assets,
                        context=context, modals=modals)


@staff_member_required
def metadata_formats_view(request):
    assets = {
        "js": [
            AddObjectModalView.get_modal_js_path(),
            EditObjectModalView.get_modal_js_path(),
            DeleteObjectModalView.get_modal_js_path(),
        ],
        "css": [
            "core_oaipmh_provider_app/admin/css/registry/metadata_formats/page.css"
        ]
    }

    modals = [
        AddObjectModalView.get_modal_html_path(),
        EditObjectModalView.get_modal_html_path(),
        DeleteObjectModalView.get_modal_html_path(),
    ]

    order_field = 'metadata_prefix'
    default_metadata_formats = oai_metadata_format_api.get_all_default_metadata_format(order_by_field=order_field)
    metadata_formats = oai_metadata_format_api.get_all_custom_metadata_format(order_by_field=order_field)
    template_metadata_formats = _get_template_metadata_format(request, order_field=order_field)

    context = {
        'default_metadata_formats': default_metadata_formats,
        'metadata_formats': metadata_formats,
        'template_metadata_formats': template_metadata_formats
    }

    return admin_render(request, "core_oaipmh_provider_app/admin/registry/metadata_formats.html", assets=assets,
                        context=context, modals=modals)


@staff_member_required
def sets_view(request):
    assets = {
        "js": [
            {
                "path": "core_oaipmh_provider_app/admin/js/registry/sets/modals/init_select.js",
                "is_raw": False
            },
            {
                "path": "core_oaipmh_provider_app/admin/libs/fSelect/js/fSelect.js",
                "is_raw": False
            },
            AddObjectModalView.get_modal_js_path(),
            EditObjectModalView.get_modal_js_path(),
            DeleteObjectModalView.get_modal_js_path(),
        ],
        "css": [
            "core_oaipmh_provider_app/admin/libs/fSelect/css/fSelect.css",
            "core_oaipmh_provider_app/admin/css/registry/sets/add_set.css"
        ]
    }

    modals = [
        AddObjectModalView.get_modal_html_path(),
        EditObjectModalView.get_modal_html_path(),
        DeleteObjectModalView.get_modal_html_path(),
    ]

    context = {
        'sets': oai_provider_set_api.get_all(order_by_field='set_spec')
    }

    return admin_render(request, "core_oaipmh_provider_app/admin/registry/sets.html", assets=assets,
                        context=context, modals=modals)


def _get_template_metadata_format(request, order_field=None):
    """ Get template metadata format information.
    Args:
        order_field: Possibility to order by field.

    Returns:
        Template metadata format information.

    """
    items_template_metadata_format = []
    template_metadata_formats = oai_metadata_format_api.get_all_template_metadata_format(order_by_field=order_field)
    for template_item in template_metadata_formats:
        host_uri = request.build_absolute_uri('/')
        item_info = {
            'id': template_item.id,
            'metadata_prefix': template_item.metadata_prefix,
            'schema': oai_metadata_format_api.get_metadata_format_schema_url(template_item, host_uri),
            'title': template_item.template.display_name,
            'metadata_namespace': template_item.metadata_namespace
        }
        items_template_metadata_format.append(item_info)

    return items_template_metadata_format


@staff_member_required
def xsl_template_view(request, metadata_format_id):
    assets = {
        "js": [
            AddObjectModalView.get_modal_js_path(),
            EditObjectModalView.get_modal_js_path(),
            DeleteObjectModalView.get_modal_js_path(),
        ],
    }

    modals = [
        AddObjectModalView.get_modal_html_path(),
        EditObjectModalView.get_modal_html_path(),
        DeleteObjectModalView.get_modal_html_path(),
    ]

    metadata_format = oai_metadata_format_api.get_by_id(metadata_format_id)

    context = {
        "xsl_templates": _get_xsl_templates(metadata_format),
        "metadata_format": metadata_format
    }

    return admin_render(request, "core_oaipmh_provider_app/admin/registry/xsl_template.html", assets=assets,
                        context=context, modals=modals)


def _get_xsl_templates(metadata_format):
    """ Get template metadata format information.
    Args:
        metadata_format: OaiProviderMetadataFormat.

    Returns:
        Template metadata format information.

    """
    items_xsl_templates = []
    xsl_templates = oai_xsl_template_api.get_all_by_metadata_format(metadata_format)
    for item in xsl_templates:
        item_info = {
            'id': item.id,
            'template_title': item.template.display_name,
            'xslt': item.xslt,
        }
        items_xsl_templates.append(item_info)

    return items_xsl_templates
