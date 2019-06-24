"""
Description:
    A library of useful SSL lookup tools, including expiry checking etc.
"""
import OpenSSL
import ssl, socket
from datetime import datetime

def check_ssl_expiry(hostname="."):
    """Allows you to check the SSL expiry. More specificly it will return\
        the notAfter for the SSL cert.
    Returns:
        str: The date and time of expiry in YYYY-MM-DD HH:MM:SS format"""
    cert=ssl.get_server_certificate((hostname, 443))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    return str(datetime.strptime(x509.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ'))
