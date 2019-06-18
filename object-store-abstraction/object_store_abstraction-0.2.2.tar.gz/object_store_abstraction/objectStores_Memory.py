from .objectStores_base import ObjectStore, ObjectStoreConnectionContext, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException, SuppliedObjectVersionWhenCreatingException, artificalRequestWithPaginationArgs

class ConnectionContext(ObjectStoreConnectionContext):
  objectStore = None
  def __init__(self, objectStore):
    super(ConnectionContext, self).__init__()
    self.objectStore = objectStore

  #transactional memory not implemented
  def _startTransaction(self):
    pass
  def _commitTransaction(self):
    pass
  def _rollbackTransaction(self):
    pass


  def _saveJSONObject(self, objectType, objectKey, JSONString, objectVersion):
    dictForObjectType = self.objectStore._INT_getDictForObjectType(objectType)
    curTimeValue = self.objectStore.externalFns['getCurDateTime']()
    newObjectVersion = None
    if objectKey not in dictForObjectType:
      if objectVersion is not None:
        raise SuppliedObjectVersionWhenCreatingException
      newObjectVersion = 1
      dictForObjectType[objectKey] = (JSONString, newObjectVersion, curTimeValue, curTimeValue)
    else:
      #We have found an object in the DB
      if objectVersion is None:
        raise TryingToCreateExistingObjectException
      if str(objectVersion) != str(dictForObjectType[objectKey][1]):
        raise WrongObjectVersionException
      newObjectVersion = int(objectVersion) + 1
    dictForObjectType[objectKey] = (JSONString, newObjectVersion, dictForObjectType[objectKey][2], curTimeValue)
    return newObjectVersion

  def _removeJSONObject(self, objectType, objectKey, objectVersion, ignoreMissingObject):
    dictForObjectType = self.objectStore._INT_getDictForObjectType(objectType)
    if objectVersion is not None:
      if objectKey not in dictForObjectType:
        if ignoreMissingObject:
          return None
        raise TriedToDeleteMissingObjectException
      if str(dictForObjectType[objectKey][1]) != str(objectVersion):
        raise WrongObjectVersionException
    if objectKey not in self.objectStore._INT_getDictForObjectType(objectType):
      if ignoreMissingObject:
        return None
    del self.objectStore._INT_getDictForObjectType(objectType)[objectKey]
    return None

  def _getObjectJSON(self, objectType, objectKey):
    objectTypeDict = self.objectStore._INT_getDictForObjectType(objectType)
    if objectKey in objectTypeDict:
      return objectTypeDict[objectKey]
    return None, None, None, None

  def _filterFN(self, item, whereClauseText):
    if whereClauseText is None:
      return True
    if whereClauseText == '':
      return True
    ###userDICT = CreateUserObjFromUserDict(appObj, item[0],item[1],item[2],item[3]).getJSONRepresenation()
    #TODO replace with a dict awear generic function
    #  we also need to consider removing spaces from consideration
    return whereClauseText in str(item).upper()


  def _getPaginatedResult(self, objectType, paginatedParamValues, outputFN):
    ##print('objectStoresMemory._getPaginatedResult self.objectType.objectData[objectType]:', self.objectType.objectData[objectType])
    srcData = []
    if objectType in self.objectStore.objectData:
      srcData = self.objectStore.objectData[objectType]
    return self.objectStore.externalFns['getPaginatedResult'](
      srcData,
      outputFN,
      artificalRequestWithPaginationArgs(paginatedParamValues),
      self._filterFN
    )

# Class that will store objects in memory only
class ObjectStore_Memory(ObjectStore):
  objectData = None
  def __init__(self, configJSON, externalFns):
    super(ObjectStore_Memory, self).__init__(externalFns)
    self.objectData = dict()
    #Dict = (objDICT, objectVersion, creationDate, lastUpdateDate)

  def _INT_getDictForObjectType(self, objectType):
    if objectType not in self.objectData:
      #print("Creating dict for " + objectType)
      self.objectData[objectType] = dict()
    return self.objectData[objectType]

  def _getConnectionContext(self):
    return ConnectionContext(self)
