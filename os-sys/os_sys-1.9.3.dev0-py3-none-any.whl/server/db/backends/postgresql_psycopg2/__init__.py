import warnings

from server.utils.deprecation import RemovedInServer30Warning

warnings.warn(
    "The server.db.backends.postgresql_psycopg2 module is deprecated in "
    "favor of server.db.backends.postgresql.",
    RemovedInServer30Warning, stacklevel=2
)
