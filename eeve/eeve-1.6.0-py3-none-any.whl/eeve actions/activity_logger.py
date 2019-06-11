from datetime import datetime, timedelta
import math
from time import sleep
from travel_backpack import Singleton, thread_encapsulation, time_now_to_string, except_and_print
import win32gui, win32process, psutil
import os
from dataclasses import dataclass

timer_runing = False
timer_initialized = False


@dataclass
class Window:
    name: str
    time: timedelta


@dataclass
class Process:
    name: str
    time: timedelta
    windows: 'Dict[Window]'


class Timer(metaclass=Singleton):
    def __init__(self, t=5 * 60, p='activity.log'):
        global timer_initialized
        print('starting timer')
        self.last_move = datetime.now()
        self.day = datetime.now().day
        self.active = False
        self.t = t
        self.log_path = p
        self.countdown()
        timer_initialized = True
        self.indef_name = '[none]'
        self.last_window_name = self.indef_name
        self.last_process_name = self.indef_name
        self.time_count_helper_process = self.last_move
        self.time_count_helper_window = self.last_move
        self.time_count_helper_summary_hourly = self.last_move
        self.proc_log = {self.indef_name: Process(name=self.indef_name, time=timedelta(), windows=dict())}

    @thread_encapsulation
    def countdown(self):
        @except_and_print
        def do_update():
            print('active:', self.active, "-- time 'til inactivity:",
                  self.t - (datetime.now() - self.last_move).total_seconds())
            if self.active and (datetime.now() - self.last_move).total_seconds() >= self.t:
                self.active = False
                print('System deactivated')
                with open(self.log_path, 'a') as f:
                    f.write(f'[{time_now_to_string()}] System Idle\n')

            self.update_window()

        while True:
            do_update()
            sleep(1)

    def update(self, print_proc_name=False):
        if not self.active:
            self.active = True
            print('System activated')
            with open(self.log_path, 'a') as f:
                time = round_up_time_delta(datetime.now() - self.last_move)
                f.write(f'\n\n\n[{time_now_to_string()}] System resume from {time} idle time\n')

        self.last_move = datetime.now()
        if print_proc_name:
            sleep(0.1)
            self.update_window()

    def update_window(self):
        try:
            if self.active:
                active_process, active_window = self.get_active_window()
            else:
                active_process, active_window = '[inactivity]', self.last_window_name
        except psutil.NoSuchProcess:
            print('Failed to grab process')
            return

        n = datetime.now()
        d = n.day
        if self.day != d:
            self.make_summary(True, n)
            self.day = d
        if os.path.isfile('dump.txt'):
            self.make_summary(False, n)
            os.remove('dump.txt')
        if os.path.isfile('clear.txt'):
            self.make_summary(True, n)
            os.remove('clear.txt')
        if n - self.time_count_helper_summary_hourly > timedelta(hours=1):
            self.time_count_helper_summary_hourly = n
            self.make_summary(False, n, '.summary.hourly')

        # initializes active process if it does not exists
        if active_process not in self.proc_log:
            self.proc_log[active_process] = Process(
                name=active_process, time=timedelta(), windows=dict())  # (time spent in seconds, window names)

        last_proc_info = self.proc_log[self.last_process_name].windows  # shortcut for last process's info

        if self.last_window_name not in last_proc_info:
            last_proc_info[self.last_window_name] = Window(name=self.last_window_name, time=timedelta())

        if active_window != self.last_window_name or active_process != self.last_process_name:
            last_proc_info[self.last_window_name].time += n - self.time_count_helper_window

            with open(self.log_path, 'a') as f:
                time = round_up_time_delta(n - self.time_count_helper_window)
                total_time = round_up_time_delta(last_proc_info[self.last_window_name].time)
                f.write(f'[{time_now_to_string()}] spent {time} on {self.last_window_name}.  {total_time} total\n' +
                        f'[{time_now_to_string()}] ---------------> {active_window}\n')

            self.last_window_name = active_window
            self.time_count_helper_window = n

        # if it changed, add time to the last one and prepare for the current
        if active_process != self.last_process_name:
            self.proc_log[self.last_process_name].time += n - self.time_count_helper_process
            self.last_process_name = active_process
            self.time_count_helper_process = n

    def get_active_window(self):
        fgw = win32gui.GetForegroundWindow()
        pid = win32process.GetWindowThreadProcessId(fgw)  #This produces a list of PIDs active window relates to
        name = psutil.Process(pid[-1]).name()
        return name, f'{name}: {win32gui.GetWindowText(fgw)}'

    def make_summary(self, delete: bool, n: datetime, postfix='.summary'):
        summ_name = postfix.join(os.path.splitext(self.log_path))
        with open(summ_name, 'a') as f:
            f.write(f'\n\n----------{n}---------\n')
            for proc_name, proc in sorted(self.proc_log.items(), key=lambda x: x[1].time, reverse=True):
                print(f'dumping to file:', proc)
                f.write(f'\n{proc_name}: {round_up_time_delta(proc.time)} total time\n')
                for window_name, wind in sorted(proc.windows.items(), key=lambda x: x[1].time, reverse=True):
                    percent = int(100 * wind.time / proc.time) if proc.time != timedelta(0) else '-'
                    f.write(f'\t{window_name}: {round_up_time_delta(wind.time)} total time ({percent}%)\n')
            if delete:
                self.proc_log = {self.indef_name: Process(name=self.indef_name, time=timedelta(), windows=dict())}


def round_up_time_delta(td: timedelta) -> timedelta:
    return timedelta(seconds=math.ceil(td.total_seconds()))


def log_activity():
    if timer_initialized:
        t = Timer()
        t.update()


def log_activity_and_current_window():
    if timer_initialized:
        t = Timer()
        t.update(True)


def initialize_logger(time, log_path):
    global timer_runing
    if not timer_runing:
        timer_runing = True
        Timer(t=time * 60, p=log_path)


actions = {
    'log activity': {
        'run': log_activity
    },
    'log activity and current window': {
        'run': log_activity_and_current_window
    },
    'start activity logger': {
        'run': initialize_logger
    }
}
