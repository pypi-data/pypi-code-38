import os
import gzip

import fastr
from ..abc.serializable import Serializable
from ..core.tool import Tool


def verify_resource_loading(filename: str, log=fastr.log):
    """
    Verify that a resource file can be loaded. Returns loaded object.

    :param filename: path of the object to load
    :param log: the logger to use to send messages to
    :return: loaded resource
    """
    name, ext = os.path.splitext(filename)

    # Check if file is gzipped
    if ext == '.gz':
        compressed = True
        name, ext = os.path.splitext(filename)
    else:
        compressed = False

    # Read file data
    log.info('Trying to read file with compression {}'.format('ON' if compressed else 'OFF'))
    if compressed:
        try:
            with gzip.open(filename, 'r') as file_handle:
                data = file_handle.read()
        except:
            log.error('Problem reading gzipped file: {}'.format(filename))
            return None
    else:
        try:
            with open(filename, 'r') as file_handle:
                data = file_handle.read()
        except:
            log.error('Problem reading normal file: {}'.format(filename))
            return None

    log.info('Read data from file successfully')

    # Try to read tool doc based on serializer matching the extension
    serializer = ext[1:]
    log.info('Trying to load file using serializer "{}"'.format(serializer))

    if serializer not in Tool.dumpfuncs:
        log.error('No matching serializer found for "{}"'.format(serializer))
        return None

    load_func = Serializable.dumpfuncs[serializer].loads

    try:
        doc = load_func(data)
    except Exception as exception:
        log.error('Could not load data using serializer "{}", encountered exception: {}'.format(serializer,
                                                                                                      exception))
        return None

    return doc


def verify_tool(filename, log=fastr.log, perform_tests=True):
    """
    Verify that a file
    """
    # Load the file
    doc = verify_resource_loading(filename, log)

    if not doc:
        log.error('Could not load data successfully from  {}'.format(filename))
        return None

    # Match the data to the schema for Tools
    log.info('Validating data against Tool schema')
    serializer = Tool.get_serializer()

    try:
        doc = serializer.instantiate(doc)
    except Exception as exception:
        log.error('Encountered a problem when verifying the Tool schema: {}'.format(exception))
        return None

    # Create the Tool object as the final test
    log.info(f'Instantiating Tool object')
    try:
        tool = Tool(doc)
        tool.filename = filename
    except Exception as exception:
        log.error('Encountered a problem when creating the Tool object: {}'.format(exception))
        return None

    log.info('Loaded tool {} successfully'.format(tool))

    if perform_tests:
        log.info('Testing tool...')
        try:
            tool.test()
        except fastr.exceptions.FastrValueError as e:
            log.error('Tool is not valid: {}'.format(e))

    return tool
