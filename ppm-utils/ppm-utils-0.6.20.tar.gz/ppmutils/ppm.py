from enum import Enum
import requests
from furl import furl
import json
import re
import os

from django.conf import settings


import logging
logger = logging.getLogger(__name__)


class PPM:
    """
    This class serves mostly to track the PPM project properties across
    studies and consolidate functionality common amongst all services.
    """
    @staticmethod
    def fhir_url():
        if hasattr(settings, 'FHIR_URL'):
            return settings.FHIR_URL

        elif os.environ.get('FHIR_URL'):
            return os.environ.get('FHIR_URL')

        # Search environment
        for key, value in os.environ.items():
            if '_FHIR_URL' in key:
                logger.debug('Found FHIR_URL in key: {}'.format(key))

                return value

        raise ValueError('FHIR_URL not defined in settings or in environment')

    @staticmethod
    def is_tester(email):
        '''
        Checks test user email patterns and returns True if a user's email
        matches.
        :param email: The user's email address
        :return: bool
        '''
        if hasattr(settings, 'TEST_EMAIL_PATTERNS') and type(getattr(settings, 'TEST_EMAIL_PATTERNS')) is str:
            testers = settings.TEST_EMAIL_PATTERNS.split(',')
        elif hasattr(settings, 'TEST_EMAIL_PATTERNS') and type(getattr(settings, 'TEST_EMAIL_PATTERNS')) is list:
            testers = settings.TEST_EMAIL_PATTERNS
        else:
            return False

        # Iterate through all patterns
        for pattern in testers:
            if re.match(pattern, email):
                return True

        return False

    class Study(Enum):
        NEER = 'neer'
        ASD = 'autism'

        @staticmethod
        def fhir_id(study):
            """
            Return the FHIR identifier for the passed study
            :return: A PPM study identifier
            :rtype: str
            """
            return 'ppm-{}'.format(PPM.Study.get(study).value)

        @staticmethod
        def identifiers():
            """
            Return a list of all PPM study identifiers to be used in FHIR resources
            :return: A list of PPM study identifiers
            :rtype: list
            """
            return [PPM.Study.fhir_id(study) for study in PPM.Study]

        @staticmethod
        def is_ppm(identifier):
            """
            Returns whether a study identifier is a PPM one or not
            :param identifier: The study identifier
            :type identifier: str
            :return: Whether it's a PPM study or not
            :rtype: bool
            """
            return identifier.lower() in PPM.Study.identifiers()

        @classmethod
        def enum(cls, enum):
            """Accepts any form of an enum and returns the enum"""
            for item in cls:
                if enum is item or enum == item.name or enum == item.value or \
                        enum == cls.title(item) or enum == cls.fhir_id(item):
                    return item

            # Check edge case
            if enum == 'ppm-asd' or enum == 'asd':
                # An edge case from change in study naming
                logger.warning('PPM.Study deprecated study identifier used: "{}"'.format(enum))
                return PPM.Study.ASD

            raise ValueError('Value "{}" is not a valid {}'.format(enum, cls.__name__))

        @classmethod
        def get(cls, enum):
            """
            Returns an instance of the Study enum for the given study value, enum, whatever
            :param enum: The study value string, name or enum
            :type enum: Object
            :return: The instance of PPM Study enum
            :rtype: PPM.Study
            """
            return cls.enum(enum)

        @staticmethod
        def from_value(study):
            """
            Returns an instance of the Study enum for the given study value
            :param study: The study value string
            :type study: str
            :return: The instance of PPM Study enum
            :rtype: PPM.Study
            """
            return PPM.Study.get(study)

        @classmethod
        def title(cls, study):
            """
            Returns the title to be used for the given study.
            :param study: The study identifier or value
            :type study: object
            :return: The title for the study
            :rtype: str
            """
            return dict(PPM.Study.choices())[PPM.Study.get(study).value]

        @classmethod
        def choices(cls):
            """
            Returns a choices tuple of tuples. Define enum titles if different from names/values
            here as this is the source for pulling enum titles.
            :return: ((str, str), )
            """
            return (
                (PPM.Study.NEER.value, 'NEER'),
                (PPM.Study.ASD.value, 'Autism'),
            )

    # Alias Project as Study until we migrate all usages to Study
    Project = Study

    # Set the appropriate participant statuses
    class Enrollment(Enum):
        Registered = 'registered'
        Consented = 'consented'
        Proposed = 'proposed'
        Accepted = 'accepted'
        Completed = 'completed'
        Pending = 'pending'
        Ineligible = 'ineligible'
        Terminated = 'terminated'

        @classmethod
        def enum(cls, enum):
            """Accepts any form of an enum and returns the enum"""
            for item in cls:
                if enum is item or enum == item.name or enum == item.value or enum == cls.title(item):
                    return item

            raise ValueError('Value "{}" is not a valid {}'.format(enum, cls.__name__))

        @classmethod
        def get(cls, enum):
            """Accepts any form of an enrollment and returns the enum"""
            return cls.enum(enum)

        @classmethod
        def choices(cls):
            return (
                (PPM.Enrollment.Registered.value, 'Registered'),
                (PPM.Enrollment.Consented.value, 'Consented'),
                (PPM.Enrollment.Proposed.value, 'Proposed'),
                (PPM.Enrollment.Pending.value, 'Pending'),
                (PPM.Enrollment.Accepted.value, 'Accepted'),
                (PPM.Enrollment.Ineligible.value, 'Queue'),
                (PPM.Enrollment.Completed.value, 'Completed'),
                (PPM.Enrollment.Terminated.value, 'Terminated'),
            )

        @classmethod
        def active_choices(cls):
            return (choice for choice in PPM.Enrollment.choices() if PPM.Enrollment.is_active(choice[0]))

        @classmethod
        def title(cls, enrollment):
            """Returns the value to be used as the enrollment's title"""
            return dict(PPM.Enrollment.choices())[PPM.Enrollment.get(enrollment).value]

        @staticmethod
        def is_active(enrollment):
            """
            Accepts an enrollment and returns whether it is considered 'active' or not. This
            will determine how this flag is set on participant records. The state of being
            active generally means this participant is in the enrollment procedure and is
            still considered for acceptance, or if already accepted, should receive notifications,
            requests, and any other communications concerning the study.
            :param enrollment: The enrollment to consider
            :return: boolean
            """
            enrollment = PPM.Enrollment.get(enrollment)

            # Set these here
            return enrollment not in [PPM.Enrollment.Ineligible, PPM.Enrollment.Terminated, PPM.Enrollment.Completed]

        @classmethod
        def notification_for_enrollment(cls, enrollment):
            """Returns the identifier of a communication to be sent out when this enrollment is set"""
            # Branch
            enrollment = PPM.Enrollment.enum(enrollment)
            if enrollment is PPM.Enrollment.Pending:
                return PPM.Communication.ParticipantPending
            elif enrollment is PPM.Enrollment.Ineligible:
                return PPM.Communication.ParticipantIneligible
            elif enrollment is PPM.Enrollment.Accepted:
                return PPM.Communication.ParticipantAccepted

            return None

    class Communication(Enum):
        ParticipantProposed = 'participant-proposed'
        ParticipantPending = 'participant-pending'
        ParticipantIneligible = 'participant-ineligible'
        ParticipantAccepted = 'participant-accepted'
        PicnicHealthRegistration = 'picnichealth-registration'

        @classmethod
        def enum(cls, enum):
            """Accepts any form of an enum and returns the enum"""
            for item in cls:
                if enum is item or enum == item.name or enum == item.value or enum == cls.title(item):
                    return item

            raise ValueError('Value "{}" is not a valid {}'.format(enum, cls.__name__))

        @classmethod
        def get(cls, enum):
            """Accepts any form of an communication and returns the enum"""
            return cls.enum(enum)

        @classmethod
        def choices(cls):
            return (
                (PPM.Communication.ParticipantProposed.value, 'Participant Proposed'),
                (PPM.Communication.ParticipantPending.value, 'Participant Pending'),
                (PPM.Communication.ParticipantIneligible.value, 'Participant Queued'),
                (PPM.Communication.ParticipantAccepted.value, 'Participant Accepted'),
                (PPM.Communication.PicnicHealthRegistration.value, 'PicnicHealth Registration'),
            )

        @classmethod
        def title(cls, communication):
            """Returns the value to be used as the communication's title"""
            return dict(PPM.Communication.choices())[PPM.Communication.get(communication).value]

    class Questionnaire(Enum):
        ASDGuardianConsentQuestionnaire = 'ppm-asd-consent-guardian-quiz'
        ASDIndividualConsentQuestionnaire = 'ppm-asd-consent-individual-quiz'
        NEERQuestionnaire = 'ppm-neer-registration-questionnaire'
        ASDQuestionnaire = 'ppm-asd-questionnaire'

        @staticmethod
        def questionnaire_for_project(study):
            if PPM.Study.get(study) is PPM.Study.ASD:
                return PPM.Questionnaire.ASDQuestionnaire.value

            elif PPM.Study.get(study) is PPM.Study.NEER:
                return PPM.Questionnaire.NEERQuestionnaire.value

        @staticmethod
        def questionnaire_for_consent(composition):
            if composition.get('type', '').lower() == 'guardian':
                return PPM.Questionnaire.ASDGuardianConsentQuestionnaire.value

            else:
                return PPM.Questionnaire.ASDIndividualConsentQuestionnaire.value

    class Provider(Enum):
        PPM = 'ppmfhir'
        Fitbit = 'fitbit'
        Twitter = 'twitter'
        Facebook = 'facebook'
        Gencove = 'gencove'
        uBiome = 'ubiome'
        PicnicHealth = 'picnichealth'
        Broad = 'broad'
        SMART = 'smart'
        File = 'file'

        @classmethod
        def enum(cls, enum):
            """Accepts any form of an enum and returns the enum"""
            for item in cls:
                if enum is item or enum == item.name or enum == item.value or enum == cls.title(item):
                    return item

            raise ValueError('Value "{}" is not a valid {}'.format(enum, cls.__name__))

        @classmethod
        def get(cls, enum):
            """Accepts any form of an provider and returns the enum"""
            return cls.enum(enum)

        @classmethod
        def choices(cls):
            return (
                (PPM.Provider.PPM.value, 'PPM FHIR'),
                (PPM.Provider.Fitbit.value, 'Fitbit'),
                (PPM.Provider.Twitter.value, 'Twitter'),
                (PPM.Provider.Facebook.value, 'Facebook'),
                (PPM.Provider.Gencove.value, 'Gencove'),
                (PPM.Provider.uBiome.value, 'uBiome'),
                (PPM.Provider.Broad.value, 'Broad'),
                (PPM.Provider.PicnicHealth.value, 'PicnicHealth'),
                (PPM.Provider.SMART.value, 'SMART on FHIR'),
                (PPM.Provider.File.value, 'PPM Files'),
            )

        @classmethod
        def title(cls, provider):
            """Returns the value to be used as the provider's title"""
            return dict(PPM.Provider.choices())[PPM.Provider.get(provider).value]

    class TrackedItem(Enum):
        Fitbit = 'fitbit'
        SalivaSampleKit = 'spitkit'
        uBiomeFecalSampleKit = 'ubiome'
        BloodSampleKit = 'blood'

        @classmethod
        def enum(cls, enum):
            """Accepts any form of an enum and returns the enum"""
            for item in cls:
                if enum is item or enum == item.name or enum == item.value or enum == cls.title(item):
                    return item

            raise ValueError('Value "{}" is not a valid {}'.format(enum, cls.__name__))

        @classmethod
        def get(cls, enum):
            """Accepts any form of an tracked item and returns the enum"""
            return cls.enum(enum)

        @classmethod
        def choices(cls):
            return (
                (PPM.TrackedItem.Fitbit.value, 'FitBit'),
                (PPM.TrackedItem.SalivaSampleKit.value, 'Saliva Kit'),
                (PPM.TrackedItem.uBiomeFecalSampleKit.value, 'uBiome'),
                (PPM.TrackedItem.BloodSampleKit.value, 'Blood Sample'),
            )

        @classmethod
        def title(cls, tracked_item):
            """
            Returns the title for the given tracked item/device
            :param tracked_item: The item code/ID
            :type tracked_item: str
            :return: The item's title
            :rtype: str
            """
            return dict(PPM.TrackedItem.choices())[PPM.TrackedItem.get(tracked_item).value]

        @staticmethod
        def devices(study=None):
            """
            Returns the device item codes for every project in PPM
            :param study: The study for which the devices should be returned
            :return: A list of device codes
            :rtype: list
            """
            devices = {
                PPM.Study.NEER.value: [PPM.TrackedItem.Fitbit.value,
                                       PPM.TrackedItem.uBiomeFecalSampleKit.value,
                                       PPM.TrackedItem.BloodSampleKit.value],

                PPM.Study.ASD.value: [PPM.TrackedItem.Fitbit.value,
                                      PPM.TrackedItem.SalivaSampleKit.value]
            }

            return devices[study] if study else devices

    # Alias Device to TrackedItem
    Device = TrackedItem

    class Service(object):

        # Subclasses set this to direct requests
        service = None

        # Set some auth header properties
        jwt_cookie_name = 'DBMI_JWT'
        jwt_authorization_prefix = 'JWT'
        token_authorization_prefix = 'Token'

        @classmethod
        def _build_url(cls, path):

            # Build the url, chancing on doubling up a slash or two.
            url = furl(cls.service_url() + '/' + path)

            # Filter empty segments (double slashes in path)
            segments = [segment for index, segment in enumerate(url.path.segments)
                        if segment != '' or index == len(url.path.segments) - 1]

            # Log the filter
            if len(segments) < len(url.path.segments):
                logger.debug('Path filtered: /{} -> /{}'.format('/'.join(url.path.segments), '/'.join(segments)))

            # Set it
            url.path.segments = segments

            return url.url

        @classmethod
        def service_url(cls):

            # Check variations of names
            names = ['###_URL', 'DBMI_###_URL', '###_API_URL', '###_BASE_URL']
            for name in names:
                if hasattr(settings, name.replace('###', cls.service.upper())):
                    service_url = getattr(settings, name.replace('###', cls.service.upper()))

                    # We want only the domain and no paths, as those should be specified in the calls
                    # so strip any included paths and queries and return
                    url = furl(service_url)
                    url.path.segments.clear()
                    url.query.params.clear()

                    return url.url

            # Check for a default
            environment = os.environ.get('DBMI_ENV')
            if environment and cls.default_url_for_env(environment):
                return cls.default_url_for_env(environment)

            raise ValueError('Service URL not defined in settings'.format(cls.service.upper()))

        @classmethod
        def default_url_for_env(cls, environment):
            """
            Give implementing classes an opportunity to list a default set of URLs based on the DBMI_ENV,
            if specified. Otherwise, return nothing
            :param environment: The DBMI_ENV string
            :return: A URL, if any
            """
            logger.warning(f'Class PPM does not return a default URL for environment: {environment}')
            return None

        @classmethod
        def headers(cls, request=None, content_type='application/json'):
            """
            Builds request headers. If no request is passed, service is assumed to use a pre-defined
            token in settings as `[SERVICE_NAME]_AUTH_TOKEN`
            :param request: The current request, if any
            :param content_type: The request content type, defaults to JSON
            :return: dict
            """
            if request and cls.get_jwt(request):

                # Use JWT
                return {"Authorization": '{} {}'.format(cls.jwt_authorization_prefix, cls.get_jwt(request)),
                        'Content-Type': content_type}

            elif hasattr(settings, '{}_AUTH_TOKEN'.format(cls.service.upper())):

                # Get token
                token = getattr(settings, '{}_AUTH_TOKEN'.format(cls.service.upper()))

                # Check for specified prefix
                prefix = getattr(settings, '{}_AUTH_PREFIX'.format(cls.service.upper()), cls.token_authorization_prefix)

                # Use token
                return {"Authorization": '{} {}'.format(prefix, token),
                        'Content-Type': content_type}

            raise SystemError('No request with JWT, or no token specified for service "{}", '
                              'cannot build request headers'.format(cls.service))

        @classmethod
        def get_jwt(cls, request):

            # Get the JWT token depending on request type
            if hasattr(request, 'COOKIES') and request.COOKIES.get(cls.jwt_cookie_name):
                return request.COOKIES.get(cls.jwt_cookie_name)

            # Check if JWT in HTTP Authorization header
            elif hasattr(request, 'META') and request.META.get('HTTP_AUTHORIZATION') \
                    and cls.jwt_authorization_prefix in request.META.get('HTTP_AUTHORIZATION'):

                # Remove prefix and return the token
                return request.META.get('HTTP_AUTHORIZATION') \
                    .replace('{} '.format(cls.jwt_authorization_prefix), '')

            return None

        @classmethod
        def head(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.head(
                    cls._build_url(path),
                    headers=cls.headers(request),
                    params=data
                )

                # Check response type
                if raw:
                    return response
                else:
                    return response.json()

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'data': data, 'path': path,
                })

            return None

        @classmethod
        def get(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.get(
                    cls._build_url(path),
                    headers=cls.headers(request),
                    params=data
                )

                # Check response type
                if raw:
                    return response
                else:
                    return response.json()

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'data': data, 'path': path,
                })

            return None

        @classmethod
        def post(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.post(
                    cls._build_url(path),
                    headers=cls.headers(request),
                    data=json.dumps(data)
                )

                # Check response type
                if raw:
                    return response
                else:
                    return response.json()

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'data': data, 'path': path,
                })

            return None

        @classmethod
        def put(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.put(
                    cls._build_url(path),
                    headers=cls.headers(request),
                    data=json.dumps(data)
                )

                # Check response type
                if raw:
                    return response
                else:
                    return response.json()

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'data': data, 'path': path,
                })

            return None

        @classmethod
        def patch(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.patch(cls._build_url(path),
                                          headers=cls.headers(request),
                                          data=json.dumps(data))

                # Check response type
                if raw:
                    return response
                else:
                    return response.ok

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'data': data, 'path': path,
                })

            return False

        @classmethod
        def delete(cls, request=None, path='/', data=None, raw=False):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param raw: How the response should be returned
            :return: object
            """
            logger.debug('Path: {}'.format(path))

            # Check for params
            if not data:
                data = {}

            try:
                # Prepare the request.
                response = requests.delete(cls._build_url(path),
                                           headers=cls.headers(request),
                                           data=json.dumps(data))

                # Check response type
                if raw:
                    return response
                else:
                    return response.ok

            except Exception as e:
                logger.exception('{} error: {}'.format(cls.service, e), exc_info=True, extra={
                    'path': path,
                })

            return False

        @classmethod
        def request(cls, verb, request=None, path='/', data=None, check=True):
            """
            Runs the appropriate REST operation. Request is required for JWT auth,
            not required for token auth.
            :param verb: The RESTful operation to be performed
            :param request: The current Django request
            :param path: The path of the request
            :param data: Request data or params
            :param check: Check the response and raise exception if faulty
            :return: object
            """
            logger.debug('{} -> Path: {}'.format(verb.upper(), path))

            # Check for params
            if not data:
                data = {}

            # Track response for error reporting
            response = None
            try:
                # Build arguments
                args = [cls._build_url(path)]
                kwargs = {'headers': cls.headers(request)}

                # Check how data should be passed
                if verb.lower() in ['get', 'head']:
                    # Pass dict along
                    kwargs['params'] = data
                else:
                    # Format as JSON string
                    kwargs['data'] = json.dumps(data)

                # Prepare the request.
                response = getattr(requests, verb)(*args, **kwargs)

                # See if we should check the response
                if check:
                    response.raise_for_status()

                # Return
                return response

            except Exception as e:
                logger.exception('{} {} error: {}'.format(cls.service, verb.upper(), e), exc_info=True, extra={
                    'path': path, 'verb': verb, 'data': data, 'response': response
                })

            return False
