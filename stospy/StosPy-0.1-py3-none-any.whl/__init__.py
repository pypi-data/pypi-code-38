import os
import time
from logging import getLogger

import psutil
from threading import Thread

from .base_classes import SwappableObject
from .config import config
from .runtime import runtime

__author__ = "Alex Barcelo <alex.barcelo@bsc.es>"
__version__ = "0.1"

__all__ = [
    "SwappableObject",
    "wait",
    "sync",
]

logger = getLogger(__name__)


def _sync():
    """Check the memory pressure and trigger it at the backend if needed."""
    process = psutil.Process(os.getpid())
    used_mem_mb = process.memory_info().rss // 1024 // 1024
    if used_mem_mb >= config.MEMORY_PRESSURE_THRESHOLD:
        logger.debug("Used memory: %d MB > %d MB, triggering memory pressure event",
                     used_mem_mb, config.MEMORY_PRESSURE_THRESHOLD)
        runtime.backend.trigger_memory_pressure()
        return True
    else:
        return False


def sync():
    """Explicit call to sync"""
    logger.info("Explicit call to sync() received, checking memory pressure...")
    if not _sync():
        logger.debug("No memory pressure, noop")


def wait():
    """Call the backend to do a blocking wait on the backend."""
    logger.info("Received a call to wait()")
    runtime.backend.wait()


def memory_supervisor():
    """Eternal watcher for the memory pressure threshold."""
    logger.info("Setting up a memory supervisor each %d seconds",
                config.MEMORY_PRESSURE_REFRESH)
    while True:
        time.sleep(config.MEMORY_PRESSURE_REFRESH)
        _sync()


mem_supervisor_th = Thread(target=memory_supervisor, daemon=True)
mem_supervisor_th.start()
