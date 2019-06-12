"""Google Calendar API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Calendar(Base):
    """Calendar class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.calendar = build('calendar', 'v3', credentials=credentials)

    def get_calendar(self, calendarId):
        """Return a calendar."""
        return self.calendar.calendars().get(calendarId=calendarId).execute()

    def get_calendar_list(self):
        """Return a list of calendars."""
        calendarList = self.calendar.calendarList()
        request = calendarList.list()
        return self.get_list_items(calendarList, request, 'items')

    def get_calendar_events_list(
            self,
            calendarId,
            showDeleted=False,
            singleEvents=False,
            timeMin=None,
            timeMax=None,
            timeZone=None,
    ):
        """Return a list of calendars."""
        params = {
            'calendarId': calendarId,
            'showDeleted': showDeleted,
            'singleEvents': singleEvents,
            'timeMin': timeMin,
            'timeMax': timeMax,
            'timeZone': timeZone,
        }
        events = self.calendar.events()
        request = events.list(**params)
        return self.get_list_items(events, request, 'items')

    def create_calendar_acl(self, calendarId, body):
        """Create a access control rule for a calendar."""
        acl = self.calendar.acl()
        return acl.insert(calendarId=calendarId, body=body).execute()

    def get_calendar_acls(self, calendarId):
        """Return a list of acls for a calendar."""
        acl = self.calendar.acl()
        request = acl.list(calendarId=calendarId)
        return self.get_list_items(acl, request, 'items')

    def update_calendar_acl(self, calendarId, ruleId, body):
        """Create a access control rule for a calendar."""
        return self.calendar.acl().update(
            calendarId=calendarId,
            ruleId=ruleId,
            body=body
        ).execute()

    def update_calendar(self, calendarId, body):
        """Update a calendar."""
        return self.calendar.calendars().update(
            calendarId=calendarId,
            body=body
        ).execute()
