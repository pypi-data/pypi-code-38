import re
from StringIO import StringIO
from datetime import datetime

from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import HttpResponse
from django.views.generic import TemplateView
from rest_framework import status

import core_main_app.components.xsl_transformation.api as xsl_transformation_api
import core_oaipmh_provider_app.commons.exceptions as oai_provider_exceptions
import core_oaipmh_provider_app.components.oai_xsl_template.api as oai_xsl_template_api
from core_main_app.commons import exceptions as exceptions
from core_main_app.components.data import api as data_api
from core_main_app.components.template import api as template_api
from core_main_app.components.version_manager import api as version_manager_api
from core_main_app.components.workspace import api as workspace_api
from core_main_app.utils.xsd_flattener.xsd_flattener_database_url import XSDFlattenerDatabaseOrURL
from core_oaipmh_common_app.utils import UTCdatetime
from core_oaipmh_provider_app import settings
from core_oaipmh_provider_app.commons import status as oai_status
from core_oaipmh_provider_app.components.oai_data import api as oai_data_api
from core_oaipmh_provider_app.components.oai_provider_metadata_format import \
    api as oai_provider_metadata_format_api
from core_oaipmh_provider_app.components.oai_provider_set import api as oai_provider_set_api
from core_oaipmh_provider_app.components.oai_settings import api as oai_settings_api
from core_oaipmh_provider_app.utils import CheckOaiPmhRequest


