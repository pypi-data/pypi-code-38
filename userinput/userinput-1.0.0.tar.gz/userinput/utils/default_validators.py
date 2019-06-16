from validate_email import validate_email
from validate_version_code import validate_version_code
from validators import url
import socket

def hostname(server: str)->bool:
    try:
        socket.gethostbyname(server)
        return True
    except socket.gaierror:
        return False

default_validators = {
    "email":validate_email,
    "version_code":validate_version_code,
    "url":url,
    "integer":lambda x: isinstance(x, int),
    "positive_integer":lambda x: isinstance(x, int) and x>=0,
    "non_empty":lambda x: isinstance(x, str) and len(x)>0,
    "hostname":hostname
}