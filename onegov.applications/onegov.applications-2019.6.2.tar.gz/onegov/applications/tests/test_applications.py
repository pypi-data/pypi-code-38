import multiprocessing
import os
import subprocess
import sys
import tempfile
import time


def spawn_command(path):
    env = os.environ.copy()
    env['PYTHONPATH'] = ':'.join(sys.path)

    stdout = tempfile.NamedTemporaryFile()

    process = subprocess.Popen(
        [sys.executable, '-m', 'pytest', path, '-x'],
        stdout=stdout,
        stderr=subprocess.STDOUT,
        env=env,
    )
    process.stdout_file = stdout

    return process


def print_result(process):
    print()
    process.stdout_file.seek(0)
    for line in process.stdout_file.readlines():
        print(line.decode('utf-8').rstrip('\n'))
    print(flush=True)


def run_single_application(applications):
    process = spawn_command(path=applications[1])

    while process.poll() is None:
        print('.', end='', flush=True)

        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            pass

        time.sleep(4.0)

    print_result(process)

    return process.returncode


def run_multiple_applications(applications):
    concurrent_jobs = multiprocessing.cpu_count()

    paths = [path for name, path in applications]
    processes = []

    def running_processes():
        return [p for p in processes if p.poll() is None]

    while paths or running_processes():

        print('.', end='', flush=True)

        for process in running_processes():
            try:
                process.wait(timeout=1.0)
                print_result(process)
            except subprocess.TimeoutExpired:
                pass

        for _ in range(len(running_processes()), concurrent_jobs):
            if paths:
                processes.append(spawn_command(paths.pop()))

        time.sleep(4.0)

    return max(p.returncode for p in processes)


def test_applications(applications):
    if len(applications) == 1:
        result = run_single_application(applications[0])
    else:
        result = run_multiple_applications(applications)

    assert result == 0
