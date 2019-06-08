import asyncio
import base64
import os
import threading
import time
from asyncio.events import AbstractEventLoop
from pathlib import Path
from threading import Lock
from typing import List, Optional, Union, Callable, Any, Tuple, Dict, Generic, TypeVar

import nest_asyncio
from pyppeteer import launch
from pyppeteer.browser import Browser
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page

T = TypeVar('T')


def run_async_code(function: Callable[..., Any], loop: AbstractEventLoop) -> Any:
    return loop.run_until_complete(function())


class Cache(Generic[T]):
    call_count: int
    window: int
    capacity: int
    cache_list: List[T]

    def __init__(self, capacity: int = 20, window: int = 10):
        self.cache_list = []
        self.capacity = capacity
        self.window = window
        self.call_count = 0

    def add(self, value: T) -> bool:
        self.cache_list.append(value)
        cache_length: int = len(self.cache_list)

        if cache_length > self.capacity:
            self.cache_list.pop(0)

        self.call_count += 1

        if self.call_count > self.window:
            self.call_count = 0
            return self.reload_needed()

        return False

    def reload_needed(self) -> bool:
        cache_length = len(self.cache_list)
        last_few_frames = self.cache_list[cache_length - self.window:]
        return all([frame == last_few_frames[0] for frame in last_few_frames])


class User:
    reload_flag: bool
    cache_b64: Cache[bytes]
    cache: Cache[bytes]
    loop: AbstractEventLoop
    element: ElementHandle

    def __init__(self, element: ElementHandle, loop: AbstractEventLoop):
        self.element = element
        self.loop = loop
        self.cache = Cache()
        self.reload_flag = False

    async def get_id(self) -> str:
        prop: ElementHandle = await self.element.getProperty("id")
        uid: str = prop.toString()[14:]
        return uid

    async def get_frame(self) -> bytes:
        frame: bytes = await self.element.screenshot()
        return frame

    @property
    def id(self):
        return run_async_code(self.get_id, self.loop)

    @property
    def frame(self):
        bytes_frame: bytes = run_async_code(self.get_frame, self.loop)
        self.reload_flag = self.cache.add(bytes_frame)
        return bytes_frame

    @property
    def b64_frame(self) -> bytes:
        bytes_frame = run_async_code(self.get_frame, self.loop)
        self.reload_flag = self.cache.add(bytes_frame)
        return base64.b64encode(bytes_frame)


class Locker:
    value: Any
    lock: Lock

    def __init__(self, value: Any):
        self.lock = threading.Lock()
        self.value = value


class FrameThread(threading.Thread):
    delay: float
    proc: Callable[..., Any]
    index: int

    def __init__(self, index: int, process: Callable[..., Any], delay: float):
        super().__init__()
        self.index = index
        self.proc = process  # type: ignore
        self.delay = delay

    def run(self) -> None:
        time.sleep(self.index * self.delay)
        self.proc()


class AgoraRTC:
    watching: bool
    locked_variables: Dict[str, Locker]
    fps: Optional[int]
    page: Optional[Page]
    browser: Optional[Browser]
    loop: AbstractEventLoop
    channel_name: Optional[str]
    app_id: str

    def __init__(self, app_id: str, loop: AbstractEventLoop, executable: Optional[str] = None, debug: bool = False):
        self.app_id = app_id
        self.channel_name = None
        self.loop = loop
        self.browser = None
        self.page = None
        self.fps = None
        self.locked_variables = dict()
        self.watching = False
        self.executable = executable
        self.debug = debug

    @classmethod
    def create_watcher(cls, app_id: str, executable: Optional[str] = None, debug: bool = False):
        loop = asyncio.get_event_loop()
        nest_asyncio.apply(loop)
        return AgoraRTC(app_id, loop, executable, debug)

    async def creator(self):

        if self.executable is not None:
            self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], executablePath=self.executable, headless=(not self.debug))
        else:
            self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], headless=(not self.debug))

        self.page = await self.browser.newPage()
        current_os_path: Union[bytes, str] = os.path.dirname(os.path.realpath(__file__))
        if isinstance(current_os_path, bytes):
            current_path: str = current_os_path.decode("utf-8")
        else:
            current_path = current_os_path

        frontend_html: Path = Path(current_path) / Path("frontend/index.html")
        await self.page.goto(f"file://{str(frontend_html)}")
        await self.page.waitForFunction("bootstrap", None, self.app_id, self.channel_name)
        await self.page.waitForSelector("video.playing")

    def join_channel(self, channel_name: str):
        if self.watching:
            raise RuntimeError("Already Watching")

        self.channel_name = channel_name
        run_async_code(self.creator, self.loop)
        self.watching = True

    async def async_close(self):
        assert self.browser is not None
        await self.browser.close()

    def unwatch(self):
        if not self.watching:
            raise RuntimeError("Nothing to close")

        run_async_code(self.async_close, self.loop)
        self.watching = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unwatch()

    async def get_users_list(self) -> List[ElementHandle]:
        assert self.browser is not None
        assert self.page is not None

        users: List[ElementHandle] = await self.page.JJ("video.playing")

        return users

    async def async_get_users(self) -> List[User]:
        assert self.browser is not None

        results: List[ElementHandle] = await self.get_users_list()
        return [User(result, self.loop) for result in results]

    def get_users(self) -> List[User]:
        if not self.watching:
            raise RuntimeError("No channel has been joined yet")

        reloaded: bool = False
        users: List[User] = run_async_code(self.async_get_users, self.loop)
        for user in users:
            if user.reload_flag:
                reloaded = True
                self.reload()
                break

        if reloaded:
            users = run_async_code(self.async_get_users, self.loop)

        return users

    def set_fps(self, fps: int = 30):
        if fps <= 0:
            raise ValueError("FPS value should be more than 0")

        self.fps = fps

    def get_frames(self, proc: Callable[..., Any], locker: Tuple[Any, ...] = ()):
        if self.fps is None:
            raise RuntimeError("FPS not set by the user. Use set_fps() method")

        self.locked_variables = {variable: Locker(value) for variable, value in locals().items() if value in locker}
        milliseconds_to_wait: float = 100 / self.fps

        print(self.fps)
        print(milliseconds_to_wait)

        threads = [FrameThread(index, proc, milliseconds_to_wait) for index in range(self.fps)]
        for thread in threads:
            thread.start()

    def reload(self):
        self.unwatch()
        self.join_channel(self.channel_name)
