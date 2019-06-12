#
# Copyright (c) 2013-2019 Quarkslab.
# This file is part of IRMA project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the top-level directory
# of this distribution and at:
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# No part of the project, including this file, may be copied,
# modified, propagated, or distributed except according to the
# terms contained in the LICENSE file.


from .exceptions import IrmaValueError
import enum


# =============
#  Return code
# =============

class IrmaReturnCode:
    success = 0
    warning = 1
    error = -1
    label = {success: "success",
             warning: "warning",
             error: "error"}


# ==============================
#  Scan status (Brain/Frontend)
# ==============================

# TODO: change to enum.IntEnum
class IrmaScanStatus:
    empty = 0
    ready = 10
    uploaded = 20
    launched = 30
    processed = 40
    finished = 50
    flushed = 60
    # cancel
    cancelling = 100
    cancelled = 110
    # errors
    error = 1000
    # Probes 101x
    error_probe_missing = 1010
    error_probe_na = 1011
    # FTP 102x
    error_ftp_upload = 1020

    label = {empty: "empty",
             ready: "ready",
             uploaded: "uploaded",
             launched: "launched",
             processed: "processed",
             finished: "finished",
             cancelling: "cancelling",
             cancelled: "cancelled",
             flushed: "flushed",
             error: "error",
             error_probe_missing: "probelist missing",
             error_probe_na: "probe(s) not available",
             error_ftp_upload: "ftp upload error"
             }

    @staticmethod
    def is_error(code):
        return code >= IrmaScanStatus.error

    @staticmethod
    def filter_status(status, status_min=None, status_max=None):
        if status not in IrmaScanStatus.label.keys():
            raise IrmaValueError("Unknown scan status {0}".format(status))
        status_str = IrmaScanStatus.label[status]
        if status_min is not None and status < status_min:
            raise IrmaValueError("Wrong scan status [{0}]".format(status_str))
        if status_max is not None and status > status_max:
            raise IrmaValueError("Wrong scan status [{0}]".format(status_str))
        return

    @staticmethod
    def code_to_label(code):
        return IrmaScanStatus.label.get(code, "Unknown status code")


class ProbeStatus(enum.IntEnum):
    CANCELLED = -2
    ERROR = -1
    GOOD = 0
    BAD = 1
    NEUTRAL = 2


# ======================
#  Irma Probe Type Enum
# ======================

class IrmaProbeType:
    unknown = "unknown"
    antivirus = "antivirus"
    database = "database"
    deferred = "deferred"
    external = "external"
    metadata = "metadata"
    sandbox = "sandbox"
    tests = "tests"
    tools = "tools"
    from_label = {
        "unknown": unknown,
        "antivirus": antivirus,
        "database": database,
        "deferred": deferred,
        "external": external,
        "metadata": metadata,
        "sandbox": sandbox,
        "tests": tests,
        "tools": tools,
    }

    @staticmethod
    def normalize(probe_type):
        if probe_type not in IrmaProbeType.from_label.keys():
            return IrmaProbeType.unknown
        else:
            return IrmaProbeType.from_label[probe_type]


class ArtifactType(enum.IntEnum):
    LOG = 1
    PCAP = 2
    SCREENSHOT = 3
    MEMDUMP = 4
    EXTRACTED = 5
    DISASSEMBLY = 6
