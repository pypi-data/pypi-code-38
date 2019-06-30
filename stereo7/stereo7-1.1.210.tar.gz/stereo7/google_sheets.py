import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


class GoogleSheets:

    def __init__(self,
                 APPLICATION_NAME='Google Sheets API Python Quickstart',
                 SCOPES='https://www.googleapis.com/auth/spreadsheets.readonly',
                 CLIENT_SECRET_FILE=''
                 ):
        self.application_name = APPLICATION_NAME
        self.scopes = SCOPES
        self.client_secret_file = CLIENT_SECRET_FILE
        self.flags = tools.argparser.parse_args(args=[])

        self.credentials = self._get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
        self.service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    def set_document(self, spreadsheetId):
        self.spreadsheetId = spreadsheetId

    def _get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'sheets.googleapis.com-python-quickstart.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.client_secret_file, self.scopes)
            flow.user_agent = self.application_name
            if self.flags:
                credentials = tools.run_flow(flow, store, self.flags)
            else:
                # Needed only for compatibility with Python 2.6
                # credentials = tools.run(flow, store)
                exit(-1)
            print 'Storing credentials to ' + credential_path
        return credentials

    def read_range(self, sheet, cell_from, cell_to, formula=False):
        rangeName = '{}!{}:{}'.format(sheet, cell_from, cell_to)
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheetId, range=rangeName).execute()
        if not formula:
            values = result.get('values', [])
        else:
            values = result.get('values', [], value_render_option='FORMULA')

        max_length = 0
        for line in values:
            max_length = max(max_length, len(line))
        for line in values:
            while len(line) < max_length:
                line.append('')
        return values

    def convert_range_to_dictionary_table(self, range):
        dict_ = {}
        for line in range:
            if not line:
                continue
            dict_[line[0]] = line[1:]
        return dict_

    def get_sheet_titles(self):
        sheet_metadata = self.service.spreadsheets().get(spreadsheetId=self.spreadsheetId).execute()
        sheets = sheet_metadata.get('sheets', '')
        titles = []
        for sheet in sheets:
            sheet_id = sheet.get("properties", {}).get("title", 0).encode('utf-8')
            titles.append(sheet_id)
        return titles


def main():
    gs = GoogleSheets()
    gs.set_document('1WvxSOHiH-AnoMhPek-mbIqkVgwboGYKrecjueGvT5jE')
    raw = gs.read_range(gs.get_sheet_titles()[0], 'A1', 'Z')
    for row in raw:
        print row


if __name__ == '__main__':
    main()
