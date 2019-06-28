#!/usr/bin/env python3

import boto3
import json
import time
import datetime
import sys
import pickle
import os


def thread_worker(q, current_list_item, results, s_timeout, kwargs, function):

    run_timeout = False

    if s_timeout <= 0:
        run_timout = True

    #q.put("starting process")

    function_results = function(current_list_item, kwargs)

    if function_results == None:
        pass
    else:
        results[current_list_item['Key']] = function_results

    #q.put("finished function")

    #q for status messaging to parent
    #current_list_item: item we want to act on
    #results? Wtf is this for?
    #s_timeout how long to run before dipping out
    #kwargs use if needed
