import os.path
import pickle
from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from dftogsheet import config


class Service:
    def __init__(self, scopes):
        # Copied from https://developers.google.com/sheets/api/quickstart/python
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists(config.token):
            with open(config.token, 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.credentials,
                    scopes
                )
                creds = flow.run_local_server()
                
            # Save the credentials for the next run
            with open(config.token, 'wb') as token:
                pickle.dump(creds, token)

        self.resource = build('sheets', 'v4', credentials=creds)

