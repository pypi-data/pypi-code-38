import datetime
import os

class TradingDayHelper:
    Days = []
    IsLoaded = False

    @staticmethod
    def Load():
        TradingDayHelper.Days.clear()
        now = datetime.datetime.now()
        for y in range(2010,now.year,1):
            fileName = os.path.split(os.path.realpath(__file__))[0] +  "\\TradingCalendar\\"+str(y)+".tc"
            for line in open(fileName, "r"):  # 设置文件对象并读取每一行文件
                nDate = int(line)
                year = nDate // 10000
                month = nDate % 10000 // 100
                day = nDate % 100
                dt = datetime.date(year, month, day)
                TradingDayHelper.Days.append(dt)
        TradingDayHelper.IsLoaded = True

    @staticmethod
    def GetPreTradingDay(t):
        if TradingDayHelper.IsLoaded == False:
            TradingDayHelper.Load()

        if t in TradingDayHelper.Days:
            num = TradingDayHelper.Days.index(t)
            num2 = num - 1;
            num2 = max(0, num2)
            return TradingDayHelper.Days[num2]
        return t + datetime.timedelta(days=-1)
