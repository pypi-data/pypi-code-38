from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from io import BytesIO
from PIL import Image
from typing import Optional, Callable


class ScreenShot(object):
    """
    *初始化传入的browser会自动退出， 方法中传入的需自己退出*
    """

    def __init__(self, browser: RemoteWebDriver = None,
                 before_shot: Optional[Callable[[RemoteWebDriver], None]] = None,
                 after_shot: Optional[Callable[[RemoteWebDriver, Image.Image], Image.Image]] = None):
        self.default_browser = browser
        self.after_shot = after_shot
        self.before_shot = before_shot

    def save_full_page_screen_shot(self, file_name: str, *args, **kwargs):
        self.get_full_page_screen_shot(*args, **kwargs).save(file_name)

    def get_full_page_screen_shot(self, browser: RemoteWebDriver = None, url: Optional[str] = None,
                                  before_shot: Optional[Callable[[RemoteWebDriver], None]] = None,
                                  after_shot: Optional[
                                      Callable[
                                          [RemoteWebDriver, Image.Image], Image.Image]] = None) -> Image.Image:
        """

        :param browser:
        :param url:
        :param before_shot:
        :param after_shot:
        :rtype: Image.Image
        :return:
        """
        if browser is None:
            browser = self.default_browser
        if url is not None:
            browser.get(url)
        if before_shot is None:
            before_shot = self.before_shot
        if after_shot is None:
            after_shot = self.after_shot
        size = browser.get_window_size()
        y = browser.execute_script('return window.scrollY')
        avail_height = size.get('height')
        i = 0
        pngs = []
        while (True):
            if before_shot is not None:
                before_shot(browser)
            png = get_img_from_bytes(browser.get_screenshot_as_png())
            if after_shot is not None:
                png = after_shot(browser, png)
            pngs.append(png)
            i += 1
            # 是否还有下一页
            y = y + avail_height
            browser.execute_script('window.scrollTo(0,{})'.format(y))
            curY = browser.execute_script('return window.scrollY')  # 下一页起点
            ratio = png.size[1] / size['height']
            if (curY < y):
                if (y - curY == 0):
                    break
                # 下一页不完整
                if before_shot is not None:
                    before_shot(browser)
                png = get_img_from_bytes(browser.get_screenshot_as_png())
                if after_shot is not None:
                    png = after_shot(browser, png)
                pngs.append(png.crop((0, ratio * (y - curY), png.size[0], png.size[1])))
                break
        # 拼接
        width = pngs[0].size[0]
        height = sum([p.size[1] for p in pngs])
        full_png = Image.new('RGB', (width, height))
        y1 = 0
        for png in pngs:
            y0 = y1
            y1 += png.size[1]
            full_png.paste(png, (0, y0, width, y1))
        return full_png

    def __del__(self):
        if self.default_browser is not None:
            self.default_browser.quit()


def get_img_from_bytes(png_data: bytes) -> Image.Image:
    """

    :param png_data:
    :rtype: Image.Image
    :return:
    """
    b = BytesIO()
    b.write(png_data)
    b.seek(0)
    i = Image.open(b)
    return i
