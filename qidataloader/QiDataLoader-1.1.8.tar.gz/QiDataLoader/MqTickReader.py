import datetime
import os
from QiDataLoader.BinaryReader import BinaryReader
from QiDataLoader.QiCore import QiCore
from QiDataLoader.Tick import Tick
from QiDataLoader.TradingDayHelper import TradingDayHelper

class MqTickReader:
        CFileHeaderLen = 44
        COrigDayLen = 8 * 4
        CTickOffset = CFileHeaderLen + COrigDayLen
        CPosTickLen = 32
        CFileFlag = 1262700884 #('K' << 24) + ('C' << 16) + ('I' << 8) + 'T'
        _filePath = ""
        _instrumentId = ""
        _exchangeId = ""
        _instrumentType = 0
        _firstRead = False
        _bNewVersion = True

        # Header
        _version = 0
        _quoteCount = 0
        _multiUnit = 1000
        _tradingDay = datetime.date
        _preClosePrice = 0.0
        _preSettlementPrice = 0.0
        _preInterest = 0.0
        _upLimit = 0.0
        _downLimit = 0.0
        _openPrice = 0.0
        _tickCount = 0
        _origDayCount = 1
        _origDayOffset = 0
        _tickOffset = 0

        # OrigDay
        _origDays = []
        _origTickOffset = []

        # 18点后
        _preTradingDay1 = datetime.date
        # 9点前
        _preTradingDay2 = datetime.date
        CReserveOld = 27
        CTickHeaderLenOld = 32
        CFileHeaderLenOld = 64

        def __init__(self, instrumentType, instrumentId, filePath):
            self._filePath = filePath
            self._instrumentId = instrumentId
            self._exchangeId = "CFFEX"
            self._firstRead = True
            self._tradingDay = datetime.date
            self._instrumentType = instrumentType
        
        def Read(self, tickSeries, offset, count):
            if os.path.exists(self._filePath) == False:
                _firstRead = True
                print("读取期货tick数据失败(" + self._filePath + "),文件不存在")
                return False
            stream = open(self._filePath,'rb')
            reader= BinaryReader(stream)
            if self._firstRead:
                if self.ReadHeader(reader):
                    stream.seek(self._origDayOffset,0)
                    self.ReadOrigDays(reader)
                else:
                    stream.seek(0,0)
                    self.ReadOldHeader(reader)
                _firstRead = False
            if self._bNewVersion == True:
                pos = self._tickOffset + offset * (self.CPosTickLen + self._quoteCount * 2 * 8)
                stream.seek(pos)
                if self._quoteCount == 1:
                    self.ReadTicks1(tickSeries, reader, offset, count)
                else:
                    raise Exception("不支持" + self._quoteCount + "档盘口")
            else:
                pos = self.CFileHeaderLenOld + offset * (self.CTickHeaderLenOld + self._quoteCount * 2 * 8)
                stream.seek(pos)
                if self._quoteCount == 1:
                    self.ReadOldTicks1(tickSeries, reader, offset, count)
                else:
                    raise Exception("不支持" + self._quoteCount + "档盘口")
            stream.close()
            return True            
        
        def ReadHeader(self, reader):        
            flag = reader.ReadInt32()
            if flag != self.CFileFlag:
                return False
            self._origDays.clear()
            self._origTickOffset.clear()
            self._origDayCount = 0
            self._version = reader.ReadInt16()
            self._quoteCount = reader.ReadByte()
            tmp = 1
            multi = reader.ReadByte()
            for i in range(0,multi):
                tmp = tmp * 10

            self._multiUnit = tmp
            year = reader.ReadInt16()
            month = reader.ReadByte()
            day = reader.ReadByte()
            self._tradingDay = datetime.date(year, month, day)
            self._preClosePrice = reader.ReadInt32() / self._multiUnit
            self._preSettlementPrice = reader.ReadInt32() / self._multiUnit
            self._preInterest = reader.ReadInt32()
            self._upLimit = reader.ReadInt32() / self._multiUnit
            self._downLimit = reader.ReadInt32() / self._multiUnit
            self._openPrice = reader.ReadInt32() / self._multiUnit
            self._tickCount = reader.ReadInt32()
            orig = reader.ReadInt16()
            self._origDayCount = (orig >> 12)
            self._origDayOffset = (orig & 0x0fff)
            self._tickOffset = reader.ReadInt16()
            return True

        def ReadOldHeader(self,reader):
            self._origDays.clear()
            self._origTickOffset.clear()
            self._origDayCount = 0

            interval = reader.ReadInt16()
            barType = reader.ReadInt16()
            if ((barType & 0xff) != 0):
                raise Exception("错误的tick数据文件标识")

            self._bNewVersion = False
            if ((barType >> 10) & 0x3) == 1:
                self._multiUnit = 1000
            else:
                self._multiUnit = 100

            year = reader.ReadInt16()
            month = reader.ReadByte()
            day = reader.ReadByte()

            self._tradingDay =  datetime.date(year, month, day)
            self._preTradingDay1 = TradingDayHelper.GetPreTradingDay(self._tradingDay)
            self._preTradingDay2 = self._preTradingDay1 + datetime.timedelta(days=1)

            self._preClosePrice = reader.ReadInt32() / self._multiUnit
            self._preSettlementPrice = reader.ReadInt32() / self._multiUnit
            self._preInterest = reader.ReadInt32()
            self._upLimit = reader.ReadInt32() / self._multiUnit
            self._downLimit = reader.ReadInt32() / self._multiUnit
            self._openPrice = reader.ReadInt32() / self._multiUnit
            self._tickCount = reader.ReadInt32()
            self._quoteCount = reader.ReadByte()

            reader.ReadBytes(self.CReserveOld)

        def ReadOrigDays(self, reader):
            for i in range(0, self._origDayCount):
                year = reader.ReadInt16()
                month = reader.ReadByte()
                day = reader.ReadByte()
                origTickOffset = reader.ReadInt32()
                origDay = datetime.date(year, month, day)
                self._origDays.append(origDay)
                self._origTickOffset.append(origTickOffset)
                
        def ReadTicks1(self, tickSeries, reader, offset, count):
            for originIndex in range(0, len(self._origTickOffset)):
                if (offset < self._origTickOffset[originIndex]):
                    break
                originIndex = originIndex + 1
            originIndex = originIndex - 1
            if (originIndex < 0):
                return
            origDay = self._origDays[originIndex]
            nextOrigOffset = 100000000
            if (originIndex < len(self._origTickOffset) - 1):
                nextOrigOffset = self._origTickOffset[originIndex + 1] - 1
            tickLen = self._tickCount - offset
            if(tickLen < count):
                tickLen = tickLen
            else:
                tickLen = count
            for i in range(0,tickLen):
                tick = Tick()              
                tick.InstrumentType = self._instrumentType,
                tick.OpenPrice = self._openPrice,
                tick.PreClosePrice = self._preClosePrice,
                tick.InstrumentId = self._instrumentId,
                tick.ExchangeId = self._exchangeId,
                tick.PreOpenInterest = self._preInterest,
                tick.PreSettlementPrice = self._preSettlementPrice,
                tick.UpLimit = self._upLimit,
                tick.DropLimit = self._downLimit               
                hour = reader.ReadByte()
                min = reader.ReadByte()
                second = reader.ReadByte()
                milliseconds = reader.ReadByte()
                milliseconds *= 10
                tick.DateTime =datetime.datetime(origDay.year,origDay.month,origDay.day,hour, min, second, milliseconds)
                tick.TradingDay = self._tradingDay
                if self._version == 1:
                    tick.LocalTime = QiCore.ConvertCSharpTicksToPyDateTime(reader.ReadInt64())
                tick.LastPrice = reader.ReadInt32() / self._multiUnit
                tick.HighPrice = reader.ReadInt32() / self._multiUnit
                tick.LowPrice = reader.ReadInt32() / self._multiUnit
                tick.OpenInterest = reader.ReadInt32()
                tick.Volume = reader.ReadInt32()
                tick.Turnover = reader.ReadDouble()
                # quote = Quote()
                # quote.AskVolume1 = reader.ReadInt32()
                # quote.BidVolume1 = reader.ReadInt32()
                # quote.AskPrice1 = reader.ReadInt32() / self._multiUnit
                # quote.BidPrice1 = reader.ReadInt32() / self._multiUnit
                # tick.Quote = quote
                tick.AskVolume1 = reader.ReadInt32()
                tick.BidVolume1 = reader.ReadInt32()
                tick.AskPrice1 = reader.ReadInt32() / self._multiUnit
                tick.BidPrice1 = reader.ReadInt32() / self._multiUnit
                tickSeries.append(tick)

                if (i + offset >= nextOrigOffset):
                    originIndex = originIndex + 1
                    if (originIndex < len(self._origDays)):
                        origDay = self._origDays[originIndex]
                    nextOrigOffset = 10000000
                    if (originIndex < len(self._origTickOffset) - 1):
                        nextOrigOffset = self._origTickOffset[originIndex + 1] - 1

        def ReadOldTicks1(self, tickSeries, reader, offset, count):
            len = self._tickCount - offset
            if (len < count):
                len = len
            else:
                len = count
            for i in range(0, len):
                tick = Tick()
                tick.InstrumentType = self._instrumentType,
                tick.OpenPrice = self._openPrice,
                tick.PreClosePrice = self._preClosePrice,
                tick.InstrumentId = self._instrumentId,
                tick.ExchangeId = self._exchangeId,
                tick.PreOpenInterest = self._preInterest,
                tick.PreSettlementPrice = self._preSettlementPrice,
                tick.UpLimit = self._upLimit,
                tick.DropLimit = self._downLimit
                hour = reader.ReadByte()
                min = reader.ReadByte()
                second = reader.ReadByte()
                milliseconds = reader.ReadByte()
                milliseconds *= 10
                tick.TradingDay = self._tradingDay
                if hour<7:
                    tick.DateTime = datetime.datetime(self._preTradingDay2.year, self._preTradingDay2.month, self._preTradingDay2.day, hour, min, second, milliseconds)
                elif hour < 18:
                    tick.DateTime = datetime.datetime(self._tradingDay.year, self._tradingDay.month, self._tradingDay.day, hour, min, second, milliseconds)
                else:
                    tick.DateTime = datetime.datetime(self._preTradingDay1.year, self._preTradingDay1.month, self._preTradingDay1.day, hour, min, second, milliseconds)

                tick.LastPrice = reader.ReadInt32() / self._multiUnit
                tick.HighPrice = reader.ReadInt32() / self._multiUnit
                tick.LowPrice = reader.ReadInt32() / self._multiUnit
                tick.OpenInterest = reader.ReadInt32()
                tick.Volume = reader.ReadInt32()
                tick.Turnover = reader.ReadDouble()
                # quote = Quote()
                # quote.AskVolume1 = reader.ReadInt32()
                # quote.BidVolume1 = reader.ReadInt32()
                # quote.AskPrice1 = reader.ReadInt32() / self._multiUnit
                # quote.BidPrice1 = reader.ReadInt32() / self._multiUnit
                # tick.Quote = quote
                tick.AskVolume1 = reader.ReadInt32()
                tick.BidVolume1 = reader.ReadInt32()
                tick.AskPrice1 = reader.ReadInt32() / self._multiUnit
                tick.BidPrice1 = reader.ReadInt32() / self._multiUnit
                tickSeries.append(tick)
        
    