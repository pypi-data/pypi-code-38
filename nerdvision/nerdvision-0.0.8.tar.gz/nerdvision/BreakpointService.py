import logging
import os
import sys
import threading

from nerdvision import settings
from nerdvision.ContextUploadService import ContextUploadService
from nerdvision.FrameProcessor import FrameProcessor
from nerdvision.models.EventSnapshot import Watcher

our_logger = logging.getLogger("nerdvision")


class BreakpointService(object):

    def __init__(self, session_id):
        self.breakpoints = {}
        self.var_id = 1
        self.context_service = ContextUploadService(session_id)
        sys.settrace(self.trace_call)
        threading.settrace(self.trace_call)

    def trace_call(self, frame, event, arg):
        if len(self.breakpoints) == 0:
            return None

        lineno = frame.f_lineno
        filename = frame.f_code.co_filename

        breakpoints_for = self.breakpoints_for(filename)

        if settings.is_point_cut_debug_enabled():
            our_logger.debug("Found %s breakpoints for %s", len(breakpoints_for), filename)

        if event == "call" and len(breakpoints_for) == 0:
            return None

        if event == "line":
            bps = self.find_match(breakpoints_for, lineno, frame)
            if len(bps) > 0:
                processor = FrameProcessor()
                processor.process_frame(frame)
                for bp in bps:
                    self.process_watches(bp, frame, processor)
                    self.context_service.send_event(processor.event, bp, processor.watchers)

        return self.trace_call

    def next_id(self):
        self.var_id = self.var_id + 1
        return self.var_id

    def dump(self, obj):
        for attr in dir(obj):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))

    def process_request(self, response):
        our_logger.debug("Processing breakpoints %s", response)
        new_breakpoints = {}
        for _breakpoint in response.breakpoints:
            if _breakpoint.args['class'] in new_breakpoints:
                new_breakpoints[_breakpoint.args['class']].append(_breakpoint)
            else:
                new_breakpoints[_breakpoint.args['class']] = [_breakpoint]
        self.breakpoints = new_breakpoints
        our_logger.debug("New breakpoint configuration %s", self.breakpoints)

    def breakpoints_for(self, filename):
        basename = os.path.basename(filename)

        if settings.is_point_cut_debug_enabled():
            our_logger.debug("Searching for breakpoint for %s", basename)

        if basename in self.breakpoints:
            breakpoints_basename_ = self.breakpoints[basename]
            return breakpoints_basename_
        else:
            return []

    def find_match(self, breakpoints_for, lineno, frame):
        bps = []
        for bp in breakpoints_for:
            if bp.line_no == lineno:
                if bp.condition is not None and bp.condition != "" and self.condition_matches(bp, frame):
                    bps.append(bp)
                elif bp.condition is None or bp.condition == "":
                    bps.append(bp)
        return bps

    @staticmethod
    def condition_matches(bp, frame):
        our_logger.debug("Executing condition evaluation: %s", bp.condition)
        try:
            result = eval(bp.condition, None, frame.f_locals)
            our_logger.debug("Condition result: %s", result)
            if result:
                return True
            return False
        except Exception as e:
            our_logger.debug("Error evaluating condition %s", bp.condition, e)
            return False

    @staticmethod
    def process_watches(bp, frame, processor):
        if not hasattr(bp, "named_watchers"):
            our_logger.debug("No watchers for breakpoint %s", bp.breakpoint_id)
            return
        watches = bp.named_watchers
        for watch in watches:
            watch_ = watches[watch]
            our_logger.debug("Evaluating watcher: %s -> %s", watch, watch_)
            if watch_ is not None and watch_ != "":
                try:
                    eval_result = eval(watch_, None, frame.f_locals)

                    type_ = type(eval_result)
                    hash_ = str(id(eval_result))
                    next_id = processor.next_id()

                    watcher = Watcher(watch, watch_)

                    processor.process_variable(hash_, watch, next_id, watcher, type_, eval_result, 0)
                    processor.add_watcher(watcher)
                except Exception as e:
                    our_logger.debug("Error evaluating watcher %s", watch_, e)
        return
