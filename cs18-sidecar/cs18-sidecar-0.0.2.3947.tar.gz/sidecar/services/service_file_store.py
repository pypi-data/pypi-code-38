import os
import pathlib

from sidecar.cloud_logger.file_logger import LogPath


class ServiceFileStore:

    @staticmethod
    def save_execution_output(name: str, cmd: str, output: bytes):
        if not os.path.exists(LogPath):
            pathlib.Path(LogPath).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(LogPath, f"{name}.{cmd}.log"), "wb") as f:
            f.write(output)
