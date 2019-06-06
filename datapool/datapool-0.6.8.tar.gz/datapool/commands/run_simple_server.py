import os
import queue
import signal
import threading
import time

from prometheus_client import Gauge

from datapool.dispatcher import Dispatcher
from datapool.instance.config_handling import read_config
from datapool.instance.landing_zone_structure import lock_file

from ..database import check_if_tables_exist, setup_db
from ..errors import InvalidOperationError
from ..http_server import run_http_server_in_background
from ..logger import get_cmdline_logger
from ..observer import (CREATED_EVENT, MODIFIED_EVENT, shutdown_observer,
                        start_observer)
from ..utils import is_server_running, remove_pid_file, write_pid_file

queue_size = Gauge("dp_queue_size", "number of files in queue waiting to be processed")


def run_simple_server(
    verbose, print_ok, print_err, schedule_existing_files=True, still_running=None
):

    config = read_config()
    if config is None:
        print_err("- no config file found. please run 'pool init-config' " "first.")
        return 1

    if is_server_running(config):
        print_err("- datapool server is already running")
        return 1

    with get_cmdline_logger(verbose), run_http_server_in_background(
        config.http_server, print_ok
    ):

        try:
            already_setup = check_if_tables_exist(config.db)
        except InvalidOperationError as e:
            print_err("+ can not check database: {}".format(e))
            return 1
        if not already_setup:
            print_ok("- setup fresh db")
            try:
                setup_db(config.db, verbose=verbose)
            except InvalidOperationError as e:
                print_err("+ can not setup database: {}".format(e))
                return 1
        else:
            print_ok("- db already setup")

        if config.julia.executable:

            print_ok("- check startup julia")
            from datapool.julia_runner import JuliaRunner

            r = JuliaRunner(config.julia.executable)
            r.start_interpreter()
            ok = r.is_alive()
            if not ok:
                print_err("+ julia startup failed")
                return 1

        setup = _setup_simple_server(
            config, print_ok, print_err, schedule_existing_files, still_running
        )
        if setup is None:
            return 1
        print_ok("- observe {} now".format(config.landing_zone.folder))
        _simple_server_loop(still_running, setup, config, print_ok, print_err)

    print_ok("+ done", fg="green")

    return 0


def _setup_simple_server(
    config, print_ok, print_err, schedule_existing_files, still_running
):

    dispatcher = Dispatcher(config, info=print_ok)
    q = queue.Queue()
    root_folder = config.landing_zone.folder

    def call_back(event, rel_path, timestamp):
        if event not in (CREATED_EVENT, MODIFIED_EVENT):
            if rel_path == lock_file:
                print_ok("- removed update lock for landing zone")
            else:
                if not os.path.basename(rel_path).startswith("."):
                    print_err("- ignored event '{}' for {}".format(event, rel_path))
        else:
            if rel_path == lock_file:
                print_ok("- lock landing zone for updating")
            else:
                q.put((event, rel_path, timestamp))
                queue_size.set(q.qsize())

    try:
        observer = start_observer(root_folder, call_back, schedule_existing_files)
    except Exception as e:
        print_err("- could not start observer: {}".format(e))
        return None

    return q, dispatcher, observer


def _simple_server_loop(still_running, setup, config, print_ok, print_err):

    q, dispatcher, observer = setup

    def _shutdown(signum=None, frame=None):
        nonlocal still_running
        print()
        print_ok("- received signal {}".format(signum or "UNKNOWN"))
        while dispatcher.currently_dispatching:
            print_ok(
                "- waiting for dispatcher to finish: {} files in pipeline".format(
                    dispatcher.currently_dispatching
                )
            )
            time.sleep(1)

        print_ok("- shutdown observer")
        shutdown_observer(observer)
        print_ok("- observer shutdown")
        still_running = lambda: False
        print_ok("- shutdown done")
        remove_pid_file(config)

    def shutdown(signum=None, frame=None):
        # run in the bg to wait for dispatcher to finish, else this
        # would block the dispatcher.
        t = threading.Thread(target=_shutdown, args=(signum, frame))
        t.start()

    old_handlers = {}
    for sig in (signal.SIGTERM, signal.SIGHUP):
        old_handler = signal.signal(sig, shutdown)
        old_handlers[sig] = old_handler

    try:
        write_pid_file(config)
        while still_running is None or still_running():
            try:
                event, rel_path, timestamp = q.get(timeout=.01)
            except queue.Empty:
                continue

            # we ignore dot files:
            if os.path.basename(rel_path).startswith("."):
                continue

            print_ok("- dispatch {}".format(rel_path))
            results = dispatcher.dispatch(rel_path, timestamp)
            for result in results:
                if isinstance(result, str):
                    print_ok("  {}".format(result))
                else:
                    print_err("  error: {}".format(result))
            print_ok("  dispatch done")
            queue_size.set(q.qsize())

    except KeyboardInterrupt:
        shutdown()
    finally:
        remove_pid_file(config)
