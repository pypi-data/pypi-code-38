import asyncio
import base64
import os
import threading
import time
from asyncio.events import AbstractEventLoop
from pathlib import Path
from threading import Lock
from typing import List, Optional, Union, Callable, Any, Tuple, Dict, Generic, TypeVar

from selenium import webdriver
import selenium.webdriver.support.ui as ui
from PIL import Image

from io import BytesIO

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
    def __init__(self, wd, element):
        self.element = element
        self.wd = wd
        # self.loop = loop
        # self.cache = Cache()
        # self.reload_flag = False

    # async def get_id(self) -> str:
    #     prop: ElementHandle = await self.element.getProperty("id")
    #     uid: str = prop.toString()[14:]
    #     return uid
    #
    # async def get_frame(self) -> bytes:
    #     frame: bytes = await self.element.screenshot()
    #     return frame

    @property
    def frame(self):
        x = self.wd.get_screenshot_as_png()
        location = self.element.location
        size = self.element.size
        im = Image.open(BytesIO(x))  # uses PIL library to open image in memory

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']

        im = im.crop((left, top, right, bottom))
        return im
        # return run_async_code(self.get_id, self.loop)


    # @property
    # def b64_frame(self) -> bytes:
    #     bytes_frame = run_async_code(self.get_frame, self.loop)
    #     self.reload_flag = self.cache.add(bytes_frame)
    #     return base64.b64encode(bytes_frame)


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
    def __init__(self, app_id: str, loop: AbstractEventLoop, executable: Optional[str] = None, debug: bool = False):
        self.app_id = app_id
        self.channel_name = ""
        self.loop = loop
        self.browser = None
        self.page = None
        self.fps = None
        self.watching = False
        self.executable = executable
        self.debug = debug
        self.wd = None

    @classmethod
    def create_watcher(cls, app_id: str, executable: Optional[str] = None, debug: bool = False):
        loop = asyncio.get_event_loop()
        # nest_asyncio.apply(loop)
        return AgoraRTC(app_id, loop, executable, debug)

    def creator(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-user-media-security=true")
        # options.add_argument("--start-maximized")
        options.add_argument("--use-fake-ui-for-media-stream")
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        if self.executable is None:
            wd = webdriver.Chrome("chromedriver", options=options)
        else:
            wd = webdriver.Chrome(self.executable, options=options)
        # wd.set_window_size(1920, 1080)
        wd.get(f'file://{str(Path(os.path.dirname(os.path.realpath(__file__))) / "frontend/index.html")}')
        # wd.find_element_by_tag_name("html").click()
        _ = wd.execute_script(f"bootstrap('{self.app_id}', '{self.channel_name}')")
        wait = ui.WebDriverWait(wd, 10)
        wait.until(lambda driver: driver.find_element_by_class_name("playing"))
        self.wd = wd

        # if self.executable is not None:
        #     self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], executablePath=self.executable, headless=(not self.debug))
        # else:
        #     self.browser = await launch(args=['--no-sandbox', '--disable-setuid-sandbox'], headless=(not self.debug))
        #
        # self.page = await self.browser.newPage()
        # current_os_path: Union[bytes, str] = os.path.dirname(os.path.realpath(__file__))
        # if isinstance(current_os_path, bytes):
        #     current_path: str = current_os_path.decode("utf-8")
        # else:
        #     current_path = current_os_path
        #
        # frontend_html: Path = Path(current_path) / Path("frontend/index.html")
        # await self.page.goto(f"file://{str(frontend_html)}")
        # await self.page.waitForFunction("bootstrap", None, self.app_id, self.channel_name)
        # await self.page.waitForSelector("video.playing")

    def join_channel(self, channel_name: str):
        self.channel_name = channel_name
        self.creator()

        # if self.watching:
        #     raise RuntimeError("Already Watching")
        #
        # self.channel_name = channel_name
        # # run_async_code(self.creator, self.loop)
        # self.creator()
        # self.watching = True

    def close(self):
        self.wd.close()
        # assert self.browser is not None
        # await self.browser.close()

    def unwatch(self):
        # if not self.watching:
        #     raise RuntimeError("Nothing to close")

        # run_async_code(self.async_close, self.loop)
        self.close()
        # self.watching = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unwatch()

    def get_users_list(self):
        return self.wd.find_elements_by_class_name("playing")
        # assert self.browser is not None
        # assert self.page is not None
        #
        # users: List[ElementHandle] = await self.page.JJ("video.playing")
        #
        # return users

    def get_users(self) -> List[User]:
        # if not self.watching:
        #     raise RuntimeError("No channel has been joined yet")
        #
        # reloaded: bool = False
        # for user in users:
        #     if user.reload_flag:
        #         reloaded = True
        #         self.reload()
        #         break
        #
        # if reloaded:
        #     users = run_async_code(self.async_get_users, self.loop)
        return [User(self.wd, i) for i in self.get_users_list()]

    # def set_fps(self, fps: int = 30):
    #     if fps <= 0:
    #         raise ValueError("FPS value should be more than 0")
    #
    #     self.fps = fps

    # def get_frames(self, proc: Callable[..., Any], locker: Tuple[Any, ...] = ()):
    #     if self.fps is None:
    #         raise RuntimeError("FPS not set by the user. Use set_fps() method")
    #
    #     self.locked_variables = {variable: Locker(value) for variable, value in locals().items() if value in locker}
    #     milliseconds_to_wait: float = 100 / self.fps
    #
    #     print(self.fps)
    #     print(milliseconds_to_wait)
    #
    #     threads = [FrameThread(index, proc, milliseconds_to_wait) for index in range(self.fps)]
    #     for thread in threads:
    #         thread.start()
    #
    # def reload(self):
    #     self.unwatch()
    #     self.join_channel(self.channel_name)
