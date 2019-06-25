# Copyright (c) 2018. Uniquid Inc. or its affiliates. All Rights Reserved.
#
# License is in the "LICENSE" file accompanying this file.
# See the License for the specific language governing permissions and limitations under the License.

"""Constant definitions."""

# application version number
APP_VERSION = '0.5.5'

# minimum supported version of python
MIN_VERSION_MAJOR = 3
MIN_VERSION_MINOR = 6

# maximum supported version of credentials file
MAX_VERSION_CREDENTIALS = 1

# permanent UniquID HTTP API addresses
# static file server port
UNIQUID_STATIC_PORT = '80'
# onboarding server - production environment
UNIQUID_LOGIN_IP = 'production.uniquid.co'
UNIQUID_LOGIN_PORT = '3000'
UNIQUID_URL_SCHEME = 'http://'
# orchestrator
ORCHESTRATOR_PORT = '8080'

# log file name on local filesystem
LOG_PREFIX = 'uniquid_cli_'
LOG_SUFFIX = '.log'

# supported IoT PaaS platforms. used by deploy command.
PLATFORM_BASIC = 'basic'
PLATFORM_AWS = 'aws'
PLATFORMS = [PLATFORM_BASIC, PLATFORM_AWS]

# error messages for authentication and login
ERR_LOGGED_OUT = 'User is logged out. Please login again.'
ERR_LOGIN_REJECTED = 'Connection refused. Please login again and check credentials.'
ERR_LOGOUT_REJECTED = 'Logout rejected. Session may have expired.'
ERR_LOGOUT_ERROR = 'Failed to logout. May already be logged out.'
ERR_ORG_NOT_FOUND = 'Organization not registered at UniquID: '
ERR_QUERY_ERROR = 'Server returned bad data.'
ERR_MISSING_API_KEY = 'Login fail. Must specify API key or credentials file.'
ERR_MISSING_USERNAME = 'Login fail. Missing Username or email.'
ERR_MISSING_ORG_ID = 'Login fail. Missing Organization ID.'
ERR_MISSING_ORG_PORT = 'Login fail. Missing Organization IP/port.'
ERR_CRED_ORG = 'Login fail. Cannot specify credential file and organization.'
ERR_CRED_USER = 'Login fail. Cannot specify credential file and user.'
ERR_CRED_KEY = 'Login fail. Cannot specify credential file and access key.'
ERR_ORG_ID_URL = 'Login fail. Cannot specify organization identifier and URL.'
ERR_LOGIN_ORG_URL = 'Login fail. Specified login URL and organization URL.'
ERR_BAD_ORCH_URL = 'Login fail. Incorrect API URL.'
ERR_MISSING_IP_PORT = 'Login fail. Require both HTTP API IP and port number.'
ERR_NO_RESPONSE = 'Connection fail. No response from server.'
ERR_INVALID_URL = 'Login fail. Invalid UniquID URL as argument.'
ERR_ORCHESTRATOR_SPINUP = 'Login suspended.'
ERR_FILE_PERM = "Insufficient permissions to open file: "
ERR_FILE_OPEN = "Login fail. Missing credentials file: "
ERR_ORCH_REQ_FAIL = 'Failed to retrieve properties for Organization.'
# error messages for commands
ERR_ENDPOINT_REJECTED = 'Server rejected credentials. Please login again.'
ERR_SERVER_ERROR = 'Server internal error. Please try again.'
ERR_SINGLE_OPTION = 'One option/argument must be passed.'
ERR_INVALID_JSON = 'Invalid format of JSON data.'
ERR_MISSING_TXID = 'TXID must be passed to command.'
ERR_NO_CONTRACT = 'Contract not found.'
ERR_NO_SHARE = 'Share not found. Share Id: '
ERR_BAD_PLATFORM = 'Platform not supported: '
ERR_UNDEPLOY_NOT_REQUIRED = 'Undeploy not required. No services were started automatically for the platform.'
ERR_MISSING_DEPENDENCY = 'Missing dependency. Cannot proceed.'
# error messages for file system
ERR_TEMP_FILE = ('Failed to create or access a temporary file. ' +
                 'Check directory permissions.')
ERR_BAD_CRED_FILE = 'Invalid credentials file.'
ERR_CRED_FILE_VERSION = 'Unsupported version of credentials file.'
ERR_MISSING_LOCAL_FILE = 'Missing local file to upload: '
# unknown error - shouldn't happen
ERR_UNKNOWN_ERROR = 'Error occurred. Please try again.'

# supported formats for data output to the console
FORMAT_TEXT = 'text'
FORMAT_JSON = 'json'
FORMAT_ALL = [FORMAT_TEXT, FORMAT_JSON]

# User dialogs
TXT_TAB = '\t'
TXT_PASS = 'Done.'
TXT_PREFIX_OK = 'Success. '
TXT_PREFIX_FAIL = 'Failure. '
TXT_LOGIN_OK = TXT_PREFIX_OK + 'Logged in: '
TXT_LOGOUT_OK = TXT_PREFIX_OK + 'Logged out: '
TXT_CONTRACT_CREATED = TXT_PREFIX_OK + 'Contract(s) requested: '
TXT_CONTRACT_CREATED_ALL = TXT_PREFIX_OK + 'All contracts requested.'
TXT_CONTRACT_INTERRUPTED = (TXT_PREFIX_FAIL +
                            'Requests interrupted. Contract(s) requested: ')
TXT_CONTRACT_DELETED = TXT_PREFIX_OK + 'Contract deleted. TXID: '
TXT_CONTRACT_DELETED_ALL = TXT_PREFIX_OK + 'All contracts deleted.'
TXT_SHARE_CREATED = TXT_PREFIX_OK + 'Devices shared: '
TXT_SHARE_INTERRUPTED = (TXT_PREFIX_FAIL +
                         'Share creation interrupted. Devices shared: ')
TXT_SHARE_DEL_INTERRUPTED = (TXT_PREFIX_FAIL +
                             ('Share deletion interrupted. '
                              ' Device share(s) deleted: '))
TXT_SHARE_DELETED = TXT_PREFIX_OK + ' Share(s) deleted: '
TXT_LOGIN_FAIL_ORCH_SPINUP = (TXT_PREFIX_FAIL +
                              ('System is starting up. Please try again after '
                               'a brief wait.'))
TXT_CONF_STATUS = 'STATUS'
TXT_CONFIGURED_YES = 'Configured'
TXT_CONFIGURED_NO = 'Not configured'
TXT_ORG_ID = 'ORGANIZATION'

TXT_SESSION_STATUS = 'CONNECTION'
TXT_SESSION_ALIVE = 'Connected'
TXT_SESSION_DEAD = 'Disconnected'

# device sharing directions
SHARE_DIR_IN = 'in'
SHARE_DIR_OUT = 'out'
SHARE_DIR_BOTH = 'all'
SHARE_DIR_ALL = [SHARE_DIR_IN, SHARE_DIR_OUT, SHARE_DIR_BOTH]

# keys of JSON objects used in Orchestrator HTTP API
KEY_ORG_ID = 'orgId'

# credentials file schema
CREDENTIALS_SCHEMA = {
    'type': 'object',
    'properties': {
        'version': {'type': 'number'},
        'organization': {'type': 'string'},
        'user': {'type': 'string'},
        'accessKey': {'type': 'string'}
    },
    'required': ['version', 'organization', 'user', 'accessKey']
}
