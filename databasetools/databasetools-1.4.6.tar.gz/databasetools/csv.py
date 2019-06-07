import os
import _csv as csv_builtin
import inspect


class CSV:
    def __init__(self, file_path=None):
        self.file_path = resolve_path(file_path, get_calling_file())

    def write(self, data, method='w'):
        """
        Export data to CSV file.

        :param data: Either a list of tuples or a list of lists.
        :param method: File opening method.
        """
        # Create list of lists from flat list
        data = data if isinstance(data[0], (list, set, tuple)) else [[d] for d in data]

        # Open file and write rows
        with open(self.file_path, method) as write:
            wr = csv_builtin.writer(write)
            wr.writerows(data)
        return self.file_path

    def append(self, data):
        """Append rows to an existing CSV file."""
        # CSV file exists, append rows
        if os.path.exists(self.file_path):
            return self.write(data, method='a')
        # CSV file does NOT exist, create new file and write rows
        else:
            return self.write(data, method='w')

    def read(self):
        """Reads CSV file and returns list of contents"""
        # Validate file path
        assert os.path.isfile(self.file_path), 'No such file exists: ' + str(self.file_path)

        # Open CSV file and read contents
        with open(self.file_path, 'r') as f:
            reader = csv_builtin.reader(f)
            loaded_data = list(reader)

        # Force digits to become integers
        return juggle_types(loaded_data)


def juggle_types(data):
    """Force all digits in a list to become integers."""
    # Data is a list of lists (2D) and not a single column table (1D)
    if isinstance(data[0], list):
        return [[force_int(col) for col in row] for row in data]

    # Data is 1D
    elif isinstance(data, list):
        return [force_int(i) for i in data]
    else:
        return data


def force_int(value):
    """Force value to be an integer if it is a digit"""
    return int(value) if str(value).isdigit() else value


def resolve_path(file_path, calling_function):
    """
    Conditionally set a path to a CSV file.

    Option 1 - Join working directory and calling function name (file_name)
    Option 2 - Join working directory and provided file_path string
    Option 3 - Return provided file_path

    :param file_path: None, filename string or Full file path
    :param calling_function: Name of the function that initialized the CSV class
    :return:
    """
    # No file_path is provided
    if not file_path:
        resolved = os.path.join(os.getcwd(), calling_function)

    # String provided that does not a '/', we can assume this is not a path
    elif file_path.count(os.sep) == 0:
        resolved = os.path.join(os.getcwd(), file_path)

    # Valid file_path is provided
    else:
        resolved = file_path

    # Add .csv file extension
    if not resolved.endswith('.csv'):
        resolved = resolved + '.csv'
    return resolved


def get_calling_file(file_path=None, result='name'):
    """
    Retrieve file_name or file_path of calling Python script
    """
    # Get full path of calling python script
    if file_path is None:
        path = inspect.stack()[1][1]
    else:
        path = file_path

    name = path.split('/')[-1].split('.')[0]
    if result == 'name':
        return name
    elif result == 'path':
        return path
    else:
        return path, name


# Backward compatibility
class CSVExport:
    def __init__(self, data=None, cols=None, file_path=None, file_name=None):
        if cols:
            data.insert(0, cols)
        file_path = os.path.join(file_path, file_name) if file_name else file_path
        CSV.write(data, file_path)


class CSVImport:
    def __init__(self, file_name):
        CSV.read(file_name)
