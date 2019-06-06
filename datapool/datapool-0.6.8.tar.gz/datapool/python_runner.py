# encoding: utf-8
from __future__ import absolute_import, division, print_function

import os

from .interpreter_bridge import InterpreterBridge


class PythonRunner(InterpreterBridge):

    NAME = "python"

    EXTRA_ARGS = ["-i", "-u", "-B"]

    MSG_MARKER = "!!!"

    TEMPLATE = """

# we cleanup the workspace first:
for name in dir():
    if not name.startswith("_"):
        exec("del %s" % name)

__exit_code = 0
try:
    {command}
except:
    __exit_code = 1
    print("\\n{MSG_MARKER}ERROR:START")
    import traceback
    traceback.print_exc(limit=1)
    print("\\n{MSG_MARKER}ERROR:END")

print("\\n{MSG_MARKER}EXITCODE:%d" % __exit_code)
print("\\n{MSG_MARKER}FINISHED")
    """

    def run_script(self, path_to_script, in_file_path, out_file_path, verbose=False):
        file_name = os.path.basename(path_to_script)

        script_folder = os.path.dirname(path_to_script)
        module_name, __ = os.path.splitext(file_name)

        code = """
        import imp
        {module_name} = imp.load_source("{module_name}", "{path_to_script}")
        {module_name}.convert("{in_file_path}", "{out_file_path}")
        """.format(
            **locals()
        )

        return self.run_command(code, verbose=verbose)
