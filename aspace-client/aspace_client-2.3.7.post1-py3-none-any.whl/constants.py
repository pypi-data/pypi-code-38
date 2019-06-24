DEFAULT_API_HOST = 'http://localhost:8089'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'

X_AS_SESSION = 'X-ArchivesSpace-Session'

VALID_REPO_URI_REGEX = r'/?repositories/\d+'
VALID_USER_URI_REGEX = r'/?users/\d+'
VALID_ENUM_URI_REGEX = r'/?config/enumerations/\d+'
VALID_TOP_CONTAINER_URI_REGEX = r'(/?repositories/\d+)/top_containers/\d+'

DEFAULT_PASSWORD_CHARACTER_SET = (
    'abcdefghijklmnopqrstuvwxyz'
    + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    + '0123456789'
)
