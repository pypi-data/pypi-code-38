"""
High level network communication

This tool abstracts network communication to a level, where the end user don`t has to care about
network communication. Server side functions can be called at the client as they were local and vise versa.
Functions may be called with parameters and may return values.

"""
from pynetworking.Communication_client import ServerCommunicator, ServerFunctions, MultiServerCommunicator
from pynetworking.Communication_server import ClientCommunicator, ClientFunctions, ClientManager
from pynetworking.Data import File
import pynetworking.utils
import pynetworking.Logging

pynetworking.Logging.logger.setLevel(40)
