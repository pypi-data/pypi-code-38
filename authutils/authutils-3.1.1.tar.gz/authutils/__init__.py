from authutils.errors import AuthError
from authutils.user import CurrentUser, set_global_user

__all__ = ["AuthError", "CurrentUser", "ROLES", "set_global_user"]

ROLES = dict(
    ADMIN="admin",
    CREATE="create",
    DELETE="delete",
    DOWNLOAD="download",
    GENERAL="_member_",
    READ="read",
    RELEASE="release",
    UPDATE="update",
)
