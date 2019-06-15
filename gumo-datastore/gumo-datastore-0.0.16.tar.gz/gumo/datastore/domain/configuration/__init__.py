import dataclasses
from typing import Optional


@dataclasses.dataclass(frozen=True)
class DatastoreConfiguration:
    use_local_emulator: bool = False
    emulator_host: Optional[str] = None
    namespace: Optional[str] = None

    def __post_init__(self):
        if self.use_local_emulator and self.emulator_host is None:
            raise ValueError(f'If the emulator enabled, then emulator_host must be present.')
