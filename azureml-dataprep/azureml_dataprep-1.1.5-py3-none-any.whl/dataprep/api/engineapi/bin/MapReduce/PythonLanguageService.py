import sys, io, json, os, platform
import struct
from collections import OrderedDict

engine_native_path = os.environ.get('AZUREML_DATAPREP_NATIVE_PATH')
if engine_native_path is not None:
    from importlib import util, machinery, import_module
    def LoadModuleFromFile(module_name, module_file_path):
        spec = util.spec_from_file_location(module_name, module_file_path)
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Ensure subsequent imports use manually loaded module:
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        sys.modules[module_name] = module

    # Try to import module if it isn't in sys.modules, create namespace module for it otherwise.
    def TryImportOrCreate(module_name):
        if sys.modules.get(module_name) is None:
            try:
                import_module(module_name)
            except ImportError:
                module_spec = machinery.ModuleSpec(module_name, None, origin='namespace')
                module_spec.submodule_search_locations = [str(Path(engine_native_path, *module_name.split('.')))]
                module = util.module_from_spec(module_spec)
                sys.modules[module_name] = module

    # Import azureml.dataprep.native from file. This will populate sys.modules['azureml.dataprep.native'],
    # though for imports to work the namespace's above native (azureml, dataprep) need to be importable as well.
    # If those namespaces exists in site-packages then we can just import them, otherwise we need to create
    # 'namespace modules' that point down the tree to native.
    from pathlib import Path
    module_name = 'azureml.dataprep.native'
    python_minor_version = str(sys.version_info.minor)
    native_module_glob = 'native.*3' + python_minor_version + '*'
    native_module_glob += '.pyd' if platform.system().lower() == 'windows' else '.so'
    azureml_dataprep_path = Path(engine_native_path, 'azureml', 'dataprep')
    paths_to_native = list(azureml_dataprep_path.glob(native_module_glob))
    if len(paths_to_native) != 1:
        raise ImportError("Failed to find single version of " + module_name +
                          " matching python3." + python_minor_version +
                          " using glob: " + str(azureml_dataprep_path / native_module_glob))
    LoadModuleFromFile(module_name, str(paths_to_native[0]))

    TryImportOrCreate('azureml.dataprep')
    sys.modules['azureml.dataprep'].native = sys.modules['azureml.dataprep.native']

    TryImportOrCreate('azureml')
    sys.modules['azureml'].dataprep = sys.modules['azureml.dataprep']

try:
    import numpy as np # Remove after vso: 246011
    import pandas
    from azureml.dataprep import native
except ImportError as error:
    sys.exit("Import failed:" + str(error.args))


class StdioRedirect():
    # redirect stdio calls so that custom code will not impact product running
    def __init__(self):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.__stdin__ = sys.__stdin__
        self.__stdout__ = sys.__stdout__
    def __enter__(self):
        inputBuf = io.StringIO()
        outputBuf = io.StringIO()
        sys.stdin = inputBuf
        sys.stdout = outputBuf
        sys.__stdin__ = inputBuf
        sys.__stdout__ = outputBuf
        return (inputBuf, outputBuf)
    def __exit__(self, type, value, traceback):
        sys.stdin = self.stdin
        sys.stdout = self.stdout
        sys.__stdin__ = self.__stdin__
        sys.__stdout__ = self.__stdout__

def ReadLength(stream):
    return struct.unpack('<i', ReadFixedSizeBuffer(stream, 4))[0]

def WriteLength(stream, length):
    stream.write(struct.pack('<i', length))

_loadedUserModules = {}

def CreateFunction(function):
    name = function["name"]
    source = function["source"]

    from hashlib import sha1
    key = sha1(source.encode("utf-8")).digest() # SHA1 malious collisions not an issue here. SHA1 is faster and has a smaller digest than SHA256.

    try:
        environment = _loadedUserModules[key]
    except KeyError:
        environment = {}
        code = compile(source, "<string>", "exec")
        exec(code, environment)
        _loadedUserModules[key] = environment

    identifiers = name.split(".")
    f = environment[identifiers[0]]
    for identifier in identifiers[1:]:
        f = f.__dict__[identifier]

    return f

def ReadFixedSizeBuffer(stream, size):
    buffer = bytearray(size)
    bytes_read = 0
    while (bytes_read < size):
        buffer_view = memoryview(buffer)[bytes_read:]
        bytes_read += stream.readinto(buffer_view)
        if bytes_read == 0:
            raise EOFError()
    return buffer

def WriteMessage(stream, message):
    message_bytes = json.dumps(message).encode('utf-8')
    WriteLength(stream, len(message_bytes))
    stream.write(message_bytes)
    stream.flush()

def GetErrorBatchProcessor(exception):
    result = {'result': 'error', 'message': str(exception)}
    def sendErrorResult(dataBytes, outStream):
        WriteMessage(outStream, result)
    return sendErrorResult

