"""User interface module for symbol_please."""
import logging

import gi

from symbol_please.config import save_config
from symbol_please.ui.overlay_window import OverlayWindow
from symbol_please.ui.profile_edit_window import ProfileEditWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa: E402

_LOGGER = logging.getLogger(__name__)

REMOVE_IMAGE = Gtk.Image(stock=Gtk.STOCK_REMOVE)


class ProfileSelectWindow(Gtk.Window):
    """Main overlay window."""

    def __init__(self, config):
        """Initialize the main window."""
        super().__init__(title="Symbol Please")

        self.overlay_window = None

        self.config = config

        self.connect("destroy", self.on_destroy)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_spacing(5)

        menuhbox = Gtk.HBox()

        self.new_button = Gtk.Button(label="New")
        self.new_button.connect("clicked", self.on_new_clicked)
        menuhbox.pack_start(self.new_button, False, False, 5)

        self.edit_button = Gtk.Button(label="Edit")
        self.edit_button.connect("clicked", self.on_edit_clicked)
        menuhbox.pack_start(self.edit_button, False, False, 5)

        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.connect("clicked", self.on_delete_clicked)
        menuhbox.pack_start(self.delete_button, False, False, 5)

        vbox.pack_start(menuhbox, False, False, 5)

        self.select_listbox = Gtk.ListBox()
        self.select_listbox.set_size_request(400, 400)
        self.select_listbox.set_activate_on_single_click(False)
        self.select_listbox.connect("row-selected", self.on_row_selected)
        self.select_listbox.connect("row-activated", self.on_row_activated)

        vbox.pack_start(self.select_listbox, True, True, 5)

        starthbox = Gtk.HBox()

        self.start_button = Gtk.Button(label="Start")
        self.start_button.connect("clicked", self.on_start_clicked)
        starthbox.pack_end(self.start_button, False, False, 5)

        vbox.pack_start(starthbox, False, False, 5)

        self.add(vbox)

        self.update_profiles()
        self.update_buttons()

    def update_profiles(self):
        """Update the profile list."""
        for child in self.select_listbox.get_children():
            child.destroy()

        for profile in self.config['profiles'].keys():
            label = Gtk.Label(profile, xalign=0)
            self.select_listbox.add(label)
            label.show()

    @property
    def selected_profile_name(self):
        """Get the selected profile name."""
        selected_row = self.select_listbox.get_selected_row()
        if selected_row is None:
            return None
        return selected_row.get_children()[0].get_text()

    @property
    def selected_profile_config(self):
        """Get the selected profile name."""
        name = self.selected_profile_name
        if name is None:
            return None
        return self.config['profiles'].get(name)

    def update_buttons(self):
        """Update the enabled status of buttons."""
        enabled = self.select_listbox.get_selected_row() is not None
        self.edit_button.set_sensitive(enabled)
        self.delete_button.set_sensitive(enabled)
        self.start_button.set_sensitive(enabled)

    def on_row_selected(self, widget, row):
        """Called when the selected row changes."""
        self.update_buttons()

    def on_row_activated(self, widget, row):
        """Called when the selected row is activated."""
        self.start()

    def on_new_clicked(self, widget):
        """Create a new profile."""
        edit_window = ProfileEditWindow(self)
        response = edit_window.run()
        if response == Gtk.ResponseType.OK:
            self.config['profiles'][edit_window.profile_name] = \
                edit_window.profile_config
            save_config(self.config)
            self.update_profiles()

        edit_window.destroy()

    def on_edit_clicked(self, widget):
        """Edit a profile."""
        edit_window = ProfileEditWindow(self)
        edit_window.profile_name = self.selected_profile_name
        edit_window.profile_config = self.selected_profile_config

        response = edit_window.run()
        if response == Gtk.ResponseType.OK:
            self.config['profiles'][edit_window.profile_name] = \
                edit_window.profile_config
            save_config(self.config)
            self.update_profiles()

        edit_window.destroy()

    def on_delete_clicked(self, widget):
        """Delete a profile."""
        del self.config['profiles'][self.selected_profile_name]
        save_config(self.config)
        self.update_profiles()

    def on_start_clicked(self, widget):
        """Start parsing for the selected profile."""
        self.start()

    def on_destroy(self, widget):
        """Window is destroyed."""
        if not self.overlay_window:
            Gtk.main_quit()

    def start(self):
        """Start parsing the selected profile."""
        self.overlay_window = OverlayWindow(self.selected_profile_config)
        self.overlay_window.show_all()
        self.destroy()

    def on_exit(self):
        """Called when the application is closing."""
        if self.overlay_window is not None:
            self.overlay_window.on_exit()
