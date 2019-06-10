"""
Utility functions used across multiple tests.
"""
import tempfile


def write_temp_return_filename(data):
    """
    Write out data to a temporary file and return that file's name.
    This file will need to be deleted.
    :param data: str: data to be written to a file
    :return: str: temp filename we just created
    """
    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(data.encode('utf-8'))
    file.close()
    return file.name


def text_to_file(text, file_path):
    """
    Write text into file_path.
    :param text: str: data to be written to the file
    :param file_path: str: path where we will write text
    """
    with open(file_path, 'w') as outfile:
        outfile.write(text)


def file_to_text(file_path):
    """
    Given a file path return the text in the file.
    :param file_path: str: path to a pre-existing file we will read
    :return: str: content of file_path
    """
    with open(file_path, 'r') as infile:
        return infile.read()
