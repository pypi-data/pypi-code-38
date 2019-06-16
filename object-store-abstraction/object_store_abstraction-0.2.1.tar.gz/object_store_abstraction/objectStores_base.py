# Code to save JSON objects into a store.
#  Allows abstraction of particular store
#  This is the baseClass other stores inherit from
StoringNoneObjectAfterUpdateOperationException = Exception('Storing None Object After Update Operation')
SavedObjectShouldNotContainObjectVersionException = Exception('SavedObjectShouldNotContainObjectVersion')

class WrongObjectVersionExceptionClass(Exception):
  pass
WrongObjectVersionException = WrongObjectVersionExceptionClass('Wrong object version supplied - Has another change occured since loading?')

class SuppliedObjectVersionWhenCreatingExceptionClass(Exception):
  pass
SuppliedObjectVersionWhenCreatingException = SuppliedObjectVersionWhenCreatingExceptionClass('Object verion was supplied but no current object found to be modified')

class ObjectStoreConfigError(Exception):
  pass

class MissingTransactionContextExceptionClass(Exception):
  pass
MissingTransactionContextException = MissingTransactionContextExceptionClass('Missing Transaction Context')

class UnallowedMutationExceptionClass(Exception):
  pass
UnallowedMutationException = UnallowedMutationExceptionClass("Trying to mutate objectStore without first starting a transaction")

class TriedToDeleteMissingObjectExceptionClass(Exception):
  pass
TriedToDeleteMissingObjectException = TriedToDeleteMissingObjectExceptionClass("Tried to delete non existant object")

class TryingToCreateExistingObjectExceptionClass(Exception):
  pass
TryingToCreateExistingObjectException = TryingToCreateExistingObjectExceptionClass("Tried to create an object that already exists")

'''
Calling pattern for connection where obj is and instance of ObjectStore:

storeConnection = obj.getConnectionContext()
def someFn(connectionContext):
  ##DO STUFF
storeConnection.executeInsideTransaction(someFn)

##Alternative (depreciated)
storeConnection = obj.getConnectionContext()
storeConnection.startTransaction()
try:
  ##DO STUFF
  storeConnection.commitTransaction()
except:
  storeConnection.rollbackTransaction()
  raise

'''

#Required until I update the baseapp with a class that accepts paginated param vlalues rather than a request
class artificalRequestWithPaginationArgs_args():
  paginatedParamValues = None
  def __init__(self, paginatedParamValues):
    self.paginatedParamValues = paginatedParamValues
  def get(self, paramName):
    if paramName in ['offset', 'pagesize', 'query', 'sort']:
      return self.paginatedParamValues[paramName]
    raise Exception("Unknown argument - " + paramName)
class artificalRequestWithPaginationArgs():
  args = None
  def __init__(self, paginatedParamValues):
    self.args = artificalRequestWithPaginationArgs_args(paginatedParamValues)
  

