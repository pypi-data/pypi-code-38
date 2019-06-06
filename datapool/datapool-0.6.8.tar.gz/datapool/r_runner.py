# encoding: utf-8
from __future__ import print_function, division, absolute_import

import os

from .interpreter_bridge import InterpreterBridge


class RRunner(InterpreterBridge):

    NAME = "R"

    EXTRA_ARGS = ["--vanilla", "-q"]

    MSG_MARKER = "!!!"

    TEMPLATE = """

        rm(list=ls());
        .exit.code <- 0;

        handler <- function(e)
        {
            .exit.code <<- 1;
            cat("[%MSG_MARKER%]ERROR:START\\n");
            cat(paste("MESSAGE:", e, "\\n"));
            calls <- sys.calls();
            n <- length(calls);
            started <- 0;
            for (i in seq(1, n  - 2)) {
                txt <- paste(calls[i]);
                matches <- regexpr("withCallingHandlers", txt);
                if(matches[1] == 1)
                    started <- 1;
                if (started) {
                    cat(paste("CALL STACK:  ", txt, "\\n"));
                }
            }
            cat("[%MSG_MARKER%]ERROR:END\\n");
        }


        try({
            withCallingHandlers(
                { [%command%]; }
                ,error=handler
            )
            }
        );

        cat(sprintf("[%MSG_MARKER%]EXITCODE:%d\\n", .exit.code));
        cat("[%MSG_MARKER%]FINISHED\\n");
    """

    # as R uses curly braces we used [% and %] above but have to fix thix now:
    TEMPLATE = (
        TEMPLATE.replace("{", "{{")
        .replace("}", "}}")
        .replace("[%", "{")
        .replace("%]", "}")
    )

    def run_script(self, path_to_script, in_file_path, out_file_path, verbose=False):
        file_name = os.path.basename(path_to_script)

        script_folder = os.path.dirname(path_to_script)
        module_name, __ = os.path.splitext(file_name)

        code = """
        source("{path_to_script}");
        convert("{in_file_path}", "{out_file_path}");
        """.format(
            **locals()
        )

        return self.run_command(code, verbose=verbose)
