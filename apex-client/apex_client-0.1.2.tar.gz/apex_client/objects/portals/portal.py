from typing import Optional

from apex_client.objects import ApexObject
from apex_client.objects.participants import Company
from apex_client.request import ApexRequest


class Portal(ApexObject):
    valid_properties = ['id', 'uuid', 'name', 'url', 'type', 'styles', 'logo', 'bookable', 'company_name', 'events']
    date_properties = ['date_created', 'date_modified']

    def __init__(self, json_data: dict):
        super().__init__(json_data)
        self.areas = []
        self.portal_events = []

        if 'company' in json_data.keys():
            if isinstance(json_data['company'], dict):
                self.company_object = Company(json_data['company'])
                self.company_id = self.company_object.id
            else:
                self.company_object = None
                self.company_id = json_data['company']

    @classmethod
    def get(cls, portal_id: int) -> Optional['Portal']:
        return Portal._get(f'portals/{portal_id}/')

    @classmethod
    def search(cls, name: str = None) -> Optional[list]:
        params = None

        if name:
            params.update({
                "name": name
            })

        return ApexRequest.search_all('portals/', params)

    @property
    def company(self):
        if not self.company_object and self.company_id:
            self.company_object = Company.get(self.company_id)

        return self.company_object

    def __str__(self):
        return self.name

    def get_portal_events(self, reload: bool = False) -> list:
        from .portal_event import PortalEvent

        if not self.portal_events or reload:
            self.portal_events = []
            portal_events = ApexRequest.search_all(f'portals/{self.id}/events/')

            if portal_events is not None:
                for portal_event in portal_events:
                    self.portal_events.append(PortalEvent(portal_event))

        return self.portal_events

    def get_areas(self, reload: bool = False) -> list:
        from apex_client.objects.events import Area

        if not self.areas or reload:
            self.areas = []

            areas = ApexRequest.search_all(f'websites/{self.id}/areas/', {'limit': None})

            if areas is not None:
                for area in areas:
                    self.areas.append(Area(area))

        return self.areas
