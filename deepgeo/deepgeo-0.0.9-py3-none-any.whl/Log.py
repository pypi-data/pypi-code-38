#-*- coding: utf-8 -*-
import datetime
import Utils as utils


# 1.2 version : Absorption
class Log:
    def __init__(self, path, is_print=True, is_log=True, max_title=43):
        print("============== LOG INITIALIZE =============")
        self._path_ = utils.create_folder(path)
        self._isPrint_ = is_print
        self._isLog_ = is_log
        self._maxTitle_ = max_title
        self.title("LOG ACTIVATE")

    def __del__(self):
        print("============== LOG SHUTDOWN  ==============")

    def title(self, title):
        size = self._maxTitle_ - len(title) - 2
        if size % 2 == 1:
            title += " "
            size -= 1
        size /= 2
        bar = ""
        for i in range(int(size)):
            bar += "="
        self.write(bar+" "+title+" "+bar, is_date=False)

    def write(self, text='', is_date=True):
        info_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " > "
        if is_date is False:
            info_date = ""

        if self._isLog_:
            file_name = datetime.datetime.now().strftime("%Y-%m-%d")
            file_name = file_name.replace("-", "") + ".log"
            f = open(self._path_ + file_name, 'a')
            try:
                data = info_date + str(text) + "\n"
            except ValueError:
                data = "DATA FORMAT(STRING) ERROR"
            f.write(data)
            f.close()
        if self._isPrint_:
            print(info_date + text)


"""
    # Manual
    log = Log("d:\\log")
    log = Log("d:\\log\\")
    log = Log("d:/log")
    log = Log("d:/log/")
    
    log = Log("d:/log/", False)
    log = Log("d:/log/", False, False)
    log = Log("d:/log/", False, False, 20)
    
    log = Log(path="d:/log")
    log = Log(path="d:/log", is_print=False)
    log = Log(path="d:/log", is_log=False)
    log = Log(path="d:/log", max_title=20)
    log = Log(path="d:/log", is_print=False, is_log=False)
    log = Log(path="d:/log", is_print=False, max_title=20)
    log = Log(path="d:/log", is_log=False, max_title=20)
    log = Log(path="d:/log", is_print=False, is_log=False, max_title=20)
    
    log.write("test")
    log.title("test")
"""