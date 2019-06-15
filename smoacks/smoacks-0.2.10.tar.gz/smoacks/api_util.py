# api_util - General API handling utilities for API clients
import logging
import os
import sys
from http import cookiejar
import requests
import jwt

LOGGER = logging.getLogger()

# Set and log base URL based on standard environment variables used in
# WSV environments.
if 'REACT_APP_BASE_URL' not in os.environ or 'REACT_APP_API_PATH' not in os.environ:
    sys.exit('Environment variables REACT_APP_BASE_URL and REACT_APP_API_PATH are not set')
BASE_URL = os.environ['REACT_APP_BASE_URL'] + os.environ['REACT_APP_API_PATH']
LOGGER.info('Base URL = {}'.format(BASE_URL))

# Define cookie acceptance policy broadly, as we need to retain
# the cookie from authenticating a user
class AcceptAll(cookiejar.CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: True
    netscape = True
    rfc2965 = hide_cookie2 = False

# Method to get an authenticated API session based on username and
# password. The session object contains CSRF tokens required for all
# API operations; the specific CSRF token required varies by API endpoint
def login(user, pwd):
    # Get a requests session object, which we will extend
    req_session = requests.session()
    req_session.cookies.set_policy(AcceptAll())
    # App session is an object containing a requests session and CSRF
    # tokens along with user ID and any user claims
    app_session = {
        'session': req_session,
        'csrf_token': None,
        'csrf_refresh_token': None
    }
    resp = call_api(app_session, 'POST', '/us/login', {'username': user, 'password': pwd})
    if not resp or resp.status_code != 200:
        print('Bad news, login failed!')
        return None
    json = resp.json()
    app_session['user_id'] = json['Users'][0]['user_id']
    claims = jwt.decode(app_session['session'].cookies['access_token_cookie'], verify=False)
    LOGGER.debug('claims = ' + str(claims))
    app_session['claims'] = claims
    return app_session

def call_api(app_session, method, url, payload=None, use_refresh_csrf=False):
    """Returns response for desired method with optional payload, adding JWT auth"""
    # If test_session is defined, then use it, otherwise use requests
    req = app_session['session'] if app_session else requests
    args = {}

    # If the supplied method supports a payload, then add it
    if method == 'PUT' or method == 'POST':
        args['json'] = payload
    
    # If the provided session has CSRF tokens, set the CSRF header
    if app_session and (app_session['csrf_token'] or app_session['csrf_refresh_token']):
        if use_refresh_csrf:
            args['headers'] = {'X-CSRF-TOKEN': app_session['csrf_refresh_token']}
        else:
            args['headers'] = {'X-CSRF-TOKEN': app_session['csrf_token']}

    # Log what we're going to call
    LOGGER.debug("\nBase URL:\n" + str(BASE_URL))
    LOGGER.debug('args = ' + str(args))

    # Get the response
    resp = None
    if method == 'GET':
        resp = req.get(BASE_URL + url, **args)
    elif method == 'PUT':
        resp = req.put(BASE_URL + url, **args)
    elif method == 'POST':
        resp = req.post(BASE_URL + url, **args)
    elif method == 'DELETE':
        resp = req.delete(BASE_URL + url, **args)
    
    # If we got a response and it has CSRF tokens, update the CSRF tokens
    # in the app session
    if resp and app_session and 'csrf_access_token' in resp.cookies:
        app_session['csrf_token'] = resp.cookies['csrf_access_token']
    if resp and app_session and 'csrf_refresh_token' in resp.cookies:
        app_session['csrf_refresh_token'] = resp.cookies['csrf_refresh_token']
    return resp

# Find the group ID for a gid based on groups in user session
def get_id_from_gid(session, gid):
    group_dict = session['claims']['user_claims']['groups']
    for group_id in group_dict:
        if group_dict[group_id]['gid'] == gid:
            return group_id

# Find the group ID for a group name based on groups in user session
def get_id_from_name(session, name):
    group_dict = session['claims']['user_claims']['groups']
    for group_id in group_dict:
        if group_dict[group_id]['name'] == name:
            return group_id
