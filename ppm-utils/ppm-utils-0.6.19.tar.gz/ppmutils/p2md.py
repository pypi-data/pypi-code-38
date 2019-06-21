import os
from enum import Enum
from furl import furl

from ppmutils.ppm import PPM
from ppmutils.fhir import FHIR

import logging
logger = logging.getLogger(__name__)


class P2MD(PPM.Service):

    service = 'P2MD'

    # This is the system prefix used for coding DocumentReferences created by P2MD
    system = 'https://peoplepoweredmedicine.org/document-type'

    # Set identifier systems
    p2md_identifier_system = 'https://peoplepoweredmedicine.org/fhir/p2md/operation'
    fileservice_identifier_system = 'https://peoplepoweredmedicine.org/fhir/fileservice/file'

    class ExportProviders(Enum):
        Participant = "ppm-participant"
        i2b2 = "ppm-i2b2"
        JSON = "ppm-json"
        FHIR = "ppm-fhir"

    @classmethod
    def default_url_for_env(cls, environment):
        """
        Give implementing classes an opportunity to list a default set of URLs based on the DBMI_ENV,
        if specified. Otherwise, return nothing
        :param environment: The DBMI_ENV string
        :return: A URL, if any
        """
        if 'local' in environment:
            return 'http://p2md:8020'
        elif 'dev' in environment:
            return 'https://p2m2.aws.dbmi-dev.hms.harvard.edu'
        elif 'prod' in environment:
            return 'https://p2m2.dbmi.hms.harvard.edu'
        else:
            logger.error(f'Could not return a default URL for environment: {environment}')

        return None

    @classmethod
    def get_auth_link(cls, request, provider, ppm_id, return_url):
        """
        Builds and returns the link that should be followed for the user to authorize PPM with
        the provided data source.
        :param request: The original Django request
        :param provider: The desired data provider (eg Fitbit, Facebook, etc)
        :param ppm_id: The PPM ID of the current user
        :param return_url: The URL to send the user post authorization
        :return: The auth URL
        """

        # Build the base auth URL

        # Build the URL
        url = furl(P2MD._build_url(f'/sources/{provider}/auth/{ppm_id}'))

        # Add the return URL
        url.query.params.add('return_url', return_url)

        # Add the operation name
        url.query.params.add('task', 'authorize_{}'.format(provider))

        # Patch for local
        if os.environ.get('DBMI_ENV') == 'local':
            url.set(host='localhost')

        return url.url

    @classmethod
    def get_smart_auth_link(cls, request, provider, ppm_id, return_url):
        """
        Builds and returns the link that should be followed for the user to authorize PPM with
        the provided SMART data source.
        :param request: The original Django request
        :param provider: The desired SMART data provider (eg s4s, epicsandbox, etc)
        :param ppm_id: The PPM ID of the current user
        :param return_url: The URL to send the user post authorization
        :return: The auth URL
        """

        # Build the base auth URL

        # Build the URL
        url = furl(P2MD._build_url(f'/sources/smart/{provider}/auth/{ppm_id}'))

        # Add the return URL
        url.query.params.add('return_url', return_url)

        # Add the operation name
        url.query.params.add('task', 'authorize_smart_{}'.format(provider))

        # Patch for local
        if os.environ.get('DBMI_ENV') == 'local':
            url.set(host='localhost')

        return url.url

    @classmethod
    def get_authorizations(cls, request, ppm_ids):
        """
        Make a request to P2MD to determine what providers all participants have authorized.
        """
        return cls.get(request, '/sources/api/auths', {'ppm_ids': ','.join(ppm_ids)})

    @classmethod
    def has_fitbit_authorization(cls, request, ppm_id):
        """
        Make a request to P2MD to determine if a participant has authorized Fitbit.
        """
        # Return True if no errors
        response = cls.head(request, f'/sources/api/fitbit/{ppm_id}', raw=True)

        return response.ok

    @classmethod
    def has_facebook_authorization(cls, request, ppm_id):
        """
        Make a request to P2MD to determine if a participant has authorized Facebook.
        """
        # Return True if no errors
        response = cls.head(request, f'/sources/api/facebook/{ppm_id}', raw=True)

        return response.ok

    @classmethod
    def has_smart_authorization(cls, request, ppm_id):
        """
        Make a request to P2MD to determine if a participant has authorized any SMART provider.
        """
        # Return True if no errors
        response = cls.head(request, f'/sources/api/smart/-/{ppm_id}', raw=True)

        return response.ok

    @classmethod
    def get_smart_authorizations(cls, request, ppm_id):
        """
        Make a request to P2MD to get a list of SMART providers authorized by the participant.
        """
        # Make the request
        data = P2MD.get_authorizations(request, [ppm_id])

        # Get list of providers
        auths = next(p['authorizations'] for p in data if p['ppm_id'] == ppm_id)

        # Get list of SMART providers and filter the user's auths list
        smart_providers = [p['provider'] for p in P2MD.get_smart_endpoints(request)['smart_endpoints']]

        return [auth for auth in auths if auth in smart_providers]

    @classmethod
    def get_operations(cls, request, ppm_id):
        """
        Make a request to P2MD to get a full history of all data operations conducted
        for the participant.
        """
        return cls.get(request, f'/sources/api/ppm/{ppm_id}')

    @classmethod
    def get_twitter_data(cls, request, ppm_id, handle):
        """
        Make a request to P2MD to fetch Twitter data and store it in PPM.
        """
        response = cls.post(request, f'/sources/api/twitter/{ppm_id}', {'handle': handle}, raw=True)

        # Return True if no errors
        return response.ok

    @classmethod
    def download_twitter_data(cls, request, ppm_id):
        """
        Downloads the Twitter dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :return: The requested dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/twitter/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def get_fitbit_data(cls, request, ppm_id):
        """
        Make a request to P2MD to fetch Fitbit data and store it in PPM.
        """
        response = cls.post(request, f'/sources/api/fitbit/{ppm_id}', data={}, raw=True)

        # Return True if no errors
        return response.ok

    @classmethod
    def download_fitbit_data(cls, request, ppm_id):
        """
        Downloads the Fitbit dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :return: The requested dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/fitbit/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def get_gencove_data(cls, request, ppm_id, gencove_id):
        """
        Make a request to P2MD to fetch Gencove data and store it in PPM.
        """
        response = cls.post(request, f'/sources/api/gencove/{ppm_id}', data={'gencove_id': gencove_id}, raw=True)

        # Return True if no errors
        return response.ok

    @classmethod
    def download_gencove_data(cls, request, ppm_id):
        """
        Downloads the Gencove dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :return: The requested dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/gencove/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def get_facebook_data(cls, request, ppm_id):
        """
        Make a request to P2MD to fetch Facebook data and store it in PPM.
        """
        response = cls.post(request, f'/sources/api/facebook/{ppm_id}', data={}, raw=True)

        # Return True if no errors
        return response.ok

    @classmethod
    def download_facebook_data(cls, request, ppm_id):
        """
        Downloads the Facebook dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :return: The requested dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/facebook/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def get_smart_data(cls, request, ppm_id, provider):
        """
        Make a request to P2MD to fetch SMART on FHIR EHR data and store it in PPM.
        """
        response = cls.post(request, f'/sources/api/smart/{provider}/{ppm_id}', data={}, raw=True)

        # Return True if no errors
        return response.ok

    @classmethod
    def download_smart_data(cls, request, ppm_id, provider):
        """
        Downloads the SMART dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param provider: The SMART provider
        :return: The requested entire dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/smart/{provider}/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def get_files(cls, request, ppm_id):
        """
        Queries P2MD for all uploaded files related to this participant.
        """
        return cls.get(request, f'/sources/api/file/{ppm_id}')

    @classmethod
    def create_file(cls, request, study, ppm_id, document_type, filename, metadata=None, tags=None, content_type='application/octect-stream'):
        """
        Make a request to P2MD to create a file upload
        """
        # Set data
        data = {'study': study, 'type': document_type, 'filename': filename}

        # Add metadata and tags if passed
        if metadata:
            data['metadata'] = metadata

        if tags:
            data['tags'] = tags

        if content_type:
            data['content_type'] = content_type

        # Get the file data
        upload = cls.post(request, f'/sources/api/file/{ppm_id}', data)

        # Get the UUID
        uuid = upload.get('uuid')

        # Return True if no errors
        return uuid, upload

    @classmethod
    def uploaded_file(cls, request, study, ppm_id, document_type, uuid, location, content_type='application/octect-stream'):
        """
        Make a request to P2MD to create a file upload
        """
        # Set data
        data = {'study': study, 'uuid': uuid, 'location': location, 'type': document_type, 'content_type': content_type}

        # Return True if no errors
        return cls.patch(request, f'/sources/api/file/{ppm_id}', data)

    @classmethod
    def get_smart_endpoints(cls, request=None):
        """
        Return a list of all registered SMART endpoints
        :param request: The current HttpRequest
        :return: list
        """
        return cls.get(request, '/sources/api/smart/provider')

    @classmethod
    def get_smart_endpoint_urls(cls, request, ppm_id, return_url):
        """
        Return a list of all registered SMART endpoints with auth links for the current user
        :param request: The current HttpRequest
        :param ppm_id: The current user's PPM ID
        :param return_url: The URL to return to post authentication
        :return: list
        """
        smart_endpoints = P2MD.get_smart_endpoints(request)

        # Collect formatted endpoints
        endpoints = []

        # Endpoints
        for endpoint in smart_endpoints.get('smart_endpoints', []):

            # Get required properties
            organization = endpoint.get('organization')
            provider = endpoint.get('provider')
            if not organization or not provider:
                logger.error('Missing properties for SMART endpoint: {} - {}'.format(organization, provider))
                continue

            # Build the URL
            url = P2MD.get_smart_auth_link(request, provider, ppm_id, return_url)

            # Add it
            endpoints.append({'organization': organization, 'url': url})

        return endpoints

    @classmethod
    def get_providers(cls, request=None):
        """
        Return a list of all registered data providers' codes and titles
        :param request: The current HttpRequest
        :return: list
        """
        return cls.get(request, f'/sources/api/provider')

    @classmethod
    def get_file_types(cls, request=None):
        """
        Return a list of all registered data providers' codes and titles
        :param request: The current HttpRequest
        :return: list
        """
        return cls.get(request, f'/sources/api/file/type')

    @classmethod
    def get_participant_data_url(cls, ppm_id, filename=None, providers=None):
        """
        Downloads the PPM dataset for the passed user
        :param ppm_id: The PPM ID of the requesting user
        :param filename: What the resulting archive should be called
        :param providers: A list of providers to limit data included to
        :return: The user's entire dataset
        """
        # Build the URL
        url = furl(P2MD._build_url(f'/sources/api/ppm/{ppm_id}/archive/'))

        # If providers, include them in query
        if providers:
            url.query.params.add('providers', ','.join(providers))

        # Add the return URL
        if filename:
            url.query.params.add('filename', filename)

        # Patch for local
        if os.environ.get('DBMI_ENV') == 'local':
            url.set(host='localhost')

        return url.url

    @classmethod
    def download_participant_data(cls, request, ppm_id, filename=None, providers=None):
        """
        Downloads the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param filename: What the resulting archive should be called
        :param providers: A list of providers to limit data included to
        :return: The user's entire dataset
        """
        # Build the URL
        url = furl(P2MD.get_participant_data_url(ppm_id=ppm_id,
                                                 filename=filename,
                                                 providers=providers))

        # Make the request
        response = cls.get(request=request, path=url.pathstr, data=url.querystr, raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def export_content_type(cls, provider=ExportProviders.Participant):
        """
        Returns the content type and extension for the passed export provider. Use this method
        to prepare a response when passing through a Fileservice document.
        :param provider: ExportProvider
        :return: str, str
        """
        if provider is cls.ExportProviders.Participant:
            return "application/zip", "zip"

        else:
            return "application/json", "json"

    @classmethod
    def get_data_document_references(cls, ppm_id, provider=None):
        """
        Queries the current user's FHIR record for any DocumentReferences related to this type
        :return: A list of DocumentReferences
        :rtype: list
        """
        # Gather data-related DocumentReferences
        document_references = FHIR.query_data_document_references(patient=ppm_id, provider=provider)
        logger.debug(f'{ppm_id}: Found {len(document_references)} DocumentReferences for: {provider}')

        # Flatten resources and pick out relevant identifiers
        flats = []
        for document_reference in document_references:

            # Flatten it
            flat = FHIR.flatten_document_reference(document_reference['resource'])

            # Pick out P2MD and Fileservice identifiers
            if P2MD.p2md_identifier_system in flat:
                flat['p2md_id'] = flat[P2MD.p2md_identifier_system]
                del flat[P2MD.p2md_identifier_system]

            if P2MD.fileservice_identifier_system in flat:
                flat['fileservice_id'] = flat[P2MD.fileservice_identifier_system]
                del flat[P2MD.fileservice_identifier_system]

            elif flat.get('url'):
                # To support older documents, try to parse it from URL
                url = furl(flat['url'])
                flat['fileservice_id'] = url.path.segments.pop(3)

            else:
                # Just make it empty
                flat['fileservice_id'] = 'ERROR'

            flats.append(flat)

        return flats

    @classmethod
    def get_data_document_references_for_providers(cls, ppm_id, providers=None):
        """
        Queries the current user's FHIR record for any DocumentReferences related to the passed types
        :return: A list of DocumentReferences
        :rtype: list
        """
        # Get all flattened data document references
        document_references = []
        for document_reference in P2MD.get_data_document_references(ppm_id, provider=None):

            # Check type and filter out non-requested provider documents
            if not providers or document_reference['type'] not in providers:
                continue

            document_references.append(document_reference)

        logger.debug(f'{ppm_id}: Found {len(document_references)} DocumentReferences for: {", ".join(providers)}')
        return document_references

    #
    # Deprecated
    #


    @classmethod
    def check_export(cls, request, ppm_id, provider=ExportProviders.Participant, age=24):
        """
        Checks the presence of the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param provider: The provider or format of the exported data
        :param age: Set the number of hours after which the dataset should be considered expired
        :return: The age of the current dataset in hours, if any
        """
        # Make the request
        response = cls.head(request, f'/sources/api/ppm/{provider.value}/{ppm_id}/export', {'age': age}, raw=True)
        if response:
            return response.ok

        return False

    @classmethod
    def get_export_url(cls, request, ppm_id, provider=ExportProviders.Participant):
        """
        Generates the URL to download the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param provider: The provider or format of the exported data
        :return: The user's entire dataset
        """
        url = furl(cls._build_url(f'/sources/api/ppm/{provider.value}/{ppm_id}/export'))

        # Patch for local
        if os.environ.get('DBMI_ENV') == 'local':
            url.set(host='localhost')

        return url.url

    @classmethod
    def download_export(cls, request, ppm_id, provider=ExportProviders.Participant):
        """
        Downloads the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param provider: The provider or format of the exported data
        :return: The user's entire dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/ppm/{provider.value}/{ppm_id}/export', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def download_data(cls, request, ppm_id, provider=ExportProviders.Participant):
        """
        Downloads the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param provider: The provider or format of the exported data
        :return: The user's entire dataset
        """
        # Make the request
        response = cls.get(request, f'/sources/api/ppm/{provider.value}/{ppm_id}/download', raw=True)
        if response:
            return response.content

        return None

    @classmethod
    def download_data_notify(cls, request, ppm_id, recipients, provider=ExportProviders.Participant):
        """
        Downloads the PPM dataset for the passed user
        :param request: The original Django request object
        :param ppm_id: The PPM ID of the requesting user
        :param recipients: The email addresses to which a notification of the data's preparation should be sent
        :param provider: The provider or format of the exported data
        :return: The user's entire dataset
        """
        # Make the request
        response = cls.post(request,
                            path=f'/sources/api/ppm/{provider.value}/{ppm_id}/',
                            data={'recipients': ','.join(recipients)},
                            raw=True)

        return response.ok
