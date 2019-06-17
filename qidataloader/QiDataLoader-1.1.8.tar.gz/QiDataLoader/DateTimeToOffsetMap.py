import datetime
from QiDataLoader.QiCore import QiCore

class OffsetCount:
    __offset = 0
    __count = 0

    def __init__(self, offset, count):
        __offset = offset
        _count = count

    @property
    def Offset(self):
        return self.__offset

    @property
    def Count(self):
        return self.__count

    def ToString(self):
        msg = 'Offset:' + str(self.__offset)
        msg += 'Count:' + str(self.__count)
        return msg

class DateTimeToOffsetMap:


    def __init__(self, fileHeader):
        self._fileHeader = fileHeader
        self.__bucketSize = 32
        self.__mask = self.__bucketSize - 1
        self.__defaultKey = datetime.datetime.today()
        self.__keys = []
        self.__values = []

    def HashKey(self, time):
        return time.Day

    def Write(self, writer):
        for i in range(0, self.__bucketSize):
            writer.Write(self.__keys[i].Ticks)
        for i in range(0, self.__bucketSize):
            value = self.__values[i]
            writer.Write(value.Offset)
            writer.Write(value.Count)
            
    def Read(self, reader):
        for i in range(0, self.__bucketSize):
            self.__keys.append(QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64()))

        for i in range(0, self.__bucketSize):
            self.__values.append(OffsetCount(reader.ReadInt64(), reader.ReadInt32()))
        

        