"""Google Sheets API."""

from httplib2 import Http

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Sheets(Base):
    """Sheets class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
        self.sheets = build(
            'sheets',
            'v4',
            credentials=credentials,
            discoveryServiceUrl=discoveryUrl
        )

    def batchupdate_sheet(self, spreadsheetId, body=[]):
        """Update a Google sheet."""
        return self.sheets.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheetId,
            body=body,
        ).execute()

    def clear_sheet(self, spreadsheetId, rangeName='Sheet1!A:A'):
        """Clear the values from a Google Sheet."""
        return self.sheets.spreadsheets().values().clear(
            spreadsheetId=spreadsheetId,
            range=rangeName,
            body={},
        ).execute()

    def get_sheet(self, spreadsheetId, rangeName='Sheet1!A:A'):
        """Return the data from a Google Sheet."""
        return self.sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=rangeName,
        ).execute()

    def update_sheet(
            self,
            spreadsheetId,
            body=[],
            rangeName='Sheet1!A:A',
            valueInputOption='RAW'
    ):
        """Update a Google sheet."""
        return self.sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheetId,
            range=rangeName,
            body=body,
            valueInputOption=valueInputOption
        ).execute()
