#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import datetime
import concurrent.futures
from bin.config import config


def run_problem(program, nickname, command, instance):
    # pass the problem to the command
    invocation = "%s %s" % (command, instance)
    # get start time
    start = datetime.datetime.now().timestamp()
    # run command
    process = subprocess.Popen(
        invocation,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    # wait for it to complete
    try:
        process.wait(timeout=config["timeout"])
    # if it times out ...
    except subprocess.TimeoutExpired:
        # kill it
        # print('TIMED OUT:', repr(invocation), '... killing', process.pid, file=sys.stderr)
        os.killpg(os.getpgid(process.pid), signal.SIGINT)
        # set timeout result
        elapsed = config["timeout"]
        output = 'timeout (%.1f s)' % config["timeout"]
    # if it completes in time ...
    else:
        # measure run time
        end = datetime.datetime.now().timestamp()
        elapsed = end - start
        # get result
        stdout = process.stdout.read().decode("utf-8", "ignore")
        stderr = process.stderr.read().decode("utf-8", "ignore")
        output = stdout + stderr
    OUTPUT_HANDLERS[program](nickname, instance, output, elapsed)


# program, specification["id"], specification["command"], problems
def run_solver(args):
    program = args[0]
    nickname = args[1]
    command = args[2]
    instances = args[3]

    for instance in instances:
        run_problem(program, nickname, command, instance)


def signal_handler():
    print("KILLING!")
    try:
        sys.exit(0)
    except SystemExit:
        exit(0)


def bench(instances, handlers):
    global OUTPUT_HANDLERS
    OUTPUT_HANDLERS = handlers

    signal.signal(signal.SIGTERM, signal_handler)

    args = [[program, nickname, command, instances] for
            program, specifications in config["commands"].items() for
            nickname, command in specifications.items()]
    try:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(run_solver, args)
    except KeyboardInterrupt:
        print('Interrupted!')
        try:
            sys.exit(0)
        except SystemExit:
            exit(0)
