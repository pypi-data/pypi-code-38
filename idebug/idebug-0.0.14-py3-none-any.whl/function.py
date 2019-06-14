
from datetime import datetime
import inspect
import pprint
pp = pprint.PrettyPrinter(indent=2)
import re
from ilib import inumber


class Function:

    def __init__(self, currentframe, RunTimeout=60):
        self.start_dt = datetime.now().astimezone()
        self.currentframe = currentframe
        self.inputs = currentframe.f_locals

        frameinfo = inspect.getframeinfo(frame=currentframe)
        self.filename = frameinfo.filename
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
        print(f" visible_inputs : {self.apply_invisible_inputs()}")
        return self

    def report_fin(self):
        """함수실행시간 체크, 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사."""
        self.end_dt = datetime.now().astimezone()
        self.runtime = (datetime.now().astimezone() - self.start_dt).total_seconds()
        t, unit = inumber.convert_timeunit(self.runtime)
        print(f"\n{'*'*60}\n {self.__class__} | {inspect.stack()[0][3]}")
        print(f" caller : {self.filename} | {self.funcname}")
        print(f" start_dt : {self.start_dt}")
        print(f" end_dt : {self.end_dt}")
        print(f" runtime : {t}")
        return self

class FuncReporter:

    def __init__(self, currentframe, RunTimeout=60):
        self.start_dt = datetime.now().astimezone()
        self.currentframe = currentframe
        self.inputs = currentframe.f_locals

        frameinfo = inspect.getframeinfo(frame=currentframe)
        self.filename = frameinfo.filename
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
        pp.pprint({
            'modulename': self.filename,
            'funcname':self.funcname,
            'visible_inputs':self.apply_invisible_inputs()})
        return self

    def report_fin(self):
        """함수실행시간 체크, 함수실행시간에 영향을 미치는 입력 파라미터는 무엇인지 나중에 조사."""
        self.end_dt = datetime.now().astimezone()
        self.runtime = (datetime.now().astimezone() - self.start_dt).total_seconds()
        t, unit = inumber.convert_timeunit(self.runtime)
        print(f"\n{'*'*60}\n {self.__class__} | {inspect.stack()[0][3]}")
        pp.pprint({
            'modulename': self.filename,
            'funcname': self.funcname,
            'start_dt': self.start_dt,
            'end_dt': self.end_dt,
            'runtime':t })
