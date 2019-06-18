"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Callable

import pyjamas.pjscore as pjscore
from pyjamas.pjsthreads import Thread


class RCallback():
    def __init__(self, ui: pjscore.PyJAMAS):
        """

        :type ui: pyjamas.PyJAMAS
        """
        super(RCallback, self).__init__()

        self.pjs = ui

    def launch_thread(self, run_fn: Callable, params: dict = None, progress_fn: Callable = None, result_fn: Callable = None, stop_fn: Callable = None, error_fn: Callable = None, finished_fn: Callable = None):
        athread = Thread(run_fn)

        for a_param in params:
            if a_param == 'progress' and params.get(a_param):
                athread.kwargs['progress_signal'] = athread.signals.progress
            elif a_param == 'stop' and params.get(a_param):
                athread.kwargs['stop_signal'] = athread.signals.stop
            elif a_param == 'error' and params.get(a_param):
                athread.kwargs['error_signal'] = athread.signals.error
            elif a_param == 'finished' and params.get(a_param):
                athread.kwargs['finished_signal'] = athread.signals.finished
            elif a_param == 'result' and params.get(a_param):
                athread.kwargs['result_signal'] = athread.signals.result
            else:
                athread.kwargs[a_param] = params.get(a_param)

        if progress_fn is not None and progress_fn is not False:
            athread.signals.progress.connect(progress_fn)

        if error_fn is not None and error_fn is not False:
            athread.signals.error.connect(error_fn)

        if result_fn is not None and result_fn is not False:
            athread.signals.result.connect(result_fn)

        if stop_fn is not None and stop_fn is not False:
            athread.signals.stop.connect(stop_fn)

        if finished_fn is not None and finished_fn is not False:
            athread.signals.finished.connect(finished_fn)

        self.pjs.threadpool.start(athread)

    def finished_fn(self):
        self.pjs.repaint()

    def stop_fn(self, stop_message: str):
        self.pjs.statusbar.showMessage(stop_message)

    def progress_fn(self, n: int):
        self.pjs.statusbar.showMessage(f" {n}% completed")

