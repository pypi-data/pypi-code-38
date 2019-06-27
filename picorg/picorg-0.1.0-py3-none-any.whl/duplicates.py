import filecmp

from itertools import combinations
from pathlib import Path
from typing import List

import settings


def handle_duplicates() -> List[Path]:
    extensions = [".jpg"]

    files = []
    result = []
    for file_ext in extensions:
        for filepath in Path().glob("*" + file_ext):
            files.append(filepath)
    for file1, file2 in combinations(files, 2):
        # If any of the two files have been moved, just continue the iteration
        if not file1.is_file() or not file2.is_file():
            continue
        if filecmp.cmp(file1, file2, shallow=False):
            Path("duplicates").mkdir(exist_ok=True)
            if len(file1.name) < len(file2.name):
                file_to_move = file2
            elif len(file1.name) > len(file2.name):
                file_to_move = file1
            else:
                file_to_move = file1 if file1 > file2 else file2
            new_filepath = Path("duplicates", file_to_move.name)
            file_to_move.replace(new_filepath)
            result.append(new_filepath)

    files.clear()
    for file_ext in extensions:
        for filepath in Path().glob("*" + file_ext):
            files.append(filepath)
    paths = settings.get("pic_paths", [])
    for path in paths:
        for file_ext in extensions:
            for filepath in Path(path).glob("**/*" + file_ext):
                matching_file = next(
                    (f for f in files if f.name == filepath.name), None
                )
                if (
                    matching_file
                    and matching_file.is_file()
                    and filecmp.cmp(matching_file, filepath, shallow=False)
                ):
                    Path("duplicates").mkdir(exist_ok=True)
                    new_filepath = Path("duplicates", matching_file.name)
                    matching_file.replace(new_filepath)
                    result.append(new_filepath)
    return result
