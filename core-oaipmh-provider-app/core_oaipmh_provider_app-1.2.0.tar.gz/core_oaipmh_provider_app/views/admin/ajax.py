"""Admin AJAX views
"""
import json

from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseBadRequest, HttpResponse
from requests import ConnectionError
from rest_framework import status

from core_main_app.commons.exceptions import NotUniqueError
from core_main_app.utils.requests_utils.requests_utils import send_get_request
from core_main_app.views.common.ajax import AddObjectModalView, EditObjectModalView, \
    DeleteObjectModalView
from core_oaipmh_provider_app.components.oai_provider_metadata_format import api as \
    oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format.models import \
    OaiProviderMetadataFormat
from core_oaipmh_provider_app.components.oai_provider_set import api as oai_provider_set_api
from core_oaipmh_provider_app.components.oai_provider_set.models import OaiProviderSet
from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.components.oai_settings.models import OaiSettings
from core_oaipmh_provider_app.components.oai_xsl_template import api as oai_xsl_template_api
from core_oaipmh_provider_app.components.oai_xsl_template.models import OaiXslTemplate
from core_oaipmh_provider_app.views.admin.forms import EditIdentityForm, MetadataFormatForm, \
    EditMetadataFormatForm, TemplateMetadataFormatForm, SetForm, MappingXSLTForm


def check_registry(request):
    """ Check the availability of a registry.
    Args:
        request:

    Returns:

    """
    try:
        http_response = send_get_request(request.GET['url'])
        is_available = http_response.status_code == status.HTTP_200_OK
    except ConnectionError:
        return HttpResponseBadRequest(
            "Connection error while checking availability",
            content_type='application/javascript'
        )
    except Exception, e:
        return HttpResponseBadRequest(e.message, content_type='application/javascript')

    return HttpResponse(json.dumps({'is_available': is_available}), content_type='application/javascript')


class EditIdentityView(EditObjectModalView):
    form_class = EditIdentityForm
    model = OaiSettings
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_identity")
    success_message = 'Data provider edited with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_settings_api.upsert(self.object)
        except Exception, e:
            form.add_error(None, e.message)


class AddMetadataFormatView(AddObjectModalView):
    form_class = MetadataFormatForm
    model = OaiProviderMetadataFormat
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_metadata_formats")
    success_message = 'Metadata Format created with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_provider_metadata_format_api.add_metadata_format(self.object.metadata_prefix,
                                                                 self.object.schema)
        except Exception, e:
            form.add_error(None, e.message)


class DeleteMetadataFormatView(DeleteObjectModalView):
    model = OaiProviderMetadataFormat
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_metadata_formats")
    success_message = 'Metadata Format deleted with success.'
    field_for_name = 'metadata_prefix'

    def _delete(self, request, *args, **kwargs):
        # Delete treatment.
        oai_provider_metadata_format_api.delete(self.object)


class EditMetadataFormatView(EditObjectModalView):
    form_class = EditMetadataFormatForm
    model = OaiProviderMetadataFormat
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_metadata_formats")
    success_message = 'Metadata Format edited with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_provider_metadata_format_api.upsert(self.object)
        except NotUniqueError:
            form.add_error(None, "A Metadata Format with the same prefix already exists. Please "
                                 "choose another prefix.")
        except Exception, e:
            form.add_error(None, e.message)


class AddTemplateMetadataFormatView(AddObjectModalView):
    form_class = TemplateMetadataFormatForm
    model = OaiProviderMetadataFormat
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_metadata_formats")
    success_message = 'Template Metadata Format created with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_provider_metadata_format_api.\
                add_template_metadata_format(self.object.metadata_prefix, self.object.template.id)
        except Exception, e:
            form.add_error(None, e.message)


class AddSetView(AddObjectModalView):
    form_class = SetForm
    model = OaiProviderSet
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_sets")
    success_message = 'Set created with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_provider_set_api.upsert(self.object)
        except Exception, e:
            form.add_error(None, e.message)


class DeleteSetView(DeleteObjectModalView):
    model = OaiProviderSet
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_sets")
    success_message = 'Set deleted with success.'
    field_for_name = 'set_spec'

    def _delete(self, request, *args, **kwargs):
        # Delete treatment.
        oai_provider_metadata_format_api.delete(self.object)


class EditSetView(EditObjectModalView):
    form_class = SetForm
    model = OaiProviderSet
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_sets")
    success_message = 'Set edited with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_provider_set_api.upsert(self.object)
        except Exception, e:
            form.add_error(None, e.message)

    def get_initial(self):
        initial = super(EditSetView, self).get_initial()
        initial['templates_manager'] = [x.id for x in self.object.templates_manager]

        return initial


class AddTemplateMappingView(AddObjectModalView):
    form_class = MappingXSLTForm
    model = OaiXslTemplate
    success_message = 'Mapping created with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_xsl_template_api.upsert(self.object)
        except Exception, e:
            form.add_error(None, e.message)

    def get_initial(self):
        initial = super(AddTemplateMappingView, self).get_initial()
        initial['oai_metadata_format'] = self.kwargs.pop('oai_metadata_format')

        return initial

    def get_success_url(self):
        return reverse_lazy("admin:core_oaipmh_provider_app_xslt_template_mapping",
                            args=(self.object.oai_metadata_format.id,))


class DeleteTemplateMappingView(DeleteObjectModalView):
    model = OaiXslTemplate
    success_url = reverse_lazy("admin:core_oaipmh_provider_app_sets")
    success_message = 'Mapping deleted with success.'

    def _delete(self, request, *args, **kwargs):
        # Delete treatment.
        oai_xsl_template_api.delete(self.object)

    def get_success_url(self):
        return reverse_lazy("admin:core_oaipmh_provider_app_xslt_template_mapping",
                            args=(self.object.oai_metadata_format.id,))

    def _get_object_name(self):
        return "the mapping using the template {0} and the xslt {1} "\
            .format(self.object.template.display_name, self.object.xslt.name)


class EditTemplateMappingView(EditObjectModalView):
    form_class = MappingXSLTForm
    model = OaiXslTemplate
    success_message = 'Mapping edited with success.'

    def _save(self, form):
        # Save treatment.
        try:
            oai_xsl_template_api.upsert(self.object)
        except Exception, e:
            form.add_error(None, e.message)

    def get_initial(self):
        initial = super(EditTemplateMappingView, self).get_initial()
        initial['xslt'] = self.object.xslt.id
        initial['template'] = self.object.template.id

        return initial

    def get_form_kwargs(self):
        """This method is what injects forms with their keyword
            arguments."""
        # grab the current set of form #kwargs
        kwargs = super(EditTemplateMappingView, self).get_form_kwargs()
        # Update the kwargs
        kwargs['edit_mode'] = True

        return kwargs

    def get_success_url(self):
        return reverse_lazy("admin:core_oaipmh_provider_app_xslt_template_mapping",
                            args=(self.object.oai_metadata_format.id,))
