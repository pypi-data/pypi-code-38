from tweb import access_token as token_util
from tornado import gen


@gen.coroutine
def verify(uid, access_token, remote_ip):
    if uid is not None and access_token is not None:
        valid = yield token_util.verify_access_token(uid, access_token, remote_ip)
        if valid:
            return uid, access_token
    return None, None
