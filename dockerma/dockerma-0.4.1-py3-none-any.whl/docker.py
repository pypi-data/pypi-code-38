#!/usr/bin/env python
# -*- coding: utf-8
import logging
import subprocess

LOG = logging.getLogger(__name__)


class Docker(object):
    def __init__(self, options, remaining):
        self._options = options
        self._remaining = remaining

    def execute(self, *args):
        self._execute(args)

    def get_output(self, *args):
        return self._execute(args, True)

    def _execute(self, args, output=False):
        cmd = ["docker"]
        o = self._options
        for bool_option in ("debug", "tls", "tlsverify"):
            if getattr(o, bool_option):
                cmd.append("--{}".format(bool_option))
        for value_option in ("config", "log_level", "tlscacert", "tlscert", "tlskey"):
            value = getattr(o, value_option)
            if value:
                cmd.append("--{}".format(value_option.replace("_", "-")))
                cmd.append(value)
        if o.host:
            for h in o.host:
                cmd.extend(("--host", h))
        cmd.extend(args)
        if output:
            LOG.debug("Getting output from: %r", cmd)
            return subprocess.check_output(cmd, universal_newlines=True)
        else:
            LOG.debug("Executing command: %r", cmd)
            subprocess.check_call(cmd)
