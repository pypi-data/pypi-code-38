# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Label Printing
"""

from __future__ import unicode_literals, absolute_import

import os
import os.path
import socket
import shutil

import six

from rattail.core import Object
from rattail.files import temp_path
from rattail.exceptions import LabelPrintingError
from rattail.time import localtime
from rattail.util import OrderedDict, progress_loop


class LabelPrinter(object):
    """
    Base class for all label printers.

    Label printing devices which are "natively" supported by Rattail will each
    derive from this class in order to provide implementation details specific
    to the device.  You will typically instantiate one of those subclasses (or
    one of your own design) in order to send labels to your physical printer.
    """

    profile_name = None
    formatter = None
    required_settings = None

    def __init__(self, config):
        self.config = config

    def print_labels(self, labels, *args, **kwargs):
        """
        Prints labels found in ``labels``.
        """
        raise NotImplementedError


class CommandPrinter(LabelPrinter):
    """
    Generic :class:`LabelPrinter` class which "prints" labels via native
    printer (textual) commands.  It does not directly implement any method for
    sending the commands to a printer; a subclass must be used for that.
    """

    def batch_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the first
        which are written to the file.
        """

        return None

    def batch_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the last
        which are written to the file.
        """

        return None


class CommandFilePrinter(CommandPrinter):
    """
    Generic :class:`LabelPrinter` implementation which "prints" labels to a
    file in the form of native printer (textual) commands.  The output file is
    then expected to be picked up by a file monitor, and finally sent to the
    printer from there.
    """

    required_settings = {'output_dir': "Output Folder"}
    output_dir = None

    def print_labels(self, labels, output_dir=None, progress=None):
        """
        "Prints" ``labels`` by generating a command file in the output folder.
        The full path of the output file to which commands are written will be
        returned to the caller.

        If ``output_dir`` is not specified, and the printer instance is
        associated with a :class:`LabelProfile` instance, then config will be
        consulted for the output path.  If a path still is not found, the
        current (working) directory will be assumed.
        """

        if not output_dir:
            output_dir = self.output_dir
        if not output_dir:
            raise LabelPrintingError("Printer does not have an output folder defined")

        labels_path = temp_path(prefix='rattail.', suffix='.labels')
        labels_file = open(labels_path, 'w')

        header = self.batch_header_commands()
        if header:
            labels_file.write('%s\n' % '\n'.join(header))

        commands = self.formatter.format_labels(labels, progress=progress)
        if commands is None:
            labels_file.close()
            os.remove(labels_path)
            return None

        labels_file.write(commands)

        footer = self.batch_footer_commands()
        if footer:
            labels_file.write('%s\n' % '\n'.join(footer))

        labels_file.close()
        fn = '{0}_{1}.labels'.format(
            socket.gethostname(),
            localtime(self.config).strftime('%Y-%m-%d_%H-%M-%S'))
        final_path = os.path.join(output_dir, fn)
        shutil.move(labels_path, final_path)
        return final_path


# Force ordering for network printer required settings.
settings = OrderedDict()
settings['address'] = "IP Address"
settings['port'] = "Port"
settings['timeout'] = "Timeout"

class CommandNetworkPrinter(CommandPrinter):
    """
    Generic :class:`LabelPrinter` implementation which "prints" labels to a
    network socket in the form of native printer (textual) commands.  The
    socket is assumed to exist on a networked label printer.
    """

    required_settings = settings
    address = None
    port = None
    timeout = None

    def print_labels(self, labels, progress=None):
        """
        Prints ``labels`` by generating commands and sending directly to a
        socket which exists on a networked printer.
        """

        if not self.address:
            raise LabelPrintingError("Printer does not have an IP address defined")
        if not self.port:
            raise LabelPrintingError("Printer does not have a port defined.")

        data = six.StringIO()

        header = self.batch_header_commands()
        if header:
            header = "{0}\n".format('\n'.join(header))
            data.write(header.encode('utf_8'))

        commands = self.formatter.format_labels(labels, progress=progress)
        if commands is None: # process canceled?
            data.close()
            return None
        data.write(commands.encode('utf_8'))

        footer = self.batch_footer_commands()
        if footer:
            footer = "{0}\n".format('\n'.join(footer))
            data.write(footer.encode('utf_8'))

        try:
            timeout = int(self.timeout)
        except ValueError:
            timeout = socket.getdefaulttimeout()

        try:
            # Must pass byte-strings (not unicode) to this function.
            sock = socket.create_connection((self.address.decode('utf_8'), int(self.port)), timeout)
            bytes = sock.send(data.getvalue())
            sock.close()
            return bytes
        finally:
            data.close()


class LabelFormatter(Object):
    """
    Base class for all label formatters.
    """
    format = None

    def __init__(self, config):
        self.config = config

    @property
    def default_format(self):
        """
        Default format for labels.  This should be defined by the derived
        formatter class.  It will be used if no format is defined within the
        label profile.
        """

        raise NotImplementedError

    def format_labels(self, labels, progress=None, *args, **kwargs):
        """
        Formats ``labels`` and returns the result.
        """
        raise NotImplementedError


class CommandFormatter(LabelFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.
    """

    def format_labels(self, labels, progress=None):
        fmt = six.StringIO()

        def format_label(record, i):
            product, quantity, data = record
            for j in range(quantity):
                header = self.label_header_commands()
                if header:
                    header = "{0}\n".format('\n'.join(header))
                    fmt.write(header.encode('utf_8'))
                body = "{}\n".format('\n'.join(self.label_body_commands(product, **data)))
                if six.PY3:
                    fmt.write(body)
                else: # PY2
                    fmt.write(body.encode('utf_8'))
                footer = self.label_footer_commands()
                if footer:
                    footer = "{0}\n".format('\n'.join(footer))
                    fmt.write(footer.encode('utf_8'))

        progress_loop(format_label, labels, progress,
                      message="Formatting labels")

        if six.PY3:
            val = fmt.getvalue()
        else: # PY2
            val = fmt.getvalue().decode('utf_8')
        fmt.close()
        return val

    def label_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immediately
        precede each *label* in one-up printing, and immediately precede each
        *label pair* in two-up printing.
        """

        return None

    def label_body_commands(self, product, **kwargs):
        raise NotImplementedError

    def label_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immedately
        follow each *label* in one-up printing, and immediately follow each
        *label pair* in two-up printing.
        """

        return None


