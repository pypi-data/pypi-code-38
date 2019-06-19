from tinynetrc import Netrc
import sys
import dong

def get_credential_or_exit(message="Can't find any credential information, please login first."):
    netrc = Netrc()
    login = netrc[dong.SERVER_NAME]['login']
    password = netrc[dong.SERVER_NAME]['password']
    if login is None or password is None:
        print(message)
        sys.exit(1)

    return (login, password)
