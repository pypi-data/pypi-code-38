from QiDataLoader.EnumBarType import EnumBarType
from QiDataLoader.BinaryReader import BinaryReader
from QiDataLoader.Bar import Bar
import datetime
import os

class MqDayReader(object):
    def __init__(self, instrumentType, instrumentId, filePath):
        self.CFileHeaderLen = 64
        self.CBarLen = 12 * 4
        self.CReserve = 48
        self.CPosEnd = 8
        self.__fileExtension = ".day"
        self.__instrumentId = instrumentId
        self.__filePath = filePath
        self.__market = instrumentType
        self.__barType = EnumBarType.Day
        self.__count = 0
        self.__beginDate = datetime.datetime.max
        self.__endDate = datetime.datetime.max
        self.__firstRead = True

        if (filePath.strip()==''):
            raise Exception("Invalid FilePath!")

    def Read(self, barSeries, beginDate, endDate):
        # barSeries.InstrumentId = self.__instrumentId
        if os.path.exists(self.__filePath) == False:
            # print("读取期货日k线失败(" + self.__filePath + "),文件不存在,跳过......")
            return

        if isinstance(beginDate,datetime.date):
            beginDate = datetime.datetime(beginDate.year,beginDate.month,beginDate.day)
        if isinstance(endDate,datetime.date):
            endDate = datetime.datetime(endDate.year,endDate.month,endDate.day)

        data = open(self.__filePath, 'rb')
        reader = BinaryReader(data)
        length = os.path.getsize(self.__filePath)
        if (length - self.CFileHeaderLen) % self.CBarLen != 0:
            raise Exception("日k线文件被破坏，数据出错")

        pos = self.CFileHeaderLen
        if self.__firstRead:
            self.ReadHeader(reader)
            pos -= self.CFileHeaderLen

        reader.stream.seek(pos, 1)
        self.ReadBars(reader, barSeries, beginDate, endDate)


    def ReadHeader(self,reader):
        interval = reader.ReadInt16()
        barType = reader.ReadInt16()
        if (barType != 4)| (interval != 1):
            print("错误的日k线文件标识")

        year = reader.ReadInt16()
        month = reader.ReadByte()
        day = reader.ReadByte()
        self.__beginDate = datetime.datetime(year, month, day)

        year = reader.ReadInt16()
        month = reader.ReadByte()
        day = reader.ReadByte()
        self.__endDate = datetime.datetime(year, month, day)

        if (self.__beginDate == datetime.datetime.max) | (self.__endDate == datetime.datetime.max) | (self.__beginDate > self.__endDate):
            raise Exception("非法的日k线文件")

        self.__count = reader.ReadInt32()
        length = os.path.getsize(self.__filePath)
        if self.__count != ((length  - self.CFileHeaderLen) / self.CBarLen):
            raise Exception("日k线文件被破坏，数据出错")

        reader.stream.seek(self.CReserve,1)
        self.__firstRead = False

    def ReadBars(self, reader, barSeries, beginDate, endDate):
        for i in range(0,self.__count):
            year = reader.ReadInt16()
            month = reader.ReadByte()
            day = reader.ReadByte()
            reader.stream.seek(self.CBarLen - 4, 1)
            dt = datetime.datetime(year, month, day)
            if dt >= beginDate:
                reader.stream.seek(-self.CBarLen, 1)
                break

        for i in range(i,self.__count):
            year = reader.ReadInt16()
            month = reader.ReadByte()
            day = reader.ReadByte()

            dt = datetime.datetime(year, month, day)

            if dt > endDate:
                break

            bar = Bar()
            bar.BeginTime = dt
            bar.EndTime =dt
            bar.Open = reader.ReadInt32() / 1000.0
            bar.Close = reader.ReadInt32() / 1000.0
            bar.High = reader.ReadInt32() / 1000.0
            bar.Low = reader.ReadInt32() / 1000.0
            bar.PreClose = reader.ReadInt32() / 1000.0
            bar.Volume = reader.ReadDouble()
            bar.Turnover = reader.ReadDouble()
            bar.OpenInterest = reader.ReadDouble()
            # bar.IsCompleted = True
            bar.TradingDate = dt

            barSeries.append(bar)

