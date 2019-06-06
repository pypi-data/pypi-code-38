# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os

from .interpreter_bridge import InterpreterBridge


class JuliaRunner(InterpreterBridge):

    NAME = "JULIA"
    EXTRA_ARGS = ["-i", "--startup-file=no"]

    MSG_MARKER = "!!!"

    TEMPLATE = '''
    module _we_use_here_a_module_to_keep_the_workspace_clean
        exit_code__ = 0
        try
            {command}
        catch ex
            bt = stacktrace(catch_backtrace())
            global exit_code__
            exit_code__ = 1
            println()
            println("{MSG_MARKER}ERROR:START")
            println("""{command}""")
            showerror(stdout, ex)
            println()
            for line in bt
                if occursin("top-level scope", string(line))
                    break
                end
                println(line)
            end
            println()
            println("{MSG_MARKER}ERROR:END")
        end
        println()
        println("{MSG_MARKER}EXITCODE:$(exit_code__)")
    end
    println()
    println("{MSG_MARKER}FINISHED")
    '''

    def run_script(self, path_to_script, in_file_path, out_file_path, verbose=True):
        file_name = os.path.basename(path_to_script)

        script_folder = os.path.dirname(path_to_script)
        module_name, __ = os.path.splitext(file_name)

        code = """
        include("{path_to_script}")
        {module_name}.convert("{in_file_path}", "{out_file_path}")
        """.format(
            **locals()
        )

        return self.run_command(code, verbose=verbose)

    def get_julia_version_string(self):
        self.p.stdin.write(b"VERSION\n")
        self.p.stdin.flush()
        result = self.p.stdout.readline().rstrip()
        assert result.startswith(b"v"), (
            'got %r, expected a string like v"0.5.0"' % result
        )
        return str(result.lstrip(b"v").strip(b'"'), encoding="ascii")

    def get_julia_version_tuple(self):
        return tuple(map(int, self.get_julia_version_string().split(".")))
