from QiDataLoader.MqTickReader import MqTickReader
from QiDataLoader.MqMinReader import MqMinReader
from QiDataLoader.MqDayReader import MqDayReader
from QiDataLoader.EnumInstrumentType import EnumInstrumentType
from dateutil.relativedelta import relativedelta
import datetime
import os

class MqDataLoader: 
    def __init__(self, futureTickPath):
        self._futureTickPath = futureTickPath

    def GetTickSeries(self, instrumentId, beginTime, endTime):
        tickSeries = []
        tradingDate = beginTime
        while(tradingDate <= endTime):  
            filePath = self._futureTickPath+"/"+ tradingDate.strftime('%Y%m%d')+"/"+instrumentId + ".tk"
            if(os.path.exists(filePath)):
                if (instrumentId != "index"):        
                    mqTickReader = MqTickReader("", instrumentId, filePath)
                    mqTickReader.Read(tickSeries, 0, 10000000000)       
            tradingDate = tradingDate + datetime.timedelta(days=1)
   
        return tickSeries

    def GetMinBarSeries(self, instrumentId, beginTime, endTime, path):
        barSeries = []
        beginMoth = datetime.datetime(beginTime.year, beginTime.month, 1, 0, 0, 0);
        endMonth = datetime.datetime(endTime.year, endTime.month, 1, 0, 0, 0);
        while (beginMoth <= endMonth):
            filePath = path + '/' + beginMoth.strftime('%Y%m')
            if (os.path.exists(filePath)):
                if (instrumentId != "index"):
                    filePath = filePath + '/' + instrumentId+ '.min'
                    mqMinReader = MqMinReader(EnumInstrumentType.期货, instrumentId, filePath);
                    mqMinReader.Read(barSeries, beginTime, endTime);
            beginMoth = beginMoth + relativedelta(months=+1)

        return barSeries

    def GetDayBarSeries(self, instrumentId, beginTime, endTime, path):
        barSeries = []
        beginMoth = datetime.datetime(beginTime.year, beginTime.month, 1, 0, 0, 0);
        endMonth = datetime.datetime(endTime.year, endTime.month, 1, 0, 0, 0);
        while (beginMoth <= endMonth):
            filePath = path + '/' + beginMoth.strftime('%Y%m')
            if (os.path.exists(filePath)):
                if (instrumentId != "index"):
                    filePath = filePath + '/' + instrumentId+ '.day'
                    mqMinReader = MqDayReader(EnumInstrumentType.期货, instrumentId, filePath);
                    mqMinReader.Read(barSeries, beginTime, endTime);
            beginMoth = beginMoth + relativedelta(months=+1)

        return barSeries