def GetMapRowsBatchProcessor(mapRowsMessage):
    raiseErrors = mapRowsMessage["raiseErrors"]
    functions = [CreateFunction(f) for f in mapRowsMessage["functions"]]

    def wrapFunction(f):
        def wrappedFunction(row):
            try:
                return f(row)
            except Exception as e:
                if raiseErrors:
                    raise e
                try:
                    inner = str(e)
                except:
                    inner = ""

                return native.DataPrepError('Microsoft.DPrep.ErrorValues.ScriptError', None, {'scriptError':inner})
        return wrappedFunction

    wrapped_functions = [wrapFunction(f) for f in functions]

    def new_values(preppyBytes):
        yield ["C" + str(i) for i in range(0, len(wrapped_functions))] # First item is column names.
        for row in native.preppy_to_pyrecords([preppyBytes]):
            yield [f(row) for f in wrapped_functions]

    def MapRows(dataBytes, outStream):
        with StdioRedirect():
            new_data_bytes = native.preppy_from_sequence(new_values(dataBytes))
        WriteMessage(outStream, {'result': 'success'})
        WriteLength(outStream, len(new_data_bytes))
        outStream.write(new_data_bytes)
        outStream.flush()

    return MapRows

def GetMapParitionsBatchProcessor(mapPartitionMessage):
    user_function = CreateFunction(mapPartitionMessage["function"])
    with_index = mapPartitionMessage["withIndex"]
    partition_index = mapPartitionMessage["partitionIndex"] if with_index else -1

    def MapPartition(data_bytes, outStream):
        columns = native.preppy_to_ndarrays([data_bytes], True) # with extended types (keep DPrepError)
        df = pandas.DataFrame.from_dict(OrderedDict(columns))
        # We do not catch exceptions from user's map as dataframe function. Any such error should fast fail.
        with StdioRedirect():
            df = user_function(df, partition_index) if with_index else user_function(df)
        new_schema = df.columns.tolist()
        new_values = []
        # Handle Categorical typed columns. Categorical is a pandas type not a numpy type and so azureml-dataprep-native can't handle it.
        # This is temporary pending improvments to native such that it can handle pandas Categoricals, vso: 246011
        for column_name in new_schema:
            if pandas.api.types.is_categorical_dtype(df[column_name]):
                new_values.append(np.asarray(df[column_name]))
            else:
                new_values.append(df[column_name].values)
        # new_values = [df[column_name].values for column_name in new_schema]
        new_data_bytes = native.preppy_from_ndarrays(new_values, new_schema)

        WriteMessage(outStream, {'result': 'success'})
        WriteLength(outStream, len(new_data_bytes))
        outStream.write(new_data_bytes)
        outStream.flush()

    return MapPartition

def GetBatchProcessor(request):
    operation = request["operation"]
    if operation == "mapRows":
        return GetMapRowsBatchProcessor(request)
    elif operation == "mapPartition":
        return GetMapParitionsBatchProcessor(request)
    else:
        raise AssertionError("Unknown request operation.")


def HandleDataRequest(request, inStream, outStream):
    try:
        batch_processor = GetBatchProcessor(request)
    except Exception as exception:
        # If we can't even load the functions then every batch
        # will get the same result. We still need to read through
        # all batches sent and respond.
        batch_processor = GetErrorBatchProcessor(exception)

    end_of_data_seen = False
    while not end_of_data_seen:
        data_size = ReadLength(inStream)
        if data_size == 0:
            WriteMessage(outStream, {'result': 'endOfData'})
            end_of_data_seen = True
        else:
            try:
                buffer = ReadFixedSizeBuffer(inStream, data_size)
                batch_processor(buffer, outStream)
            except Exception as exception:
                WriteMessage(outStream, {'result': 'error', 'message': str(exception)})


# Streams without text encoding.
raw_stdout = sys.stdout.buffer
raw_stdin = sys.stdin.buffer

# Write Starting message to signal ready for processing
WriteMessage(raw_stdout, {'result':'started'})

exit = False
while not exit:
    input_size = ReadLength(raw_stdin)
    request_bytes = ReadFixedSizeBuffer(raw_stdin, input_size)
    try:
        request = json.loads(request_bytes.decode('utf-8'))
    except Exception as e:
        sys.stderr.write("Error parsing message. Message size:" + str(input_size) + " Message binary:")
        sys.stderr.write(str(request_bytes))
        raise e

    try:
        operation = request["operation"]
    except KeyError:
        sys.stderr.write("Unexpected message. Missing operation. Message size:" + str(input_size) + " Message binary:")
        sys.stderr.write(str(request_bytes))
        raise e

    if operation == "exit":
        exit = True
    elif operation == "mapRows" or operation == "mapPartition":
        HandleDataRequest(request, raw_stdin, raw_stdout)
    else:
        WriteMessage(raw_stdout, {'result': 'error', 'message': "Unexpected request type. " + str(operation)})

