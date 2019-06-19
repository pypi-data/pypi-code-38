'''Emarsys API Authenticator

This script allows the user to easily create a X_WSSE header 
for Authentication with the Emarsys RESTful API.
'''

# import needed modules
import uuid
import hashlib
import datetime
import base64

def create_xwsse_header(username, secret):
    # Returns x_wsse authentication headers for emarsys api call.
    #
    # Content 
    # -------
    # UsernameToken
    #     Indicates that the authentication method of WSSE is token-based.
    # Username
    #     Contains the user name.
    # PasswordDigest
    #     Contains the hashed token (Nonce + Created + Secret) that authenticates the request. 
    #     It must be recomputed for each request.
    # Nonce
    #     A random value ensuring that the request is unique. 
    #     This string is always 16 bytes long and must be represented as a 32-character hexadecimal value.
    # Created
    #     Contains the current UTC, GMT, ZULU timestamp (YYYY-MM-DDTHH:MM:SS) according to the ISO8601 format.
    #
    # For more information see emarsys documentation on https://dev.emarsys.com/v2/before-you-start/authentication
    #
    # Parameters
    # ----------
    # username : str 
    #     user name for emarsys account
    # sercret : str
    #     secret for emarsys account
    #
    # Returns
    # -------
    # dict

    # Login information for emarsys    
    user_name = username
    user_secret = secret

    # Create random 32-character hexadeximal value
    nonce = uuid.uuid4().hex

    # Create current utc time in ISO8601 format
    created = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    # Create sha1-hash-object and feed it with needed information       
    hash_digest = hashlib.sha1()
    hash_digest.update(nonce.encode("utf-8"))
    hash_digest.update(created.encode("utf-8"))
    hash_digest.update(user_secret.encode("utf-8"))

    # Get hashed value as encoded hexadeciaml
    password_digest = hash_digest.hexdigest().encode("utf-8")
    
    # Encode hashed value in base64 and decode
    password_digest = base64.b64encode(password_digest).decode('utf-8')

    # Assemble headers
    X_WSSE = 'UsernameToken Username="' +user_name+ '", PasswordDigest="' +password_digest+ '", Nonce="' +nonce+ '", Created="' +created+ '"' 
    headers = {
        'Content-Type': 'application/json',
        'X-WSSE': X_WSSE
    }
    
    return headers
