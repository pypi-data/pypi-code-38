import math
import time
from QiDataLoader.Quote import Quote

class Tick: 
    NumTrades = 0
    TotalBidQty = 0
    TotalAskQty = 0
    WeightedAvgBidPrice = 0.0
    WeightedAvgAskPrice = 0.0
    BidPriceLevel = 1
    AskPriceLevel = 1

    _instrumentId = ""
    _exchangeId = ""
    _quote = Quote()
    _status = 1
    _lastPrice = 0.0
    _iopv = 0.0
    _preClosePrice = 0.0
    _openPrice = 0.0
    _highPrice = 0.0
    _lowPrice = 0.0
    _volume = 0
    _turnover = 0.0
    _upLimitPrice = 0.0
    _dropLimitPrice = 0.0
    _tradingDay = time.time()
    _naturalTime = time.time()
    _localTime = time.time()
    _openInterest = 0.0
    _preOpenInterest = 0.0
    _preSettlementPrice = 0.0
    _instrumentType =1

    #测试先用
    _askPrice1 = 0.0
    _askVolume1 = 0
    _bidPrice1 = 0.0
    _bidVolume1 = 0
    
    def __init__(self):
        pass

    @property 
    def InstrumentId(self):
        return self._instrumentId
      
    @InstrumentId.setter 
    def InstrumentId(self,value):
        self._instrumentId = value
      
    @property 
    def ExchangeId(self):
        return self._exchangeId
      
    @ExchangeId.setter 
    def ExchangeId(self,value):
        self._exchangeId = value
      
    @property
    def InstrumentType(self):
        return self._instrumentType

    @InstrumentType.setter
    def InstrumentType(self,value):
        self._instrumentType = value
      
    
    @property
    def DateTime(self):
        return self._naturalTime
      
    @DateTime.setter
    def DateTime(self,value):
        self._naturalTime = value
         
    @property
    def TimeNow(self):
        return self._naturalTime.TimeOfDay
      
    @property     
    def TradingDay(self):
        return self._tradingDay
      
    @TradingDay.setter
    def TradingDay(self,value):
        self._tradingDay = value
      
    @property
    def Quote(self):
        return self._quote
      
    @Quote.setter
    def Quote(self,value):
        self._quote = value

    @property
    def LocalTime(self):
        return self._localTime

    @LocalTime.setter
    def LocalTime(self, value):
        self._localTime = value

      
    # @property
    # def AskPrice1(self):
    #     return self._quote.AskPrice1

    # @AskPrice1.setter
    # def AskPrice1(self,value):
    #     self._quote.AskPrice1 = value
      
    # @property
    # def AskVolume1(self):
    #     return self._quote.AskVolume1

    # @AskVolume1.setter
    # def AskVolume1(self,value):
    #     self._quote.AskVolume1 = value
    
    # @property
    # def BidPrice1(self):
    #     return self._quote.BidPrice1
 
    # @BidPrice1.setter
    # def BidPrice1(self,value):
    #     self._quote.BidPrice1 = value

    # @property
    # def BidVolume1(self):
    #     return self._quote.BidVolume1

    # @BidVolume1.setter
    # def BidVolume1(self,value):
    #     self._quote.BidVolume1 = value

    @property
    def AskPrice1(self):
        return self._askPrice1

    @AskPrice1.setter
    def AskPrice1(self,value):
        self._askPrice1 = value
      
    @property
    def AskVolume1(self):
        return self._askVolume1

    @AskVolume1.setter
    def AskVolume1(self,value):
        self._askVolume1 = value
    
    @property
    def BidPrice1(self):
        return self._bidPrice1
 
    @BidPrice1.setter
    def BidPrice1(self,value):
        self._bidPrice1 = value

    @property
    def BidVolume1(self):
        return self._bidVolume1

    @BidVolume1.setter
    def BidVolume1(self,value):
        self._bidVolume1 = value
    
    @property 
    def PreClosePrice(self):
        return self._preClosePrice

    @PreClosePrice.setter
    def PreClosePrice(self, value): 
        self._preClosePrice = value
      
    @property 
    def OpenPrice(self):
        return self._openPrice
    
    @OpenPrice.setter
    def OpenPrice(self,value):  
        self._openPrice = value
      
    
    @property 
    def HighPrice(self):
        return self._highPrice
    
    @HighPrice.setter
    def HighPrice(self,value):  
        self._highPrice = value
       
    @property 
    def LowPrice(self):
        return self._lowPrice
    
    @LowPrice.setter
    def LowPrice(self,value):    
        self._lowPrice = value
      
    
    @property 
    def LastPrice(self):
        return self._lastPrice
      
    @LastPrice.setter
    def LastPrice(self,value):
        self._lastPrice = value
      
    @property 
    def Iopv(self):
        return self._iopv
    
    @Iopv.setter
    def Iopv(self,value):    
        self._iopv = value
       
    @property 
    def Volume(self):
        return self._volume

    @Volume.setter 
    def Volume(self,value):
        self._volume = value
        
    @property 
    def Turnover(self):
        return self._turnover

    @Turnover.setter 
    def Turnover(self,value):
        self._turnover = value
     
    @property 
    def UpLimit(self):
        return self._upLimitPrice
    
    @UpLimit.setter
    def UpLimit(self,value):
        self._upLimitPrice = value
      
    
    @property 
    def DropLimit(self):
        return self._dropLimitPrice
    
    @DropLimit.setter
    def DropLimit(self,value):
        self._dropLimitPrice = value
        
    @property 
    def OpenInterest(self):
        return self._openInterest
    
    @OpenInterest.setter
    def OpenInterest(self,value):  
        self._openInterest = value
      
    @property 
    def PreOpenInterest(self):
        return self._preOpenInterest

    @PreOpenInterest.setter 
    def PreOpenInterest(self,value):
        self._preOpenInterest = value
     
    @property 
    def PreSettlementPrice(self):
        return self._preSettlementPrice
    
    @PreSettlementPrice.setter
    def PreSettlementPrice(self,value):
        self._preSettlementPrice = value
       
    @property 
    def Change(self):
        # if (self.PreSettlementPrice > 0.0):
        #   return math.Round((self.LastPrice / self.PreSettlementPrice - 1.0) * 100.0, 4)
        # if (self.PreClosePrice > 0.0):
        #   return math.Round((self.LastPrice / self.PreClosePrice - 1.0) * 100.0, 4)
        return 0.0
       
    @property 
    def IfUpLimit(self):
        if (self.AskPrice1 <= 0.0):
          return self.BidPrice1 > 0.0
        return False
    
    @property
    def IfDropLimit(self):
        if (self.BidPrice1 <= 0.0):
          return self.AskPrice1 > 0.0
        return False
    
    @property
    def Status(self):
        return self._status

    @Status.setter 
    def Status(self,value):   
        self._status = value

    @property
    def BidNumOrder1(self):
        return self.Quote.BidNumOrder1
    
    @property
    def AskNumOrder1(self):
        return self.Quote.AskNumOrder1
        