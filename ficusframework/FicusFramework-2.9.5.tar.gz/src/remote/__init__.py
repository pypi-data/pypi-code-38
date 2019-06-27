from flask import Blueprint

from api.exceptions import ServiceInnerException

remote = Blueprint('remote', __name__, )


@remote.errorhandler(ServiceInnerException)
def handle_bad_request(e):
    return str(e), 500


from .ActuatorRemote import *
from .TriggerRemoteActor import *
from .LogReadRemoteService import *
from .AsyncResponseRestService import *
