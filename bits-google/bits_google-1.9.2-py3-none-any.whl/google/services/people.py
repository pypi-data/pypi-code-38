"""Google People API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class People(Base):
    """People class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        # build a connection to the people API
        self.people = build('people', 'v1', credentials=credentials)

        # define default list of personFields
        self.person_fields = [
            'addresses',
            'ageRanges',
            'biographies',
            'birthdays',
            'braggingRights',
            'coverPhotos',
            'emailAddresses',
            'events',
            'genders',
            'imClients',
            'interests',
            'locales',
            'memberships',
            'metadata',
            'names',
            'nicknames',
            'occupations',
            'organizations',
            'phoneNumbers',
            'photos',
            'relations',
            'relationshipInterests',
            'relationshipStatuses',
            'residences',
            'sipAddresses',
            'skills',
            'taglines',
            'urls',
            'userDefined',
        ]

    def get_batch(self, resourceNames, personFields):
        """Return a batch of people."""
        params = {
            'resourceNames': resourceNames,
            'personFields': personFields,
        }
        return self.people.people().getBatchGet(**params).execute()

    def get_connections(self):
        """Return connections for the current user."""
        connections = self.people.people().connections()
        params = {
            'resourceName': 'people/me',
            'personFields': 'names,emailAddresses'
        }
        request = connections.list(**params)
        return self.get_list_items(connections, request, 'connections')

    def get_person(self, resourceName, fields=None):
        """Return a person."""
        if not fields:
            fields = self.person_fields
        params = {
            'resourceName': resourceName,
            'personFields': ','.join(fields),
        }
        return self.people.people().get(**params).execute()
