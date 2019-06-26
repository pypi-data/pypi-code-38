import traceback
import warnings
import sys


def warn_with_traceback():
    "Replace ``warnings.showwarning``"
    def warn(message, category, filename, lineno, file=None, line=None):
        """Print tracebacks for warnings (see https://stackoverflow.com/a/22376126)"""
        log = file if hasattr(file, 'write') else sys.stderr
        traceback.print_stack(file=log)
        log.write(warnings.formatwarning(message, category, filename, lineno, line))

    warnings.showwarning = warn
