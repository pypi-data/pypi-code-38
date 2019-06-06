# encoding: utf-8
from __future__ import print_function

import os

from .interpreter_bridge import InterpreterBridge
from .errors import InvalidScriptName


class MatlabRunner(InterpreterBridge):

    NAME = "MATLAB"
    EXTRA_ARGS = ["-nodisplay", "-nodesktop", "-nojvm", "-nosplash"]
    MSG_MARKER = "!!!"
    TEMPLATE = """

    clear;
    exit_code__ = 0
    try

        {command};

    catch ME

        exit_code__ = 1
        disp('{MSG_MARKER}ERROR:START');
        disp(ME);
        if length(ME.stack) > 0
            disp('STACK :');
            for k=1:length(ME.stack)
                disp(sprintf('STACK ELEMENT %d', k))
                disp(ME.stack(k))
            end
        end
        disp('{MSG_MARKER}ERROR:END');

    end
    disp(sprintf('{MSG_MARKER}EXITCODE:%d', exit_code__));
    disp('{MSG_MARKER}FINISHED');
    """

    def run_script(self, path_to_script, in_file_path, out_file_path, verbose=False):
        file_name = os.path.basename(path_to_script)
        if file_name != "conversion.m":
            raise InvalidScriptName(
                "script at {} must have name 'conversion.m'".format(path_to_script)
            )

        script_folder = os.path.dirname(path_to_script)

        code = """
        saved_path = path;
        path(saved_path, '{script_folder}');
        try
            conversion('{in_file_path}', '{out_file_path}');
        catch ME
            path(saved_path);
            rethrow(ME)
        end
        path(saved_path);
        """.format(
            **locals()
        )

        return self.run_command(code, verbose=verbose)
