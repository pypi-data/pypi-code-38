from flask import Blueprint

remote = Blueprint('remote', __name__, )

from .ActuatorRemote import *
from .TriggerRemoteActor import *
from .LogReadRemoteService import *
