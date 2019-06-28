import os
import argparse
import logging as log
import filelock as fl
from pathlib import Path
from signal import signal, SIGTERM
from contextlib import suppress, contextmanager
from .touchpad import SIGTOGGLE
from .watchdog import WatchDog

lockfp: Path = Path('/tmp') / 'linux-touchpad.lock'
pidfp: Path = Path(__file__).with_name('.pid')
lock = fl.FileLock(str(lockfp), timeout=1)


def start():
    """Try to begin process. Fail if lock exists."""
    with suppress(fl.Timeout), lock:
        watchdog = WatchDog()

        # Handle toggle and kill signals
        signal(SIGTOGGLE, watchdog.on_toggle)
        pidfp.write_text(str(os.getpid()))
        log.info('Starting watchdog.')
        watchdog.start()

def stop():
    """Kill existing process if exists."""
    with suppress(FileNotFoundError):
        pid = int(pidfp.read_text())
        pidfp.unlink()
        log.info(f'Killing {pid}.')
        os.kill(pid, SIGTERM)

def toggle():
    """Send toggle signal to existing process if exists."""
    with suppress(FileNotFoundError):
        pid = int(pidfp.read_text())
        log.info('Requesting Toggle.')
        os.kill(pid, SIGTOGGLE)


def main():
    items = {
        'start': start,
        'stop': stop,
        'toggle': toggle
    }
    parser = argparse.ArgumentParser(
        prog="linux-touchpad",
        description="Auto disable touchpad when mouse is detected."
    )
    parser.add_argument('command', choices=items)
    args = parser.parse_args()
    items[args.command]()


if __name__ == '__main__':
    main()