class ObjectStoreConnectionContext():
  #if object version is set to none object version checking is turned off
  # object version may be a number or a guid depending on store technology
  
  callsToStartTransaction = None
  def __init__(self):
    self.callsToStartTransaction = 0
  
  def _INT_startTransaction(self):
    if self.callsToStartTransaction != 0:
      raise Exception("Disabled ability for nexted transactions")
    self.callsToStartTransaction = self.callsToStartTransaction + 1
    return self._startTransaction()
  def _INT_commitTransaction(self):
    if self.callsToStartTransaction == 0:
      raise Exception("Trying to commit transaction but none started")
    self.callsToStartTransaction = self.callsToStartTransaction - 1
    return self._commitTransaction()
  def _INT_rollbackTransaction(self):
    if self.callsToStartTransaction == 0:
      raise Exception("Trying to rollback transaction but none started")
    self.callsToStartTransaction = self.callsToStartTransaction - 1
    return self._rollbackTransaction()
    
  def _INT_varifyWeCanMutateData(self):
    if self.callsToStartTransaction == 0:
      raise UnallowedMutationException
  
    
  def executeInsideTransaction(self, fnToExecute):
    retVal = None
    self._INT_startTransaction()
    try:
      retVal = fnToExecute(self)
      self._INT_commitTransaction()
    except:
      self._INT_rollbackTransaction()
      raise
    return retVal

  #Return value is objectVersion of object saved
  def saveJSONObject(self, objectType, objectKey, JSONString, objectVersion = None):
    if 'ObjectVersion' in JSONString:
      raise SavedObjectShouldNotContainObjectVersionException
    self._INT_varifyWeCanMutateData()
    return self._saveJSONObject(objectType, objectKey, JSONString, objectVersion)

  #Return value is None
  def removeJSONObject(self, objectType, objectKey, objectVersion = None, ignoreMissingObject = False):
    self._INT_varifyWeCanMutateData()
    return self._removeJSONObject(objectType, objectKey, objectVersion, ignoreMissingObject)

  # Update the object in single operation. make transaction safe??
  # Return value is same as saveJSONobject
  ## updateFn gets two paramaters:
  ##  object
  ##  connection
  #Seperate implementations not required as this uses save function
  def updateJSONObject(self, objectType, objectKey, updateFn, objectVersion = None):
    self._INT_varifyWeCanMutateData()
    
    obj, ver, creationDateTime, lastUpdateDateTime = self.getObjectJSON(objectType, objectKey)
    if objectVersion is None:
      #If object version is not supplied then assume update will not cause an error
      objectVersion = ver 
    if str(objectVersion) != str(ver):
      raise WrongObjectVersionException
    obj = updateFn(obj, self)
    if obj is None:
      raise StoringNoneObjectAfterUpdateOperationException
    return self.saveJSONObject(objectType, objectKey, obj, objectVersion)
  
  #Return value is objectDICT, ObjectVersion, creationDate, lastUpdateDate
  #Return None, None, None, None if object isn't in store
  def getObjectJSON(self, objectType, objectKey):
    return self._getObjectJSON(objectType, objectKey)
  
  def getPaginatedResult(self, objectType, paginatedParamValues, outputFN):
    def defOutput(item):
      return item
    def defFilter(item, whereClauseText):
      return True
    if outputFN is None:
      outputFN = defOutput
    return self._getPaginatedResult(objectType, paginatedParamValues, outputFN)
  
  def _saveJSONObject(self, objectType, objectKey, JSONString, objectVersion):
    raise Exception('Not Overridden')
  def _removeJSONObject(self, objectType, objectKey, objectVersion, ignoreMissingObject):
    raise Exception('Not Overridden')
  def _getObjectJSON(self, objectType, objectKey):
    raise Exception('Not Overridden')
  def _getPaginatedResult(self, objectType, paginatedParamValues, outputFN):
    raise Exception('Not Overridden')

  #should return a fresh transaction context
  def _startTransaction(self):
    raise Exception('Not Overridden')
  def _commitTransaction(self):
    raise Exception('Not Overridden')
  def _rollbackTransaction(self):
    raise Exception('Not Overridden')

  #Optional override for closing the context
  def _close(self):
    pass
    
#Base class for object store
class ObjectStore():
  externalFns = None
  def __init__(self, externalFns):
    self.externalFns = externalFns
  
  #def getConnectionContext(self):
  #  return self._getConnectionContext()
  def executeInsideConnectionContext(self, fnToExecute):
    context = self._getConnectionContext()
    a = None
    try:
      a = fnToExecute(context)
    finally:
      context._close()
    return a

  #helper function if we need just a single transaction in our contexts
  def executeInsideTransaction(self, fnToExecute):
    def dbfn(context):
      return context.executeInsideTransaction(fnToExecute)
    return self.executeInsideConnectionContext(dbfn)
      
  def _getConnectionContext(self):
    raise Exception('Not Overridden')

  def resetDataForTest(self):
    return self._resetDataForTest()

  #test only functions  
  def _resetDataForTest(self):
    raise Exception('Not Overridden')


