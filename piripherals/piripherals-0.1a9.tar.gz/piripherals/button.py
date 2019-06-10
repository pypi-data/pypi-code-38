"""Things that have to do with buttons, digital inputs.

Use GPIO pins as button inputs with debouncing and multi-click and hold-detection.
"""

from .util import not_raising, fork, cleanup_at_exit
from threading import Thread, Event
from functools import partial
from time import sleep, monotonic
try:
    import RPi.GPIO as GPIO
except:
    pass

__all__ = ['ClickButton']


class ClickButton:
    """Representation of a button with multi-click and hold-detection.

    This was inspired by http://www.mathertel.de/Arduino/OneButtonLibrary.aspx,
    but extended to n-clicks and click-hold.

    .. note::

        Most debouncing code out there is wrong. The debounce functionality of
        RPi.GPIO just suppresses events, but does not debounce. Debouncing
        correctly in software is tricky but doable.
        Read this http://www.ganssle.com/debouncing.htm.

    This button can be bound to GPIO pins but it can be used with other
    input sources as well.

    **What is click, hold, up/down, pressed/released?**

    The state of the button is updated by calling :meth:`update` with ``True`` or ``False`` as
    argument (equivalently just calling the button, calling :meth:`press`, :meth:`release`).
    Updating the state to ``True`` is called `press`, updating the state to ``False`` is called `release`.

    The state is `changed` when :meth:`update` was called with a parameter different from
    the previous call. If the state did not change for a time > ``click_time``, the
    button in considered `down` (stated changed to `pressed`) or `up` (state changed to `released`).
    This effectivly debounces the input. The final state wins, but quick jumps between states
    are filtered out.

    The button is considered `clicked` when

    1. it was `pressed` for > ``click_time`` (click is counted)
    2. and then `released` for > ``double_click_time`` (click is fired)

    If it was pressed again after beeing released within < ``double_click_time``,
    another click may be counted (start again at 1.). This way n-clicks can be detected.

    The button is considered `held` when it was `pressed` for > ``hold_time``
    (enter hold state). There might have been preceding clicks, that have been
    counted, but not fired. This way we get n-hold, with n beeing the number of
    clicks preceding the hold. Hold events are fired as long as the button stays
    held with ``hold_repeat`` delay, if ``hold_repeat`` > 0.

    .. attention::

        Setting ``when_clicked`` or ``when_held`` disables any handlers
        registered with :meth:`on_click` or :meth:`on_hold`. So there is
        either a single click/hold handler or a handler for each type of
        click/hold.

    Args:
        pin (int): BCM_ pin to bind to, 0 = do not use GPIO
        when_clicked (callable(n)): click handler, n = # of clicks
        when_held (callable(n)): hold handler, n = # of clicks before hold
        click_time (float): seconds button needs to stay in pressed/released
            state to consider it a click (this does the debouncing)
        double_click_time (float): max. seconds between clicks to count them
            as double clicks (or triple, or quadruple, ...)
        hold_time (float): seconds in pressed state after which button is
            considered held
        hold_repeat (float): seconds between repeated hold events, when
            button stays held, 0 = disable hole repeat
        name (str): name of the button for str() and debugging

    .. _BCM: https://pinout.xyz/
    """

    def __init__(self,
                 pin=0,
                 when_clicked=None,
                 when_held=None,
                 click_time=25e-3,
                 double_click_time=200e-3,
                 hold_time=1,
                 hold_repeat=0,
                 name=None):
        self.name = name
        self.pressed = False
        self.held = False
        self.down = False
        self.time = 0
        self.clicks = 0
        self.click_time = click_time
        self.double_click_time = double_click_time
        self.hold_time = hold_time
        self.hold_repeat = hold_repeat
        if when_clicked:
            self.when_clicked = not_raising(when_clicked)
        self.click_handlers = {}
        if when_held:
            self.when_held = not_raising(when_held)
        self.hold_handlers = {}
        if pin:
            self.bind(pin)

    def __str__(self):
        return self.name or 'ClickButton'

    def _handle(self, handlers, n):
        try:
            handlers[n]()
        except KeyError:
            pass

    def when_clicked(self, n):
        """fired when clicked.

        Args:
            n (int): # of clicks, 1 = single click, 2 = double click, ...
        """
        self._handle(self.click_handlers, n)

    def when_held(self, n):
        """fired when held.

        Args:
            n (int): # of clicks *before* hold, 0 = hold, 1 = click + hold
                2 = double click + hold
        """
        self._handle(self.hold_handlers, n)

    def on_click(self, n, callback, *args, **kwargs):
        """register a click handler.

        Args:
            n (int): # of click to register the handler with, see :meth:`when_clicked`
            callback (callable): the handler
            *args: args passed to handler
            **kwargs: kwargs passed to handler
        """
        self.click_handlers[n] = partial(
            not_raising(callback), *args, **kwargs)
        return callback

    def on_hold(self, n, callback, *args, **kwargs):
        """register a hold handler.

        Args:
            n (int): # of click to register the handler with, see :meth:`when_held`
            callback (callable): the handler
            *args: args passed to handler
            **kwargs: kwargs passed to handler
        """
        self.hold_handlers[n] = partial(not_raising(callback), *args, **kwargs)
        return callback

    def update(self, pressed, now=None):
        """update state.

        When bound to GPIO this called automatically. You need to call this,
        when you want bind this button a different input source.

        This can (and must be) call ed repeatedly (even with teh same pressed
        state) to allow the click and hold detection to work.

        The button itself is callable, calling the button is equivalent to
        call :meth:`update`.

        Args:
            pressed (bool): True = button is down, False = button is up
            now (float): time when it change state (optional)
        """
        if not now:
            now = monotonic()

        is_pressed = pressed  # new state
        was_pressed = self.pressed  # old state
        dt = now - self.time  # time since last state change

        if dt > self.click_time:
            self.down = is_pressed

        if not was_pressed:
            if is_pressed:  # state changed --> pressed
                self.pressed = True
                self.time = now
            else:  # still released
                if self.clicks and dt > self.double_click_time:
                    self.when_clicked(self.clicks)
                    self.clicks = 0
        elif was_pressed:
            if is_pressed:  # still pressed
                if self.held:
                    if self.hold_repeat and dt > self.hold_repeat:
                        self.time = now
                        self.when_held(self.clicks)
                elif dt > self.hold_time:  # state changed --> held
                    self.held = True
                    self.time = now
                    self.when_held(self.clicks)
            else:  # state changed --> released
                if self.held:
                    self.clicks = 0
                elif dt > self.click_time:
                    self.clicks += 1
                self.pressed = self.held = False
                self.time = now

    def press(self):
        ":meth:`update()` with ``pressed=True``"
        self.update(True)

    def release(self):
        ":meth:`update()` with ``pressed=False``"
        self.update(False)

    def is_down(self):
        """check if button is down, respecting click_time

        The button itself evaluated as ``bool(button)`` is equivalent to ``is_down()``:

        Return:
            bool: if down for > click_time
        """
        return self.down

    def is_up(self):
        """check if button is up, respecting click_time

        Return:
            bool: if up for > click_time
        """
        return not self.down

    def is_held(self):
        """check if button is held, respecting hold_time

        Return:
            bool: if down for > hold_time
        """
        return self.held

    def bind(self, pin, low_active=1, pullup=1,  delay=0.01, count=100):
        """bind to GPIO pin.

        .. note::

            The state of the GPIO will be polled regularly, but the polling is only
            started on demand after edge detection and runs for a limited time.

        Args:
            pin (int): BCM_ pin number
            low_active (bool): low means pressed
            pullup (int): 1 = pullup, -1 = pulldown, 0 = nothing
            delay (float): delay between polls in seconds
            count (int): # of polls after button was released, this allows
                the polling to be paused if the button is untouched
        """
        GPIO.setmode(GPIO.BCM)
        cleanup_at_exit(GPIO)
        pullup = [GPIO.PUD_DOWN, GPIO.PUD_OFF, GPIO.PUD_UP][pullup + 1]
        pressed = GPIO.LOW if low_active else GPIO.HIGH
        edge = GPIO.FALLING if low_active else GPIO.RISING
        GPIO.setup(pin, GPIO.IN, pull_up_down=pullup)
        event = Event()
        GPIO.add_event_detect(pin, edge, lambda *x: event.set())

        def poll():
            k = -1
            while True:
                if k < 0:
                    event.clear()
                    event.wait()
                    k = count
                self.update(GPIO.input(pin) == pressed)
                if self.pressed:
                    k = count
                else:
                    k -= 1
                sleep(delay)

        fork(poll)

    __call__ = update
    __bool__ = is_down
