from j5basic import TimeUtils
from j5test import Utils
import datetime
import time
import _thread
import threading

td = datetime.timedelta

def test_timedelta_roundtrip():
    timedelta = td(days=5,hours=23,minutes=12,seconds=59)
    timetuple = TimeUtils.timedelta_to_tuple(timedelta)
    assert timetuple == (5,23,12,59)
    assert TimeUtils.tuple_to_timedelta(timetuple) == timedelta

def test_timedelta_totals():
    assert TimeUtils.totalmilliseconds(td(microseconds=1)) == 0.001
    assert TimeUtils.totalmilliseconds(td(milliseconds=1)) == 1
    assert TimeUtils.totalmilliseconds(td(seconds=1)) == 1000
    assert TimeUtils.totalmilliseconds(td(seconds=-1)) == -1000
    assert TimeUtils.totalmilliseconds(td(seconds=1.25)) == 1250
    assert TimeUtils.totalmilliseconds(td(hours=1)) == 3600 * 1000
    assert TimeUtils.totalmilliseconds(td(days=1)) == 24 * 3600 * 1000
    assert TimeUtils.totalseconds(td(microseconds=1)) == 0
    assert TimeUtils.totalseconds(td(milliseconds=1)) == 0
    assert TimeUtils.totalseconds(td(seconds=1)) == 1
    assert TimeUtils.totalseconds(td(seconds=-1)) == -1
    assert TimeUtils.totalseconds(td(seconds=1.25)) == 1
    assert TimeUtils.totalseconds(td(hours=1)) == 3600
    assert TimeUtils.totalseconds(td(days=1)) == 24 * 3600
    assert TimeUtils.totalseconds_float(td(microseconds=1)) == 0.000001
    assert TimeUtils.totalseconds_float(td(milliseconds=1)) == 0.001
    assert TimeUtils.totalseconds_float(td(seconds=1)) == 1
    assert TimeUtils.totalseconds_float(td(seconds=-1)) == -1
    assert TimeUtils.totalseconds_float(td(seconds=1.25)) == 1.25
    assert TimeUtils.totalseconds_float(td(hours=1)) == 3600
    assert TimeUtils.totalseconds_float(td(days=1)) == 24 * 3600
    assert TimeUtils.totalseconds_float(td(days=1.25, hours=3.6, seconds=4.2, milliseconds=9.8, microseconds=125)) == 24 * 3600 + 9 * 3600 + 36 * 60 + 4.2 + 0.0098 + 0.000125

def test_strftime():
    """Tests the adjusted strftime works with dates before 1900"""
    assert TimeUtils.strftime(datetime.datetime(1996,9,3,12,51,50), "%Y:%m:%d %H:%M:%S") == "1996:09:03 12:51:50"
    assert TimeUtils.strftime(datetime.datetime(1896,9,3,12,51,50), "%Y:%m:%d %H:%M:%S") == "1896:09:03 12:51:50"
    assert TimeUtils.strftime(datetime.datetime(1818,9,18,18,18,18), "%Y%m%d%H%M%S") == "18180918181818"
    assert TimeUtils.strftime(datetime.datetime(1822,9,22,22,22,22), "%Y%m%d%H%M%S") == "18220922222222"
    assert TimeUtils.strftime(datetime.datetime(1822,9,22,22,22,22), "%%Y%m%d%H%M%S") == "%Y0922222222"

def always_skip(*args, **kwargs):
    return True

@Utils.if_long_test_run()
def test_sequence():
    """Checks that the day names are in order from 1/1/1 until August 2000"""
    # from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/306860
    s = TimeUtils.strftime(datetime.date(1800, 9, 23),
                 "%Y has the same days as 1980 and 2008")
    if s != "1800 has the same days as 1980 and 2008":
        raise AssertionError(s)

    print("Testing all day names from 0001/01/01 until 2000/08/01")
    # Get the weekdays.  Can't hard code them; they could be
    # localized.
    days = []
    for i in range(1, 10):
        days.append(datetime.date(2000, 1, i).strftime("%A"))
    nextday = {}
    for i in range(8):
        nextday[days[i]] = days[i+1]

    startdate = datetime.date(1, 1, 1)
    enddate = datetime.date(2000, 8, 1)
    prevday = TimeUtils.strftime(startdate, "%A")
    one_day = datetime.timedelta(1)

    testdate = startdate + one_day
    while testdate < enddate:
        if (testdate.day == 1 and testdate.month == 1 and
            (testdate.year % 100 == 0)):
            print("Testing century", testdate.year)
        day = TimeUtils.strftime(testdate, "%A")
        if nextday[prevday] != day:
            raise AssertionError(str(testdate))
        prevday = day
        testdate = testdate + one_day

threadsrun = 0
@Utils.skip_test_for("This test does not reliably pass, as sometimes we do not hit the race condition, and everything is fine with strptime", always_skip)
def test_threading_fail():
    def f(event):
        try:
            for m in range(1,13):
                for d in range(1,29):
                    time.strptime("2010%02d%02d"%(m,d),"%Y%m%d")
            global threadsrun
            threadsrun += 1
        finally:
            event.set()
    threads = []
    for _ in range(10):
        threads.append(threading.Event())
        _thread.start_new_thread(f, (threads[-1],))
    for t in threads:
        t.wait()
    assert threadsrun != 10

threadsrun_ = 0
def test_threading_fix():
    def f(event):
        try:
            for m in range(1,13):
                for d in range(1,29):
                    TimeUtils.safestrptime("2010%02d%02d"%(m,d),"%Y%m%d")
            global threadsrun_
            threadsrun_ += 1
        finally:
            event.set()
    threads = []
    for _ in range(10):
        threads.append(threading.Event())
        _thread.start_new_thread(f, (threads[-1],))
    for t in threads:
        t.wait()
    assert threadsrun_ == 10


def test_functions():
    assert TimeUtils.utcnow()
    assert TimeUtils.localminutenow()
    assert TimeUtils.localsecondnow()
    assert TimeUtils.totalhours(datetime.timedelta(hours=4, minutes=10)) > 4
    assert TimeUtils.hoursandminutes(datetime.timedelta(seconds=4*3600 + 4*60 + 4)) == (4, 4)
    assert TimeUtils.str_to_timedelta(TimeUtils.timedelta_to_str(datetime.timedelta(hours=4, minutes=10)))
    assert TimeUtils.str_to_timedelta(TimeUtils.timedelta_to_str(datetime.timedelta(days=1, hours=4, minutes=10)))

    assert TimeUtils.timetuple2datetime((2019, 8, 4, 5, 4, 3, 200))