"""authutils.globals

global variables for auth
"""


ROLES = {
    "ADMIN": "admin",
    "CREATE": "create",
    "DELETE": "delete",
    "DOWNLOAD": "download",
    "GENERAL": "_member_",
    "READ": "read",
    "RELEASE": "release",
    "UPDATE": "update",
}

MEMBER_DOWNLOADABLE_STATES = ["submitted", "processing", "processed"]

SUBMITTER_DOWNLOADABLE_STATES = [
    "uploaded",
    "validating",
    "validated",
    "error",
    "submitted",
    "processing",
    "processed",
]
