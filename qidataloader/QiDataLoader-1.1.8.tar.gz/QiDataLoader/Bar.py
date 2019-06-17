import math
import time

class Bar:
    _high = -100000000.0
    _low = 100000000.0
    _instrumentId = ''
    _tradingDate = time.time()
    _beginTime = time.time()
    _endTime = time.time()
    _open = 0.0
    _close = 0.0
    _preClose = 0.0
    _volume = 0.0
    _turnover = 0.0
    _isComplete = False
    _openInterest = 0.0

    def __init__(self):
        pass

    @property
    def InstrumentId(self):
        return self._instrumentId

    @InstrumentId.setter
    def InstrumentId(self, value):
        self._instrumentId = value

    @property
    def TradingDate(self):
        return self._tradingDate

    @TradingDate.setter
    def TradingDate(self, value):
        self._tradingDate = value

    @property
    def BeginTime(self):
        return self._beginTime

    @BeginTime.setter
    def BeginTime(self, value):
        self._beginTime = value

    @property
    def EndTime(self):
        return self._endTime

    @EndTime.setter
    def EndTime(self, value):
        self._endTime = value

    @property
    def Duration(self):
        return self.EndTime - self.BeginTime

    @property
    def High(self):
        if (self._high < 1E-07) & (abs(self.Volume) < 1E-10):
            return self._preClose
        return self._high

    @High.setter
    def High(self, value):
        self._high = value

    @property
    def Open(self):
        if (self._open < 1E-07) & (abs(self.Volume) < 1E-10):
            return self._preClose
        return self._open

    @Open.setter
    def Open(self, value):
        self._open = value

    @property
    def Low(self):
        if (self._low < 1E-07) & (abs(self.Volume) < 1E-10):
            return self._preClose
        return self._low

    @Low.setter
    def Low(self, value):
        self._low = value

    @property
    def Close(self):
        if (self._close < 1E-07) & (abs(self.Volume) < 1E-10):
            return self._preClose
        return self._close

    @Close.setter
    def Close(self, value):
        self._close = value

    @property
    def PreClose(self):
        return self._preClose

    @PreClose.setter
    def PreClose(self, value):
        self._preClose = value

    @property
    def Volume(self):
        return self._volume

    @Volume.setter
    def Volume(self, value):
        self._volume = value

    @property
    def Turnover(self):
        return self._turnover

    @Turnover.setter
    def Turnover(self, value):
        self._turnover = value

    @property
    def OpenInterest(self):
        return self._openInterest

    @OpenInterest.setter
    def OpenInterest(self, value):
        self._openInterest = value

    # @property
    # def self[BarData barData]:
    #     switch (barData)    
    #       case BarData.Close:
    #         return self.Close
    #       case BarData.Open:
    #         return self.Open
    #       case BarData.High:
    #         return self.High
    #       case BarData.Low:
    #         return self.Low
    #       case BarData.Volume:
    #         return self.Volume
    #       case BarData.Turnover:
    #         return self.Turnover
    #       default:
    #         return 0.0

    @property
    def BarChange(self):
        num = 0.0
        if (abs(self.Open) > 1E-10):
            num = round(100.0 * (self.Close / self.Open - 1.0), 3)
        return num

    @property
    def Change(self):
        num = 0.0
        if (abs(self.PreClose) > 1E-10):
            num = round(100.0 * (self.Close / self.PreClose - 1.0), 3)
        return num

    def AddTick(self, tick):
        if (self._high < tick.LastPrice):
            self._high = tick.LastPrice
        if (self._low > tick.LastPrice):
            self._low = tick.LastPrice
        self._close = tick.LastPrice
        self.EndTime = tick.DateTime
        self.OpenInterest = tick.OpenInterest

    def AddBar(self, bar):
        if (self._high < bar.High):
            self._high = bar.High
        if (self._low > bar.Low):
            self._low = bar.Low
        self._close = bar.Close
        self.EndTime = bar.EndTime
        self.OpenInterest = bar.OpenInterest
        self.Volume += bar.Volume
        self.Turnover += bar.Turnover

    def OpenBar(self, begintime, tick, bar):
        self.BeginTime = begintime
        self._high = self._low = self._open = self._close = tick.LastPrice
        if (any(bar) == False):
            if (tick.HighPrice > 0.0) & (tick.HighPrice < 10000000000.0):
                self.High = tick.HighPrice
            if (tick.LowPrice > 0.0) & (tick.LowPrice < 10000000000.0):
                self.Low = tick.LowPrice
            if (tick.OpenPrice > 0.0) & (tick.OpenPrice < 10000000000.0):
                self.Open = tick.OpenPrice

        self.EndTime = tick.DateTime
        if (any(bar) == False):
            if tick.PreClosePrice > 0.0:
                self.PreClose = tick.PreClosePrice
            else:
                self.PreClose = tick.OpenPrice
        else:
            self.PreClose = bar.Close
        self.OpenInterest = tick.OpenInterest

    def OpenBarWithNewBar(self, newbar):
        self.BeginTime = newbar.BeginTime
        self.High = newbar.High
        self.Low = newbar.Low
        self.Open = newbar.Open
        self.Close = newbar.Close
        self.EndTime = newbar.EndTime
        self.Volume = newbar.Volume
        self.Turnover = newbar.Turnover
        self.PreClose = newbar.PreClose
        self.OpenInterest = newbar.OpenInterest

    def CloseBar(self, endtime):
        self.EndTime = endtime

    def Clone(self):
        bar = Bar()
        bar._instrumentId = self._instrumentId
        bar._beginTime = self._beginTime
        bar._endTime = self._endTime
        bar._high = self._high
        bar._open = self._open
        bar._low = self._low
        bar._close = self._close
        bar._preClose = self._preClose
        bar._volume = self._volume
        bar._turnover = self._turnover
        bar._isComplete = self._isComplete
        bar._openInterest = self._openInterest
        bar._tradingDate = self._tradingDate
        return bar

    def ToString(self):
        msg = "" + "[" + str(self.BeginTime) + "-" + str(self.EndTime) + "]"
        msg += "高" + str(self.High)
        msg += "开" + str(self.Open)
        msg += "低" + str(self.Low)
        msg += "收" + str(self.Close)
        msg += "量=" + str(self.Volume)
        msg += "额=" + str(self.Turnover)
        msg += "持仓" + str(self.OpenInterest)

        return msg
