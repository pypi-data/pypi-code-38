"""
Standard OS Module Exit Codes
    - See https://docs.python.org/3.6/library/os.html#process-management

Module Attributes:
    - exit_codes (dict):  exist error codes for Microsoft Windows
"""

import os


# --- exit codes for Microsoft Windows operating systems -----------------------


exit_codes = {
    'EX_OK': {
        'Code': 0,
        'Reason': 'No error occurred'
    },
    'E_DEPENDENCY': {
        'Code': 1,
        'Reason': 'Missing required dependency'
    },
    'E_DIR': {
        'Code': 2,
        'Reason': 'Failure to create log dir, log file'
    },
    'E_ENVIRONMENT': {
        'Code': 3,
        'Reason': 'Incorrect shell, language interpreter, or operating system'
    },
    'EX_AWSCLI': {
        'Code': 4,
        'Reason': 'Value could not be determined from local awscli configuration'
    },
    'EX_NOPERM': {
        'Code': 77,
        'Reason': 'IAM user or role permissions do not allow this action'
    },
    'E_AUTHFAIL': {
        'Code': 5,
        'Reason': 'Authentication Fail'
    },
    'E_BADPROFILE': {
        'Code': 6,
        'Reason': 'Local profile variable not set or incorrect'
    },
    'E_USER_CANCEL': {
        'Code': 7,
        'Reason': 'User abort'
    },
    'E_BADARG': {
        'Code': 8,
        'Reason': 'Bad input parameter'
    },
    'E_EXPIRED_CREDS': {
        'Code': 9,
        'Reason': 'Credentials expired or otherwise no longer valid'
    },
    'E_MISC': {
        'Code': 9,
        'Reason': 'Unknown Error'
    },
    'EX_NOUSER': {
        'Code': 67,
        'Reason': 'specified user does not exist'
    },
    'EX_CONFIG': {
        'Code': 78,
        'Reason': 'Configuration or config parameter error'
    },
    'EX_CREATE_FAIL': {
        'Code': 21,
        'Reason': 'Keyset failed to create. Possible Permissions issue'
    },
    'EX_DELETE_FAIL': {
        'Code': 22,
        'Reason': 'Keyset failed to delete.  Possible Permissions issue'
    }
}
