
from datetime import datetime
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re
from ilib import inumber


class Loop:

    def __init__(self, title, len):
        self.title = title
        self.start_dt = datetime.now()
        self.count = 1
        self.len = len

    def report(self, addi_info='...'):
        if self.count <= self.len:
            cum_runtime = (datetime.now() - self.start_dt).total_seconds()
            avg_runtime = cum_runtime / self.count
            expected_total_runtime = avg_runtime * self.len
            expected_remaining_runtime = avg_runtime * (self.len - self.count)
            tpls = [
                ('전체예상시간', expected_total_runtime),
                ('잔여예상시간', expected_remaining_runtime),
                ('평균실행시간', avg_runtime),
            ]
            title = f"{self.title} --> {addi_info}"
            print(f"\n{'*'*60}\n {self.__class__} ({self.count}/{self.len})\n title + addi_info : {title}")
            for tpl in tpls:
                timeexp, unit = inumber.convert_timeunit(tpl[1])
                print(f" {tpl[0]} : {timeexp} ({unit})")
            self.count += 1

class Function:

    def __init__(self, currentframe, RunTimeout=60):
        self.start_dt = datetime.now().astimezone()
        self.middle_dt = self.start_dt
        self.inputs = currentframe.f_locals

        frameinfo = inspect.getframeinfo(frame=currentframe)
        self.filename = frameinfo.filename
        self.modulename = ''
        self.funcname = frameinfo.function

        #argvalues = inspect.getargvalues(frame=currentframe)
        #self.inputs = argvalues.locals

        self.RunTimeout = RunTimeout
        self.regs = ['^query', 'df|df\d+', '.+li', '^r$', '^whoami', '^soup', '^js']

    def set_invisible_regex(self, regs=[]):
        if isinstance(regs, list):
            self.regs += regs
        else:
            print("\n regs 는 리스트타입으로 입력해라.\n")
        return self

    def apply_invisible_inputs(self):
        """input_param_중에_list를_포함한_query는_프린트하지않는다"""
        invisibles = self.inputs.copy()
        for reg in self.regs:
            p = re.compile(pattern=reg)
            for key, val in self.inputs.items():
                if p.search(string=key) is not None:
                    del(invisibles[key])
        return invisibles

    def report_init(self):
        """함수가 시작되었음을 알리는 구분선과 입력변수를 프린트."""
        print(f"\n{'*'*60}\n {self.__class__} | {inspect.stack()[0][3]}")
        print(f" caller : {self.filename} | {self.funcname}")
        print(f" visible_inputs :")
        pp.pprint(self.apply_invisible_inputs())
        return self

    def report_mid(self, addi_info='addi_info'):
        print(f"\n{'*'*60}\n {self.__class__} | {inspect.stack()[0][3]}")
        print(f" caller : {self.filename} | {self.funcname} | {addi_info}")
        print(f" start_dt : {self.middle_dt}")
        self.interval_runtime = (datetime.now().astimezone() - self.middle_dt).total_seconds()
        self.middle_dt = datetime.now().astimezone()
        print(f" end_dt : {self.middle_dt}")
        t, unit = inumber.convert_timeunit(self.interval_runtime)
        print(f" interval_runtime : {t} ({unit})")
        return self

    def report_fin(self, addi_info=None):
        """함수실행시간 체크, 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사."""
        self.end_dt = datetime.now().astimezone()
        self.runtime = (datetime.now().astimezone() - self.start_dt).total_seconds()
        t, unit = inumber.convert_timeunit(self.runtime)
        print(f"\n{'*'*60}\n {self.__class__} | {inspect.stack()[0][3]}")
        print(f" caller : {self.filename} | {self.funcname} | {addi_info}")
        print(f" start_dt : {self.start_dt}")
        print(f" end_dt : {self.end_dt}")
        print(f" runtime : {t} ({unit})")
        return self
