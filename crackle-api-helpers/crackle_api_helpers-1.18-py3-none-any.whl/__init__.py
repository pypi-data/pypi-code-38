''' Crackle API Wrapper setup '''
from crackle_api_helpers.auth_key_missing_error import AuthKeyMissingError
from crackle_api_helpers.session import SESSION

__all__ = ['AuthKeyMissingError', 'SESSION']
