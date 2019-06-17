from QiDataLoader.DateTimeToOffsetMap import DateTimeToOffsetMap
from QiDataLoader.EnumInstrumentType import EnumInstrumentType
from QiDataLoader.EnumBarType import EnumBarType
from QiDataLoader.QiCore import QiCore
import datetime

class FileHeader():
    def __init__(self):
        self.__fileVersionSize = 8
        self.__fileHeaderSize = 64
        self.__fileHeaderTotalSize = 64 + 32 * 20 + 32 * 20
        self.__isDirty = False
        self.__fileVersion = '1.0'
        self.__market = EnumInstrumentType.期货
        self.__barType = EnumBarType.Minute
        self.__beginTime = datetime.datetime.today()
        self.__endTime = datetime.datetime.today()
        self.__beginTradingDay = datetime.datetime.today()
        self.__endTradingDay = datetime.datetime.today()
        self.__barCount = 0
        self.__period = 1
        self.__tradingDayIndices = DateTimeToOffsetMap(self)
        self.__naturalDayIndices = DateTimeToOffsetMap(self)

    @property
    def FileHeaderAllSize(self):
        return self.__fileHeaderTotalSize

    def MarkAsDirty(self, value):
        self.__isDirty = value

    def Read(self, reader):
        self.__fileVersion = reader.ReadString()
        reader.stream.seek(self.__fileVersionSize,0)
        self.__market = reader.ReadInt32()
        self.__barType = reader.ReadInt32()
        self.__period = reader.ReadInt32()
        self.__beginTime = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        self.__endTime = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        self.__beginTradingDay = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        self.__endTradingDay = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        self.__barCount = reader.ReadInt32()
        reader.stream.seek(self.__fileHeaderSize,0)
        self.__tradingDayIndices.Read(reader)
        self.__naturalDayIndices.Read(reader)
        self.MarkAsDirty(False)