from squirreldb.commands.listOperations import ListOperations

class ListOperationsImpl(ListOperations):

    def  __init__(self):
        super().__init__()

    def rpushKey(self, inMemoryReference, key, value):
        if inMemoryReference == None or key == None or value == None:
            return False
        if key not in inMemoryReference:
            inMemoryReference[key] = []
        if isinstance(inMemoryReference[key], list):
            if len(inMemoryReference[key]) == 0:
                inMemoryReference[key].append(value)
                return True
            elif type(inMemoryReference[key][-1]) == type(value):
                inMemoryReference[key].append(value)
                return True
        return False

    def rpushKeyIfExists(self, inMemoryReference, key, value):
        if inMemoryReference == None or key == None or value == None:
            return False
        if key in inMemoryReference:
            return self.rpushKey(inMemoryReference, key, value)
        else:
            return False

    def lpushKey(self, inMemoryReference, key, value):
        if inMemoryReference == None or key == None or value == None:
            return False
        if key not in inMemoryReference:
            inMemoryReference[key] = []
        if isinstance(inMemoryReference[key], list):
            if len(inMemoryReference[key]) == 0:
                inMemoryReference[key].insert(0,value)
                return True
            elif type(inMemoryReference[key][0]) == type(value):
                inMemoryReference[key].insert(0, value)
                return True
        return False

    def llen(self, inMemoryReference, key):
        if inMemoryReference == None or key == None:
            return False
        if key in inMemoryReference:
            if isinstance(inMemoryReference[key],list):
                return len(inMemoryReference[key])
        return False

    def lpop(self, inMemoryReference, key):
        if inMemoryReference == None or key == None:
            return False
        if key in inMemoryReference:
            if isinstance(inMemoryReference[key], list):
                if len(inMemoryReference[key]) != 0:
                    return inMemoryReference[key].pop(0)
        return False

    def lindex(self, inMemoryReference, key,index):
        if inMemoryReference == None or key == None or index == None:
            return False
        if key in inMemoryReference:
            if isinstance(inMemoryReference[key], list):
                inMemoryListReference = inMemoryReference[key]
                #Pretty compilcated white listing of the index value
                if type(index) is int and index > 0 and index < len(inMemoryListReference):
                    return inMemoryListReference[index]
        return False


    def linsert(self, inMemoryReference, key, pivot, value):
        if inMemoryReference == None or key == None or pivot == None or value == None:
            return  False
        if key in inMemoryReference:
            inMemoryListReference = inMemoryReference[key]
            if isinstance(inMemoryListReference, list):
                if isinstance(pivot, int):
                    if 0 < pivot < len(inMemoryListReference):
                        if type(inMemoryListReference[-1]) == type(value):
                            inMemoryListReference.insert(pivot, value)
                            return True
                    elif pivot == 0:
                        if len(inMemoryListReference) > 0 and type(inMemoryListReference[-1]) == type(value):
                            inMemoryListReference.insert(pivot,value)
                            return True
                        elif len(inMemoryListReference) == 0:
                            inMemoryListReference.append(value)
                            return True
                    elif pivot >= len(inMemoryListReference):
                        if len(inMemoryListReference) > 0 and type(inMemoryListReference[-1]) == type(value):
                            inMemoryListReference.append(value)
                            return True
                        else:
                            inMemoryListReference.append(value)
                            return True
        return False


    def ltrim(self, inMemoryReference, key, start, stop):
        if inMemoryReference == None or key == None or start == None or stop == None:
            return False
        if not isinstance(start, int) or not isinstance(stop, int) or start > stop or start < 0:
            return False
        if key in inMemoryReference:
            inMemoryListReference = inMemoryReference[key]
            if isinstance(inMemoryListReference, list):
                if start < len(inMemoryListReference):
                    inMemoryReference[key] = inMemoryListReference[start:stop+1]
                    return True
                elif start >= len(inMemoryListReference):
                    inMemoryReference[key] = []
                    return True
        return False

    def lset(self, inMemoryReference, key, index, value):
        if inMemoryReference == None or key == None or index == None or value == None:
            return False
        if key in inMemoryReference:
            inMemoryListReference = inMemoryReference[key]
            if isinstance(inMemoryListReference, list):
                if isinstance(index, int) and 0 <= index < len(inMemoryListReference):
                    if type(inMemoryListReference[index]) == type(value):
                        inMemoryListReference[index] = value
                        return True
                    if len(inMemoryListReference) == 0 and index == 0:
                        inMemoryListReference.append(value)
                        return True
        elif isinstance(index, int) and index == 0:
            inMemoryReference[key] = [value]
            return True
        return False


    def rpop(self, inMemoryReference, key):
        if inMemoryReference == None or key == None:
            return False
        if key in inMemoryReference:
            inMemoryListReference = inMemoryReference[key]
            if isinstance(inMemoryListReference, list):
                if len(inMemoryListReference) > 0:
                    return inMemoryListReference.pop(-1)
        return False


    def lrange(self, inMemoryReference, key, start, end):
        if inMemoryReference == None or key == None or start == None or end == None:
            return False
        if not isinstance(start, int) or not isinstance(end, int) or start > end or start < 0:
            return False
        if key in inMemoryReference:
            inMemoryListReference = inMemoryReference[key]
            if isinstance(inMemoryListReference , list):
                if start < len(inMemoryListReference):
                    return inMemoryListReference[start:end+1]
                elif start >= len(inMemoryListReference):
                    return []
        return False

    def createList(self, inMemoryReference, key):
        if inMemoryReference == None or key == None:
            return False
        if key not in inMemoryReference:
            inMemoryReference[key] = []
            return True
        return False


    def deleteList(self, inMemoryReference, key):
        if inMemoryReference == None or key == None:
            return False
        if key in inMemoryReference:
            if isinstance(inMemoryReference[key], list):
                del inMemoryReference[key]
                return True
        return False
