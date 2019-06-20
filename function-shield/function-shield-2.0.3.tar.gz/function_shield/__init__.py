import json
import os
import pkgutil
import tempfile
import platform
from ctypes import cdll

if os.environ.get('AWS_EXECUTION_ENV') or os.environ.get('X_GOOGLE_FUNCTION_NAME'):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    function_shield_so_path = os.path.join(dir_path, 'lib', 'libfunctionshield.so')

    if not os.path.isfile(function_shield_so_path):
        function_shield_so_path = os.path.join(tempfile.gettempdir(), 'libfunctionshield.so')
        with open(function_shield_so_path, 'wb') as function_shield_so_file:
            function_shield_so_file.write(pkgutil.get_data(__name__, 'lib/libfunctionshield.so'))

    function_shield_so = cdll.LoadLibrary(function_shield_so_path)


    def configure(options):
        options["runtime"] = "Python"
        options["runtime_version"] = platform.python_version()
        options_str = json.dumps(options).encode('utf-8')
        return function_shield_so.functionshield_configure(options_str)

else:
    def configure(options):
        print('[WARNING] [FunctionShield] Unsupported environment. FunctionShield currently supports: AWS Lambda and Google Cloud Functions.')