class TwoUpCommandFormatter(CommandFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.

    This class contains logic to implement "two-up" label printing.
    """

    @property
    def half_offset(self):
        """
        The X-coordinate value by which the second label should be offset, when
        two labels are printed side-by-side.
        """
        raise NotImplementedError

    def format_labels(self, labels, progress=None):
        fmt = six.StringIO()
        self.half_started = False

        def format_label(record, i):
            product, quantity, data = record
            for j in range(quantity):
                kw = dict(data)
                if self.half_started:
                    kw['x'] = self.half_offset
                    fmt.write('{}\n'.format('\n'.join(self.label_body_commands(product, **kw))))
                    footer = self.label_footer_commands()
                    if footer:
                        fmt.write('{}\n'.format('\n'.join(footer)))
                    self.half_started = False
                else:
                    header = self.label_header_commands()
                    if header:
                        fmt.write('{}\n'.format('\n'.join(header)))
                    kw['x'] = 0
                    fmt.write('{}\n'.format('\n'.join(self.label_body_commands(product, **kw))))
                    self.half_started = True

        progress_loop(format_label, labels, progress,
                      message="Formatting labels")

        if self.half_started:
            footer = self.label_footer_commands()
            if footer:
                fmt.write('{}\n'.format('\n'.join(footer)))

        val = fmt.getvalue()
        fmt.close()
        return val
