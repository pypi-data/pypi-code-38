class Config:
    def __init__(
        self,
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        value_input_option='RAW',
        credentials='.dftogsheet/credentials/credentials.json',
        token='.dftogsheet/credentials/token.pickle'
    ):
        self.scopes = scopes
        self.value_input_option = value_input_option
        self.token = token
        self.credentials = credentials

    def set_scopes(self, scopes=['https://www.googleapis.com/auth/spreadsheets']):
        self.scopes = scopes
        os.remove(self.token)
    
    def set_value_input_option(self, value_input_option='RAW'):
        # Check that it's a valid option passed
        # Documentation https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption
        if value_input_option != 'RAW' and value_input_option != 'USER_ENTERED':
            error = f'Invalid value input option: {value_input_option}'
            url = 'https://developers.google.com/sheets/api/reference/rest/v4/ValueInputOption'
            raise ValueInputOptionError(f'{error}. See {url} for documentation.')
        self.value_input_option = value_input_option

    def set_token(self, token='.dftogsheet/credentials/token.pickle'):
        self.token = token

    def set_credentials(self, credentials='.dftogsheet/credentials/credentials.json'):
        self.credentials = credentials


class ValueInputOptionError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)

        if errors:
            self.errors = errors
