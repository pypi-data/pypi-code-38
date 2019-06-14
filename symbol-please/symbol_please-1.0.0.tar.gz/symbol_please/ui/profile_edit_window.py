"""User interface module for symbol_please."""
import logging

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa: E402

_LOGGER = logging.getLogger(__name__)


class ProfileEditWindow(Gtk.Dialog):
    """Main overlay window."""

    def __init__(self, parent, profile=None):
        """Initialize the main window."""
        super().__init__("Symbol Please", parent, 0, (
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.response = Gtk.ResponseType.CANCEL

        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_spacing(5)

        label = Gtk.Label("Profile Name:")
        label.set_xalign(0)
        vbox.pack_start(label, False, False, 5)

        self.name_entry = Gtk.Entry()
        vbox.pack_start(self.name_entry, False, False, 5)

        label = Gtk.Label("Log file:")
        label.set_xalign(0)
        vbox.pack_start(label, False, False, 5)

        logfilehbox = Gtk.HBox(spacing=5)

        self.logfile_entry = Gtk.Entry()
        self.logfile_entry.set_size_request(400, 0)

        logfilehbox.pack_start(self.logfile_entry, True, True, 5)

        open_image = Gtk.Image(stock=Gtk.STOCK_OPEN)
        logfile_open_button = Gtk.Button(image=open_image)
        logfile_open_button.connect("clicked", self.on_logfile_open_clicked)

        logfilehbox.pack_start(logfile_open_button, False, False, 5)

        vbox.pack_start(logfilehbox, False, False, 5)

        label = Gtk.Label("Character Level:")
        label.set_xalign(0)
        vbox.pack_start(label, False, False, 5)

        self.level_entry = Gtk.SpinButton.new_with_range(1, 60, 1)
        vbox.pack_start(self.level_entry, False, False, 5)

        self.get_content_area().add(vbox)
        self.show_all()

    def on_logfile_open_clicked(self, widget):
        """Select the log file."""
        dialog = Gtk.FileChooserDialog(
            "Please select the log file for this profile", self,
            Gtk.FileChooserAction.OPEN, (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_logs = Gtk.FileFilter()
        filter_logs.set_name("Log files (*.txt)")
        filter_logs.add_pattern("*.txt")
        dialog.add_filter(filter_logs)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.logfile_entry.set_text(dialog.get_filename())

        dialog.destroy()

    @property
    def profile_name(self):
        """Get the entered profile name."""
        return self.name_entry.get_text()

    @profile_name.setter
    def profile_name(self, value):
        """Set the entered profile name."""
        self.name_entry.set_text(value)

    @property
    def profile_config(self):
        """Get the entered profile config."""
        log_file = self.logfile_entry.get_text()
        level = self.level_entry.get_value()

        return {
            'log_file': log_file,
            'level': level,
        }

    @profile_config.setter
    def profile_config(self, value):
        """Set the entered profile config."""
        self.logfile_entry.set_text(value.get('log_file', ''))
        self.level_entry.set_value(value.get('level', 1))
