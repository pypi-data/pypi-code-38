import datetime

class QiCore():
    @staticmethod
    def ConvertCSharpTicksToLinuxTicks(value):
        if(value == 0):
            return value
        cSharpTicks1970 = 621355968000000000
        linuxTicks = (value - cSharpTicks1970) / 10000000
        timeZone = 28800
        linuxTicks = linuxTicks - timeZone
        return linuxTicks

    @staticmethod
    def ConvertCSharpTicksToPyDateTime(value):
        pyTime = datetime.datetime.fromtimestamp(QiCore.ConvertCSharpTicksToLinuxTicks(value))
        return pyTime