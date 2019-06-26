"""File utility tools"""
import re

def replace_in_files(files_map, replace_map):
    """
    Replaces a series of matches in a collection of files

    Args:
        file_paths (dict): A dictionary where the key is the file source and the value is a file target.
            If the target is set to an empty string, the original file will be replaced
        replace_map (dict): A dictionary where the keys are the regex to be matched and
            the value is the content to replace the match with

    Example:
        file_map {
            '/tmp/source.txt': '/tmp/destination.txt'
        }
        replace_map {
            '.*foo.*': 'bar'
        }
        replace_in_files(file_map, replace_map)
    """
    for file_src_path, file_dst_path in files_map.items():
        with open(file_src_path, 'r+') as src_file:
            data = src_file.read()
            new_data = data
            for pattern, replace_value in replace_map.items():
                new_data = re.sub(pattern, replace_value, new_data, flags=re.DOTALL)
            if not file_dst_path:
                src_file.seek(0)
                src_file.write(new_data)
                src_file.truncate()
            else:
                with open(file_dst_path, 'w') as dest_file:
                    dest_file.write(new_data)
