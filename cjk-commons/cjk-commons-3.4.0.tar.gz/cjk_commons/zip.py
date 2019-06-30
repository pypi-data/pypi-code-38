# -*- coding: utf-8 -*-
import os
from pathlib import Path
import time
from typing import List
import zipfile

from loguru import logger


def extract_from_zip(zip_path: Path, dir_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as zip_file:
        for zip_member in zip_file.infolist():
            zip_file.extract(zip_member, dir_path)
            zip_member_time = time.mktime(zip_member.date_time + (0, 0, -1))
            os.utime(Path(dir_path, zip_member.filename), (zip_member_time, zip_member_time))


def write_to_zip(zip_path: Path, in_path: Path, file_paths: List[Path] = None) -> float:
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        mtime = -1.
        if in_path.is_file():
            zip_file.write(in_path, in_path.name)
            mtime = in_path.stat().st_mtime
        elif in_path.is_dir():
            if not file_paths:
                file_paths = []
                for root, dirnames, filenames in os.walk(str(in_path)):
                    for filename in filenames:
                        file_paths.append(Path(root, filename))
            for file_path in file_paths:
                if file_path.is_file():
                    zip_file.write(file_path, file_path.relative_to(in_path))
                    file_stat_result = file_path.stat()  # todo
                    if mtime < file_stat_result.st_mtime:
                        mtime = file_stat_result.st_mtime
        return mtime


logger.disable(__name__)
