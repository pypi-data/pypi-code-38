"""Google drive API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Drive(Base):
    """Drive class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.drive = build('drive', 'v3', credentials=credentials)
        self.drive_v2 = build('drive', 'v2', credentials=credentials)

    def add_parents(self, fileId, parents):
        """Add parents to a drive file."""
        params = {
            'fileId': fileId,
            'addParents': parents,
        }
        return self.drive.files().update(**params).execute()

    def change_owner(self, fileId, owner):
        """Change the owner of a drive file."""
        body = {
            'emailAddress': owner,
            'role': 'owner',
            'type': 'user',
            'value': owner,
        }
        params = {
            'body': body,
            'fileId': fileId,
            'sendNotificationEmails': False,
        }
        return self.drive_v2.permissions().insert(**params).execute()

    def change_owner_v3(self, fileId, owner):
        """Change the owner of a drive file."""
        body = {
            'emailAddress': owner,
            'role': 'owner',
            'type': 'user',
            'value': owner,
        }
        params = {
            'body': body,
            'fileId': fileId,
            'sendNotificationEmail': False,
            'transferOwnership': True,
        }
        return self.drive.permissions().create(**params).execute()

    def create_folder(self, name):
        """Create a drive folder."""
        body = {
            'mimeType': 'application/vnd.google-apps.folder',
            'name': name,
            'parents': [{'id': 'root'}],
        }
        return self.drive.files().create(body=body).execute()

    def get_about(self, fields=None):
        """Return the about informaiton for a Google Drive user."""
        fieldnames = [
            'appInstalled',
            'exportFormats',
            'folderColorPalette',
            'importFormats',
            'kind',
            'maxImportSizes',
            'maxUploadSize',
            'storageQuota',
            'user',
        ]
        if not fields:
            fields = ','.join(fieldnames)
        return self.drive.about().get(fields=fields).execute()

    def get_files(self, fields=None, orderBy=None, q=None):
        """Return a list of Google Drive files."""
        fieldnames = [
            'nextPageToken',
            'files(id,name,mimeType,ownedByMe,permissions)',
        ]
        if not fields:
            fields = ','.join(sorted(fieldnames))
        params = {
            'fields': fields,
            'orderBy': orderBy,
            'q': q,
        }
        files = self.drive.files()
        request = files.list(**params)
        return self.get_list_items(files, request, 'files')

    def get_team_drives(self):
        """Return a list of Google Team Drives."""
        teamDrives = self.drive.teamdrives()
        request = teamDrives.list(useDomainAdminAccess=True)
        return self.get_list_items(teamDrives, request, 'teamDrives')
