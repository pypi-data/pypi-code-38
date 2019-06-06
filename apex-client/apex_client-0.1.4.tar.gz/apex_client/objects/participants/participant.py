from typing import Optional

from apex_client.objects import ApexObject

from .company import Company


class Participant(ApexObject):
    valid_properties = ['id', 'uuid', 'first_name', 'last_name', 'full_name', 'email', 'is_active', 'company_name',
                        'gender']
    date_properties = ['date_created', 'date_modified', 'deletion_date']

    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.company = None

        if 'company' in json_data and json_data['company']:
            self.company = Company(json_data['company'])

    @classmethod
    def get(cls, participant_id: int) -> Optional['Participant']:
        return Participant._get(f'participants/{participant_id}/')

    def __str__(self):
        return f"{self.full_name} ({self.email})"
