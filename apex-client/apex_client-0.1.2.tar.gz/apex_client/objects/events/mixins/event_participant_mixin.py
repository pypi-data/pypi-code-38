from apex_client.objects.participants import Company, Participant


class EventParticipantMixin:
    def __init__(self, json_data: dict):
        super().__init__(json_data)

        self.participant_id = json_data['participant']
        self.company_id = json_data['company']

        self.participant_object = None
        self.company_object = None

    @property
    def participant(self):
        if not self.participant_object and self.participant_id:
            self.participant_object = Participant.get(self.participant_id)

        return self.participant_object

    @property
    def company(self):
        if not self.company_object and self.company_id:
            self.company_object = Company.get(self.company_id)

        return self.company_object
