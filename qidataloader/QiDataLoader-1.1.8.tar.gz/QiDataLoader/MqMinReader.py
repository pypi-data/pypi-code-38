from QiDataLoader.FileHeader import FileHeader
from QiDataLoader.EnumBarType import EnumBarType
from QiDataLoader.BinaryReader import BinaryReader
from QiDataLoader.Bar import Bar
from QiDataLoader.QiCore import QiCore
import datetime
import os

class MqMinReader(object):
    def __init__(self, instrumentType, instrumentId, filePath):
        self.__fileExtension = ".min"
        self.__instrumentId = instrumentId
        self.__filePath = filePath
        self.__fileHeader = FileHeader()
        self.__fileVersion = "1.0"
        self.__period = 1
        self.__market = instrumentType
        self.__barType = EnumBarType.Minute

        if (filePath.strip()==''):
            raise Exception("Invalid FilePath!")

        # extension = Path.GetExtension(filePath).ToLower()
        # if (extension != FileExtension)
        #     raise Exception("Invalid file extension!")

    def Read(self, barSeries, beginTime, endTime):
        # barSeries.InstrumentId = self.__instrumentId
        if isinstance(beginTime,datetime.date):
            beginTime = datetime.datetime(beginTime.year,beginTime.month,beginTime.day)
        if isinstance(endTime,datetime.date):
            endTime = datetime.datetime(endTime.year,endTime.month,endTime.day)
        readCount = 0
        data = open(self.__filePath, 'rb')
        reader = BinaryReader(data)
        self.__fileHeader.Read(reader)
        length = os.path.getsize(self.__filePath)
        while (reader.stream.tell() < length):
                readCount+=1
                bar = self.ReadBar(reader)
                if (bar.TradingDate >= beginTime) & (bar.TradingDate <= endTime):
                    barSeries.append(bar)
                elif (bar.TradingDate > endTime):
                    break
        return readCount > 0

    def ReadBar(self, reader):
        bar =  Bar()
        bar.BeginTime = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        bar.EndTime = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        bar.TradingDate = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
        bar.Open = reader.ReadDouble()
        bar.Close = reader.ReadDouble()
        bar.High = reader.ReadDouble()
        bar.Low = reader.ReadDouble()
        bar.PreClose = reader.ReadDouble()
        bar.Volume = reader.ReadDouble()
        bar.Turnover = reader.ReadDouble()
        bar.OpenInterest = reader.ReadDouble()
        bar.IsCompleted = True

        return bar
