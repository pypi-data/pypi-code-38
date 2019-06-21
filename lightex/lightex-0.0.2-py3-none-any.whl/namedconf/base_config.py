from dataclasses import dataclass
from pathlib import Path

@dataclass
class ContainerDirs:
    container_working_dir: str = '/project'
    container_data_dir: str = '/data'
    container_mlflow_data_dir: str = "/mlflow_data"


@dataclass
class VolumeMount:
    name: str
    mount_path: str
    host_path: str


@dataclass
class HostDirs:
    mlflow_dir: str
    working_dir: str = '.' 
    data_dir: str = '.' 

    def __post_init__(self):
        self.working_dir = str(Path(self.working_dir).resolve())
        self.data_dir = str(Path(self.data_dir).resolve())
