import os.path
import pickle
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Service:
    def __init__(self, config):
        # Copied from https://developers.google.com/sheets/api/quickstart/python
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(config.token) and os.path.getsize(config.token) > 0:
            with open(config.token, 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            # If there is no credentials file, raise error before we try to log in.
            if not os.path.exists(config.credentials):
                error = f'Missing credentials file: project-root-folder/{config.credentials}'
                help = 'Enable the Google Sheets API for your Google account and download your credentials file'
                url = 'https://developers.google.com/sheets/api/quickstart/python'
                raise AuthError(
                    f'{error}. {help} at {url} .'
                )
            
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.credentials,
                    config.scopes
                )
                creds = flow.run_local_server()
                
            # Save the credentials for the next run
            with open(config.token, 'wb') as token:
                pickle.dump(creds, token)

        self.resource = build('sheets', 'v4', credentials=creds)


class AuthError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)

        if errors:
            self.errors = errors
