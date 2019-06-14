"""User interface module for symbol_please."""
from collections import OrderedDict
import datetime
import logging
import queue

import cairo
import gi

from symbol_please.parser import ParserThread
from symbol_please.parser.spell import SpellEventCast, SpellEventExpired

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, Gdk  # noqa: E402

_LOGGER = logging.getLogger(__name__)

REMOVE_IMAGE = Gtk.Image(stock=Gtk.STOCK_REMOVE)


def effect_remaining_time(effect):
    """Calculate remaining time for effect."""
    now = datetime.datetime.now()
    cast_time = effect.cast_time
    duration = effect.duration

    elapsed_time = (now - cast_time).total_seconds()
    return duration - elapsed_time


class OverlayWindow(Gtk.Window):
    """Main overlay window."""

    def __init__(self, config):
        """Initialize the main window."""
        super().__init__(title="Symbol Please")

        self.connect("destroy", Gtk.main_quit)

        self.parser = ParserThread(config)
        self.parser.start()

        self._event_queue = self.parser.client.add_event_listener_thread()
        self._active_effects = OrderedDict()
        self._effect_hboxes = {}
        self._effect_bars = {}
        self._effect_remove_btns = {}

        self.locked = False

        self.set_decorated(False)
        self.set_size_request(500, 0)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_keep_above(True)

        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.on_button_press)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)

        self.lock_button = Gtk.Button(label="Lock")
        self.lock_button.connect("clicked", self.on_lock_clicked)

        self.vbox = Gtk.VBox(spacing=5)
        self.vbox.set_spacing(5)

        tophbox = Gtk.HBox()
        tophbox.pack_start(self.lock_button, False, False, 5)

        quit_image = Gtk.Image(stock=Gtk.STOCK_QUIT)
        self.quit_button = Gtk.Button(image=quit_image)
        self.quit_button.connect("clicked", Gtk.main_quit)
        tophbox.pack_end(self.quit_button, False, False, 5)

        self.vbox.pack_start(tophbox, False, False, 0)

        self.contentvbox = Gtk.VBox()
        self.contentvbox.set_spacing(5)
        self.vbox.pack_start(self.contentvbox, True, True, 5)

        self.add(self.vbox)

        self.set_opacity(0.8)

        GLib.timeout_add(25, self.update)

    def on_button_press(self, widget, event):
        """On main window button press."""
        # Only handle left clicks
        if event.button == 1:
            if event.x <= 20:
                # If clicking the left side, begin a resize
                self.get_window().begin_resize_drag_for_device(
                    Gdk.WindowEdge.WEST, event.device, event.button,
                    event.x_root, event.y_root, event.time)
            elif self.get_size().width - event.x <= 20:
                # If clicking the right side, begin a resize
                self.get_window().begin_resize_drag_for_device(
                    Gdk.WindowEdge.EAST, event.device, event.button,
                    event.x_root, event.y_root, event.time)
            else:
                # Otherwise begin a move
                self.get_window().begin_move_drag_for_device(
                    event.device, event.button, event.x_root, event.y_root,
                    event.time)
            return True

    def on_lock_clicked(self, widget):
        """On lock button clicked."""
        self.locked = not self.locked
        # self.set_app_paintable(self.locked)
        if self.locked:
            self.lock_button.set_label("Unlock")
            self.set_opacity(0.5)
            self.lock_allocate_handler = self.lock_button.connect(
                "size-allocate", self.on_lock_size_allocate)
            self.quit_button.hide()
        else:
            self.lock_button.set_label("Lock")
            self.set_opacity(0.8)
            self.quit_button.show()

        for btn in self._effect_remove_btns.values():
            if self.locked:
                btn.hide()
            else:
                btn.show()

    def on_lock_size_allocate(self, widget, area):
        """On lock button clicked."""
        self.lock_button.disconnect(self.lock_allocate_handler)
        if self.locked:
            rectangle_int = cairo.RectangleInt(
                area.x, area.y, area.width, area.height)
            self.get_window().input_shape_combine_region(
                cairo.Region(rectangle_int), 0, 0)

    def update(self):
        """Run periodic updates on UI thread."""
        self.check_event_queue()
        self.update_effects()
        return True

    def update_effects(self):
        """Repack the effect progress bars."""
        for instance_id in self._active_effects.keys():
            name = self._active_effects[instance_id].spell['name']
            target = self._active_effects[instance_id].target

            remaining_time = effect_remaining_time(
                self._active_effects[instance_id])
            duration = self._active_effects[instance_id].duration

            self._effect_bars[instance_id].set_fraction(
                remaining_time / duration)

            if remaining_time >= 100:
                remaining_mins = int(remaining_time / 60)
                self._effect_bars[instance_id].set_text(
                    "{} - {} ({}m)".format(name, target, remaining_mins))
            elif remaining_time > 0:
                remaining_secs = int(remaining_time)
                self._effect_bars[instance_id].set_text(
                    "{} - {} ({}s)".format(name, target, remaining_secs))
            elif remaining_time <= -100:
                expired_mins = int(remaining_time * -1 / 60)
                self._effect_bars[instance_id].set_text(
                    "{} - {} (Expired {}m)".format(name, target, expired_mins))
            else:
                expired_secs = int(remaining_time * -1)
                self._effect_bars[instance_id].set_text(
                    "{} - {} (Expired {}s)".format(name, target, expired_secs))

    def redraw_effects(self):
        """Repack the effect progress bars."""
        self._active_effects = OrderedDict(sorted(
            self._active_effects.items(),
            key=lambda item: effect_remaining_time(item[1])))
        self.update_effects()

        for child in self.contentvbox:
            self.contentvbox.remove(child)

        for instance_id in self._active_effects.keys():
            self.contentvbox.pack_start(
                self._effect_hboxes[instance_id], False, False, 0)

            self._effect_hboxes[instance_id].show()
            self._effect_bars[instance_id].show()
            if not self.locked:
                self._effect_remove_btns[instance_id].show()
        width = self.get_size()[0]
        self.resize(width, 1)

    def check_event_queue(self):
        """Check the event queue for new events."""
        try:
            while True:
                event = self._event_queue.get_nowait()
                self.on_parser_event(event)
        except queue.Empty:
            pass

    def on_remove_click(self, instance_id):
        """Called when a remove button is clicked."""
        self.remove_effect(instance_id)

    def remove_effect(self, instance_id):
        """Remove a tracked effect."""
        self._active_effects.pop(instance_id, None)
        self._effect_bars.pop(instance_id, None)
        self._effect_hboxes.pop(instance_id, None)
        self._effect_remove_btns.pop(instance_id, None)
        self.redraw_effects()

    def on_parser_event(self, event):
        """Called when a parser event is triggered."""
        _LOGGER.info("Detected event %s", event)
        if isinstance(event, SpellEventCast):
            if event.duration is None:
                return
            self._active_effects[event.instance_id] = event

            bar = Gtk.ProgressBar()
            bar.set_show_text(True)
            self._effect_bars[event.instance_id] = bar

            remove_btn = Gtk.Button(image=REMOVE_IMAGE)
            self._effect_remove_btns[event.instance_id] = remove_btn
            remove_btn.connect(
                "clicked", lambda *_: self.on_remove_click(event.instance_id))

            hbox = Gtk.HBox()
            hbox.pack_start(bar, True, True, 5)
            hbox.pack_start(remove_btn, False, False, 5)
            self._effect_hboxes[event.instance_id] = hbox

            self.redraw_effects()

        elif isinstance(event, SpellEventExpired):
            self.remove_effect(event.instance_id)

    def on_exit(self):
        """Called when the application is closing."""
        self.parser.stop()
