#!/usr/bin/env python
# -*- coding: utf-8 -*-

from amarettopy.lib import *
from amarettopy.const import *
import sys,math
from pprint import pprint

# ノイジーなので2分探索やめておく

def _cost(amaretto, devId, cur, x, span_ms = 1000):

    try:
        amaretto.set_calibration_data(devId, x)
        amaretto.ready(devId)

        amaretto.set_ref_current(devId, cur)
        time.sleep(span_ms/1000)
        vplus = amaretto.query_servo_status(devId)[QSSR_IDX_VEL]
        amaretto.set_ref_current(devId, 0)
        time.sleep(0.5)
        amaretto.set_ref_current(devId, -cur)
        time.sleep(span_ms/1000)
        vminus = amaretto.query_servo_status(devId)[QSSR_IDX_VEL]
        amaretto.set_ref_current(devId, 0)
        time.sleep(0.5)

        amaretto.stop(devId) # out-of-control
        amaretto.hold(devId)

        if vplus <= 0 or vminus >= 0:
            print(x, vplus, vminus, "N/A")
            return math.inf
        else:
            ret = abs(vplus + vminus) / abs(vplus - vminus)
            print(x, vplus, vminus, abs(vplus + vminus), abs(vplus - vminus), ret)
            return  ret

    except InvalidOperationError:
        print("invalid operation")
        print(amaretto.query_servo_status(devId))
        return math.inf
    except WaitUntilTimeoutError:
        print("timeout")
        print(amaretto.query_servo_status(devId))
        return math.inf


def calibrate(amaretto, devId, current=2000, span_ms=1000):
    """

    キャリブレーションを行う

    Parameters
    ----------
    devId : int
        デバイスID
    current: int
        指令電流値
    """

    # rough search

    resolution = 256
    rough_skip = 16

    assert(resolution % rough_skip == 0)

    amaretto.ready(devId)

    rough_search_result = []

    for x in range(0, resolution, rough_skip):
        rough_search_result.append((x, _cost(amaretto, devId, current, x, span_ms)))

    rough_best = sorted(rough_search_result, key= lambda a : a[1])[0]

    #pprint(candidates)
    rough_best_idx = rough_best[0]
    rough_best_val = rough_best[1]

    if rough_best_val == math.inf:
        sys.exit("candidates are not found")

    end_idx   = (rough_best_idx + rough_skip) % resolution
    start_idx = (rough_best_idx - rough_skip) % resolution

    start_val = [v for (i,v) in rough_search_result if i == start_idx][0]
    end_val   = [v for (i,v) in rough_search_result if i == end_idx][0]

    if start_val == math.inf:
        start_idx = rough_best_idx
        start_val = rough_best_val
    if end_val == math.inf:
        end_idx = rough_best_idx
        end_val = rough_best_val

    if start_idx == end_idx:
        sys.exit("calibration error: too small search range")

    fine_search_result = [(start_idx, start_val), (end_idx, end_val)]

    idx = start_idx

    while idx != end_idx:
        idx = (idx + 1) % resolution
        fine_search_result.append((idx, _cost(amaretto, devId, current, idx, span_ms)))

    best = sorted(fine_search_result, key= lambda a : a[1])[0]

    print("result: ", best)

    amaretto.set_calibration_data(devId, best[0])


