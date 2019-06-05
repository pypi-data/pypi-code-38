"""
    Returns gdrive connection. Note, if no token.pickle or credentials.json
    files are found, OAuth2 flow is promoted to be completed via UI.
"""
import csv
import io
import os
import os.path
import json
import pandas as pd
import sys

from hellofresh_data import logging_setup
from hellofresh_data.parameter_store import get_parameter_store_value

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

PATH_TO_JSON = '/US/OA/Prod/GoogleAPI/service_account_json'

class GoogleDrive():
    """
        Google Drive Helper Class
    """
    def __init__(self):

        self.__location__ = os.getcwd()

        self._logger = logging_setup.init_logging("GoogleDrive")

        self.number_of_rows_pulled = 0
        self.file_name = None

    def get_google_api_service_account(self):
        """
            Returns Google API service account json as string.
        """
        service_account = get_parameter_store_value(PATH_TO_JSON)

        return service_account

    def get_gdrive_connection(self):
        """
            Uses service account json file, pulled from parameter store, to
            authenticate login. No browser login necessary.
        """
        scopes = ['https://www.googleapis.com/auth/drive']

        creds = None

        service_account_str = self.get_google_api_service_account()

        creds = json.loads(service_account_str)
        with open(os.path.join(self.__location__, 'service_account.json'), 'w') as fp:
            json.dump(creds, fp)

        service_account_file = \
        os.path.join(self.__location__, 'service_account.json')

        creds = Credentials.from_service_account_file(service_account_file,
                                                      scopes=scopes)

        return build('drive', 'v3', credentials=creds)

    def get_gsheet_connection(self):
        """
            Uses service account json file, pulled from parameter store, to
            authenticate login. No browser login necessary.
        """
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        creds = None

        service_account_str = self.get_google_api_service_account()

        creds = json.loads(service_account_str)
        with open(os.path.join(self.__location__, 'service_account.json'), 'w') as fp:
            json.dump(creds, fp)

        service_account_file = \
        os.path.join(self.__location__, 'service_account.json')

        creds = Credentials.from_service_account_file(service_account_file,
                                                      scopes=scopes)

        return build('sheets', 'v4', credentials=creds)

    def get_gsheet_file_by_id(self, file_id, range):
        """
            Get google sheet data by spreadsheet id
        """
        service = self.get_gsheet_connection()

        sheet = service.spreadsheets()

        try:
            result = sheet.values().get(spreadsheetId=file_id,
                                        range=range).execute()
        except HttpError as err:
            self._logger.warning('No files or sheet found with id: %s',
                                 file_id)
            sys.exit(0)

        values = result.get('values', [])

        return values

    def get_gdrive_csv_by_name(self, file_name):
        """
              Search drive by file name and check if file is present.
        """
        self.file_name = file_name
        gdrive_service = self.get_gdrive_connection()

        response = \
        gdrive_service.files().list(q="name='{}'".format(self.file_name),
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)'
                                    ).execute()

        response_obj = response.get('files', [])

        if not response_obj:
            self._logger.warning('No files found with name: %s', self.file_name)
            sys.exit(0)
        else:
            self._logger.info('Found file: %s', response_obj[0])

        data_io = self.get_gdrive_csv_by_id(response_obj[0].get('id'))

        return data_io

    def get_gdrive_csv_by_id(self, file_id):
        """
            Search drive by file ID and check if file is present.
            If present, download.
        """
        gdrive_service = self.get_gdrive_connection()

        try:
            response = gdrive_service.files().get_media(fileId=file_id)
            fh_io = io.BytesIO()
            downloader = MediaIoBaseDownload(fh_io, response, chunksize=1024*1024)

            self._logger.info('Downloading "%s" from drive...', self.file_name)
            done = False
            while done is False:
                status, done = downloader.next_chunk(num_retries=2)

        except HttpError as err:
            self._logger.error(err)
            sys.exit(1)

        self._logger.info('Downloaded "%s" successfully!', self.file_name)

        return fh_io.getvalue()

    def convert_drive_io_data_to_df(self, data):
        """
            Get the data streamed from google drive and convert
            to DataFrame.
        """

        self._logger.info('Convert stream drive data to pandas DataFrame')

        decoded_data = data.decode('utf-8')
        file_io = io.StringIO(decoded_data)
        reader = csv.reader(file_io, delimiter=',')

        data_df = pd.DataFrame(reader)
        data_df = data_df.infer_objects()

        self.number_of_rows_pulled = len(data_df)

        self._logger.info('Pulled %s rows from drive file', self.number_of_rows_pulled)

        return data_df
