import pyautogui as ag
from time import sleep

__version__ = "0.3.0"


class Cursor(object):
    def to(self, x, y):
        ag.moveTo(x, y)

    def click(self):
        ag.click()

    @property
    def position(self):
        return ag.position()

    def drag_to(self, x, y, speed=0.1, button="left"):
        ag.dragTo(x, y, speed, button=button)

    def drag_rel(self, x, y, speed=0.1, button="left"):
        ag.dragRel(x, y, speed, button=button)


class Keyboard(object):
    def press(self, key, times=1):
        for x in range(0, times):
            ag.press(key)

    def tab(self, times=1):
        self.press("tab")

    def enter(self, times=1):
        self.press("enter", times)

    def pagedown(self, times=1):
        self.press("pagedown", times)

    def pageup(self, times=1):
        self.press("pageup", times)

    def esc(self, times=1):
        self.press("esc", times)

    def ctrl(self, key):
        ag.hotkey("ctrl", key)

    def f(self, number, times=1):
        self.press(r"f{number}", times)

    def down(self, times=1):
        self.press("down", times)

    def up(self, times=1):
        self.press("up", times)

    def right(self, times=1):
        self.press("right", times)

    def left(self, times=1):
        self.press("left", times)

    def delete(self, times=1):
        self.press("delete", times)

    def write(self, text):
        ag.typewrite(text)

    def writeline(self, text):
        ag.typewrite(text)
        self.enter()


class MsgBox(object):
    def confirm(self, msg):
        return ag.confirm(msg)

    def alert(self, msg):
        return ag.alert(msg)


class Automater(object):
    def __init__(self):
        self.cursor = self.cr = Cursor()
        self.keyboard = self.kb = Keyboard()
        self.msgbox = self.mb = MsgBox()
        self.failsafe = True

    @property
    def failsafe(self):
        return ag.FAILSAFE

    @failsafe.setter
    def failsafe(self, value):
        ag.FAILSAFE = value

    @property
    def throttle(self):
        return ag.PAUSE

    @throttle.setter
    def throttle(self, value):
        ag.PAUSE = float(value)

    def request_throttle(self):
        speed = input("  Throttle input (0.1-2.0): ")
        self.throttle = float(speed)

    def pause(self, seconds):
        sleep(seconds)

    def locate_image(self, image_file, region=None):
        return list(ag.locateAllOnScreen(image_file, region=region))

    def image_visible(self, image_file, region=None):
        return len(list(self.locate_image(image_file, region=region)))

    def run(self, macro, *args, **kwargs):
        macro(self, *args, *kwargs)