class OAIProviderView(TemplateView):
    content_type = 'text/xml'

    def __init__(self, **kwargs):
        super(OAIProviderView, self).__init__(**kwargs)
        self.request = None
        self.oai_verb = None
        self.metadata_prefix = None
        self.set = None
        self.From = None
        self.until = None
        self.identifier = None
        self.resumption_token = None

    def render_to_response(self, context, **response_kwargs):
        # All OAI responses should be XML
        if 'content_type' not in response_kwargs:
            response_kwargs['content_type'] = self.content_type
        # Add common context data needed for all responses
        context.update({
            'now': UTCdatetime.datetime_to_utc_datetime_iso8601(datetime.now()),
            'verb': self.oai_verb,
            'identifier': self.identifier if hasattr(self, 'identifier') else None,
            'metadataPrefix': self.metadata_prefix if hasattr(self, 'metadata_prefix') else None,
            'url': self.request.build_absolute_uri(self.request.path),
            'from': self.From if hasattr(self, 'From') else None,
            'until': self.until if hasattr(self, 'until') else None,
            'set': self.set if hasattr(self, 'set') else None,
        })
        # Render the template with the context information
        return super(TemplateView, self) \
            .render_to_response(context, **response_kwargs)

    def error(self, error):
        return self.errors([error])

    def errors(self, errors):
        self.template_name = "core_oaipmh_provider_app/user/xml/error.html"
        return self.render_to_response({
            'errors': errors,
        })

    def get(self, request, *args, **kwargs):
        try:
            # Check if the server is enabled for providing information.
            information = oai_settings_api.get()
            if information and not information.enable_harvesting:
                return HttpResponseNotFound('<h1>OAI-PMH not available for harvesting</h1>')
            # Get verb
            self.oai_verb = request.GET.get('verb', None)
            self.request = request
            # Check if the verb and arguments are illegal.
            CheckOaiPmhRequest.check_bad_argument(self.oai_verb, request.GET)
            # Get arguments.
            self.metadata_prefix = request.GET.get('metadataPrefix', None)
            self.set = request.GET.get('set', None)
            self.From = request.GET.get('from', None)
            self.until = request.GET.get('until', None)
            self.identifier = request.GET.get('identifier', None)
            self.resumption_token = request.GET.get('resumptionToken', None)
            # Verb processing.
            if self.oai_verb == 'Identify':
                return self.identify()
            elif self.oai_verb == 'GetRecord':
                return self.get_record()
            elif self.oai_verb == 'ListSets':
                return self.list_sets()
            elif self.oai_verb == 'ListIdentifiers':
                return self.list_identifiers()
            elif self.oai_verb == 'ListMetadataFormats':
                return self.list_metadata_formats()
            elif self.oai_verb == 'ListRecords':
                return self.list_records()

        except oai_provider_exceptions.OAIExceptions, e:
            return self.errors(e.errors)
        except oai_provider_exceptions.OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse(
                {'content': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def identify(self):
        """ Response to identify request.
        Returns:
            XML type response.

        """
        from core_oaipmh_provider_app import settings
        # Template name
        self.template_name = 'core_oaipmh_provider_app/user/xml/identify.html'
        # Get settings information from database
        information = oai_settings_api.get()
        # Fill the identify response
        identify_data = {
            'name': information.repository_name,
            'protocol_version': settings.OAI_PROTOCOL_VERSION,
            'admins': (email for name, email in settings.OAI_ADMINS),
            'earliest_date': self._get_earliest_date(),
            'deleted': settings.OAI_DELETED_RECORD,
            'granularity': settings.OAI_GRANULARITY,
            'identifier_scheme': settings.OAI_SCHEME,
            'repository_identifier': information.repository_identifier,
            'identifier_delimiter': settings.OAI_DELIMITER,
            'sample_identifier': settings.OAI_SAMPLE_IDENTIFIER
        }

        return self.render_to_response(identify_data)

    def list_sets(self):
        """ Response to ListSets request.
        Returns:
            XML type response.

        """
        self.template_name = 'core_oaipmh_provider_app/user/xml/list_sets.html'
        items = []
        try:
            sets = oai_provider_set_api.get_all("set_spec")
            if len(sets) == 0:
                raise oai_provider_exceptions.NoSetHierarchy
            else:
                for set_ in sets:
                    item_info = {
                        'setSpec': set_.set_spec,
                        'setName':  set_.set_name,
                        'description':  set_.description
                    }
                    items.append(item_info)

            return self.render_to_response({'items': items})
        except oai_provider_exceptions.OAIExceptions, e:
            return self.errors(e.errors)
        except oai_provider_exceptions.OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_metadata_formats(self):
        """ Response to ListMetadataFormats request.
        Returns:
            XML type response.

        """
        try:
            items = []
            self._check_resumption_token_not_implemented()
            self.template_name = 'core_oaipmh_provider_app/user/xml/list_metadata_formats.html'
            # If an identifier is provided, we look for its metadata formats
            if self.identifier is not None:
                record_id = CheckOaiPmhRequest.check_identifier(self.identifier)
                try:
                    record = data_api.get_by_id(record_id, self.request.user)
                    metadata_formats = oai_provider_metadata_format_api.get_all_by_templates([record.template])
                    xslt_metadata_formats = oai_xsl_template_api.get_metadata_formats_by_templates([record.template])
                    metadata_formats = set(metadata_formats).union(xslt_metadata_formats)
                except Exception:
                    raise oai_provider_exceptions.IdDoesNotExist(self.identifier)
            else:
                # No identifier provided. We return all metadata formats available
                metadata_formats = oai_provider_metadata_format_api.get_all()

            if len(metadata_formats) == 0:
                raise oai_provider_exceptions.NoMetadataFormat
            else:
                host_uri = self.request.build_absolute_uri('/')
                for metadata_format in metadata_formats:
                    item_info = {
                        'metadataNamespace': metadata_format.metadata_namespace,
                        'metadataPrefix':  metadata_format.metadata_prefix,
                        'schema':  oai_provider_metadata_format_api.get_metadata_format_schema_url(metadata_format,
                                                                                                   host_uri)
                    }
                    items.append(item_info)

            return self.render_to_response({'items': items})
        except oai_provider_exceptions.OAIExceptions, e:
            return self.errors(e.errors)
        except oai_provider_exceptions.OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list_identifiers(self):
        """ Response to ListIdentifiers request.
        Returns:
            XML type response.

        """
        self.template_name = 'core_oaipmh_provider_app/user/xml/list_identifiers.html'
        return self._treatment_list_items()

    def list_records(self):
        """ Response to ListRecords request.
        Returns:
           XML type response.

        """
        self.template_name = 'core_oaipmh_provider_app/user/xml/list_records.html'
        return self._treatment_list_items(include_metadata=True)

    def _treatment_list_items(self, include_metadata=False):
        """ Response to ListRecords or ListIdentifiers request.
        Returns:
           XML type response.

        """
        try:
            self._check_resumption_token_not_implemented()
            use_raw = True
            # Handle FROM and UNTIL
            from_date = None
            until_date = None
            if self.From:
                from_date = CheckOaiPmhRequest.check_from(self.From)
            if self.until:
                until_date = CheckOaiPmhRequest.check_until(self.until)
            templates_id = self._get_templates_id_by_metadata_prefix(self.metadata_prefix)
            metadata_format = oai_provider_metadata_format_api.get_by_metadata_prefix(self.metadata_prefix)
            if len(templates_id) == 0:
                templates_id = oai_xsl_template_api.get_template_ids_by_metadata_format(metadata_format)
                use_raw = False

            templates_id_from_set = self._get_templates_id_by_set_spec(self.set)
            set(templates_id).intersection(templates_id_from_set)

            items = self._get_items(templates_id, from_date, until_date, metadata_format, include_metadata, use_raw)

            return self.render_to_response({'items': items})
        except oai_provider_exceptions.OAIExceptions, e:
            return self.errors(e.errors)
        except oai_provider_exceptions.OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_record(self):
        """ Response to GetRecord request.
       Returns:
           XML type response.

       """
        try:
            self.template_name = 'core_oaipmh_provider_app/user/xml/get_record.html'
            # Check if the identifier pattern is OK.
            record_id = CheckOaiPmhRequest.check_identifier(self.identifier)
            try:
                oai_data = oai_data_api.get_by_data(record_id)
            except Exception:
                raise oai_provider_exceptions.IdDoesNotExist(self.identifier)

            try:
                metadata_format = oai_provider_metadata_format_api.get_by_metadata_prefix(
                    self.metadata_prefix
                )
                # Check if the record and the given metadata prefix use the same template.
                use_raw = metadata_format.is_template and \
                    oai_data.template == metadata_format.template
                if oai_data.status != oai_status.DELETED:
                    xml = re.sub(r'<\?xml[^?]+\?>', '', oai_data.data.xml_content)

                    if not use_raw:
                        xslt = oai_xsl_template_api.get_by_template_id_and_metadata_format_id(
                            oai_data.template.id, metadata_format.id
                        ).xslt
                        xml = xsl_transformation_api.xsl_transform(xml, xslt.name)
                else:
                    xml = None
            except Exception:
                raise oai_provider_exceptions.CannotDisseminateFormat(self.metadata_prefix)

            record_info = {
                'identifier': self.identifier,
                'last_modified': UTCdatetime.datetime_to_utc_datetime_iso8601(oai_data.oai_date_stamp),
                'sets': oai_provider_set_api.get_all_by_template_ids([oai_data.template.id]),
                'XML': xml,
                'deleted': oai_data.status == oai_status.DELETED
            }

            return self.render_to_response(record_info)
        except oai_provider_exceptions.OAIExceptions, e:
            return self.errors(e.errors)
        except oai_provider_exceptions.OAIException, e:
            return self.error(e)
        except Exception, e:
            return HttpResponse({'content': e.message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _check_resumption_token_not_implemented(self):
        """ Check if a resumption token has been given. Token not implemented yet.
        Raises:
            BadResumptionToken if a token has been given.

        """
        if self.resumption_token is not None:
            raise oai_provider_exceptions.BadResumptionToken(self.resumption_token)

    @staticmethod
    def _get_items(templates_id, from_date, until_date, metadata_format, include_metadata=False,
                   use_raw=True):
        items = []
        for template in templates_id:
            try:
                xslt = None
                if not use_raw:
                    xslt = oai_xsl_template_api.get_by_template_id_and_metadata_format_id(
                        template, metadata_format
                    ).xslt
                oai_data = oai_data_api.get_all_by_template(
                    template, from_date=from_date, until_date=until_date
                )
                for elt in oai_data:
                    # Only data from public workspace.
                    if elt.data.workspace is not None and \
                            workspace_api.is_workspace_public(elt.data.workspace):
                        identifier = '%s:%s:id/%s' % (settings.OAI_SCHEME,
                                                      settings.OAI_REPO_IDENTIFIER,
                                                      str(elt.data_id))
                        item_info = {
                            'identifier': identifier,
                            'last_modified': UTCdatetime.datetime_to_utc_datetime_iso8601(
                                elt.oai_date_stamp
                            ),
                            'sets': oai_provider_set_api.get_all_by_template_ids([template]),
                            'deleted': elt.status == oai_status.DELETED
                        }
                        if include_metadata and elt.status == oai_status.ACTIVE:
                            xml = re.sub(r'<\?xml[^?]+\?>', '', elt.data.xml_content)

                            if not use_raw:
                                xml = xsl_transformation_api.xsl_transform(xml, xslt.name)

                            item_info.update({'XML': xml})

                        items.append(item_info)
            except (exceptions.DoesNotExist, exceptions.XMLError, Exception):
                pass

        # If there is no records
        if len(items) == 0:
            raise oai_provider_exceptions.NoRecordsMatch

        return items

    @staticmethod
    def _get_earliest_date():
        try:
            return UTCdatetime.datetime_to_utc_datetime_iso8601(oai_data_api.get_earliest_data_date())
        except (exceptions.ModelError, Exception):
            return UTCdatetime.datetime_to_utc_datetime_iso8601(datetime.min)

    @staticmethod
    def _get_templates_id_by_metadata_prefix(metadata_prefix):
        try:
            templates_id = []
            metadata_format = oai_provider_metadata_format_api.get_by_metadata_prefix(metadata_prefix)
            if metadata_format.is_template:
                templates_id.append(str(metadata_format.template.id))
            return templates_id
        except Exception:
            raise oai_provider_exceptions.CannotDisseminateFormat(metadata_prefix)

    @staticmethod
    def _get_templates_id_by_set_spec(set_spec):
        try:
            templates_id = []
            if set_spec is not None:
                # Get templates manager
                set_templates_manager = oai_provider_set_api.get_by_set_spec(set_spec).templates_manager
                for set_template_manager in set_templates_manager:
                    # Get all versions
                    templates_id.extend(set_template_manager.versions)

            return templates_id
        except (exceptions.DoesNotExist, exceptions.ModelError, Exception):
            raise oai_provider_exceptions.NoRecordsMatch


def get_xsd(request, title, version_number):
    """ Page that allows to retrieve an XML Schema by its title and version number.
    Args:
        request: Request.
        title: Schema title.
        version_number: Version of the schema.

    Returns:
        Flatten Schema.

    """
    try:
        template_version = version_manager_api.get_active_global_version_manager_by_title(title)
        template = template_api.get(version_manager_api.get_version_by_number(template_version, int(version_number)))
        flatten = XSDFlattenerDatabaseOrURL(template.content.encode('utf-8'))
        content_encoded = flatten.get_flat()
        file_obj = StringIO(content_encoded)

        return HttpResponse(file_obj, content_type='text/xml')
    except (exceptions.DoesNotExist, exceptions.ModelError, Exception):
        return HttpResponseBadRequest('Impossible to retrieve the schema with the given name and version.')
