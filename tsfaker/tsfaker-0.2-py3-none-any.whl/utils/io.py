import contextlib
import os
import sys
from typing import Tuple

from tableschema import Schema
from tableschema.exceptions import LoadError

from tsfaker.exceptions import TsfakerException, DifferentNumberInputOutput


def process_input_output(input_descriptors: Tuple[str], output_files: Tuple[str]):
    """ Manage specific cases in input and output arguments



    :param input_descriptors:
    :param output_files:
    :return: (input_descriptors, output_files) after preprocessing
    """
    if is_single_folder(input_descriptors):
        input_folder = input_descriptors[0]
        input_descriptors = get_descriptors_files_path_in_folder(input_folder)

        if output_files == ('-',):
            output_files = tuple(replace_json_to_csv_ext(input_file_path) for input_file_path in input_descriptors)

        if is_single_folder(output_files):
            output_folder = output_files[0]
            output_files = list()
            for input_file_path in input_descriptors:
                relative_path = os.path.relpath(input_file_path, start=input_folder)
                output_file_path = os.path.join(output_folder, replace_json_to_csv_ext(relative_path))
                output_files.append(output_file_path)
            output_files = tuple(output_files)

    if output_files == ('-',):
        output_files = ('-',) * len(input_descriptors)

    if len(input_descriptors) != len(output_files):
        raise DifferentNumberInputOutput(input_descriptors, output_files)

    return input_descriptors, output_files


def is_single_folder(ressources: Tuple[str]) -> bool:
    return len(ressources) == 1 and isinstance(ressources[0], str) and os.path.isdir(ressources[0])


def replace_json_to_csv_ext(file_path: str) -> str:
    if file_path.endswith('.json'):
        return file_path[:-5] + '.csv'
    else:
        raise TsfakerException("Input file path '{}' should end with extension '.json'".format(file_path))


def get_descriptors_files_path_in_folder(folder_path: str) -> Tuple[str]:
    descriptor_files_paths = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if is_schema_file(file_path):
                descriptor_files_paths.append(file_path)

    return tuple(descriptor_files_paths)


def is_schema_file(file_path):
    if not file_path.endswith('.json'):
        return False

    try:
        Schema(file_path)
    except LoadError:
        return False

    return True


@contextlib.contextmanager
def smart_open_write(filename=None):
    if filename and filename != '-':
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()
