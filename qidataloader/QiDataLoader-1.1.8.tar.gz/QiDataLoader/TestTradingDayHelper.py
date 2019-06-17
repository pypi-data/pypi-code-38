from QiDataLoader.TradingDayHelper import TradingDayHelper
import datetime

td = TradingDayHelper()
day = td.GetPreTradingDay(datetime.datetime(2009,5,5))
print(day)