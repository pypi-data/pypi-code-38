"""Google Calendar (as in 'google:USERNAME@gmail.com') loader."""

import datetime
import logging
import time

from googleapiclient import discovery
import oauth2client.file

from metabot.calendars import base
from metabot.util import iso8601


class Calendar(base.Calendar):
    """Google Calendar (as in 'google:USERNAME@gmail.com') loader."""

    caltype = 'google'
    sync_token = None

    _service = None

    @classmethod
    def service(cls):
        """An authenticated Google Calendar API Resource object."""

        if cls._service is None:
            store = oauth2client.file.Storage('config/google_calendar_credentials.json')
            cls._service = discovery.build('calendar',
                                           'v3',
                                           credentials=store.get(),
                                           cache_discovery=False)
        return cls._service

    def poll(self):
        changes = False
        page_token = None
        while True:
            try:
                results = self.service().events().list(  # pylint: disable=no-member
                    calendarId=self.calpath,
                    singleEvents=True,
                    syncToken=self.sync_token,
                    pageToken=page_token).execute()
            except:  # pylint: disable=bare-except
                logging.exception('Error during event fetch:')
                self.sync_token = page_token = None
                self.events = {}
                continue

            for event in results.get('items', ()):
                if event['status'] == 'cancelled':
                    if self._removed(event['id']):
                        changes = True
                else:
                    if self._updated(event):
                        changes = True
            page_token = results.get('nextPageToken')
            if not page_token:
                if self.sync_token != results['nextSyncToken']:
                    self.sync_token = results['nextSyncToken']
                    changes = True
                break
            time.sleep(1)
        return changes

    def event_proto_to_local(self, proto):
        return {
            'description': proto.get('description'),
            'end': self.datetime_proto_to_local(proto['end']),
            'id': proto['id'],
            'location': proto.get('location'),
            'start': self.datetime_proto_to_local(proto['start']),
            'summary': proto.get('summary'),
            'updated': self.datetime_proto_to_local(proto['updated']),
        }

    def event_local_to_proto(self, local):
        proto = {}

        for k in ('description', 'id', 'location', 'summary'):
            if k in local:
                proto[k] = local[k]

        for k in ('end', 'start'):
            if k in local:
                proto[k] = self.datetime_local_to_proto(local[k])

        return proto

    @staticmethod
    def datetime_proto_to_local(proto):
        """Convert a time spec from Google Calendar API format to local format."""

        if isinstance(proto, dict):
            if proto.get('dateTime'):
                proto = proto['dateTime']
            else:
                proto = proto['date']
        return iso8601.totimestamp(proto)

    @staticmethod
    def datetime_local_to_proto(local):
        """Convert a time spec from local format to Google Calendar API format."""

        return {
            'date': None,
            'dateTime': datetime.datetime.utcfromtimestamp(local).isoformat() + 'Z',
            'timeZone': None,
        }

    def proto_add(self, proto):
        # pylint: disable=no-member
        return self.service().events().insert(calendarId=self.calpath, body=proto).execute()

    def proto_remove(self, proto_id):
        # pylint: disable=no-member
        self.service().events().delete(calendarId=self.calpath, eventId=proto_id).execute()

    def proto_update(self, proto_id, proto):
        return self.service().events().patch(  # pylint: disable=no-member
            calendarId=self.calpath, eventId=proto_id, body=proto).execute()
