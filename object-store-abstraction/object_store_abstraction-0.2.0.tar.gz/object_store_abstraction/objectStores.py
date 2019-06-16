from .objectStores_Memory import ObjectStore_Memory
from .objectStores_SQLAlchemy import ObjectStore_SQLAlchemy
from .objectStores_SimpleFileStore import ObjectStore_SimpleFileStore

class InvalidObjectStoreConfigMissingTypeClass(Exception):
  pass
InvalidObjectStoreConfigMissingTypeException = InvalidObjectStoreConfigMissingTypeClass('APIAPP_OBJECTSTORECONFIG value has no Type attribute')

class InvalidObjectStoreConfigUnknownTypeClass(Exception):
  pass
InvalidObjectStoreConfigUnknownTypeException = InvalidObjectStoreConfigUnknownTypeClass('APIAPP_OBJECTSTORECONFIG Type value is not recognised')

class ObjectStoreConfigNotDictObjectExceptionClass(Exception):
  pass

def _createObjectStoreInstanceTypeSpecified(type, configDICT, initFN, externalFns):
  print("Using Object Store Type: " + type)
  return initFN(configDICT, externalFns)

#Based on applicaiton options create an instance of objectStore to be used
def createObjectStoreInstance(objectStoreConfigDict, externalFns):
  if 'getCurDateTime' not in externalFns:
    raise Exception("createObjectStoreInstance - Must supply getCurDateTime externalFunction")
  if 'getPaginatedResult' not in externalFns:
    raise Exception("createObjectStoreInstance - Must supply getPaginatedResult externalFunction")

  if objectStoreConfigDict is None:
    objectStoreConfigDict = {}
    objectStoreConfigDict["Type"] = "Memory"

  if not isinstance(objectStoreConfigDict, dict):
    raise ObjectStoreConfigNotDictObjectExceptionClass('You must pass a dict as config to createObjectStoreInstance (or None)')


  if "Type" not in objectStoreConfigDict:
    raise InvalidObjectStoreConfigMissingTypeException
  if objectStoreConfigDict["Type"] == "Memory":
    return _createObjectStoreInstanceTypeSpecified("Memory", objectStoreConfigDict, ObjectStore_Memory, externalFns)
  if objectStoreConfigDict["Type"] == "SQLAlchemy":
    return _createObjectStoreInstanceTypeSpecified("SQLAlchemy", objectStoreConfigDict, ObjectStore_SQLAlchemy, externalFns)
  if objectStoreConfigDict["Type"] == "SimpleFileStore":
    return _createObjectStoreInstanceTypeSpecified("SimpleFileStore", objectStoreConfigDict, ObjectStore_SimpleFileStore, externalFns)

  raise InvalidObjectStoreConfigUnknownTypeException
