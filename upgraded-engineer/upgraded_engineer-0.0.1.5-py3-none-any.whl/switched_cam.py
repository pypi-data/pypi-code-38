from . import core
from typing import Callable


class Processor:
    def __init__(
        self,
        process_func: Callable,
        video_size: Tuple[int, int, int] = core.DEFAULT_VIDEO_SIZE,
    ):
        self.engi = core.Engine(video_size=video_size)
