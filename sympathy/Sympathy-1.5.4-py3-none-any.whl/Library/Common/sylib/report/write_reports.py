
# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import os
import json
import sys
import six

marker = '__WRITE_REPORT_MARKER__'


def main():
    """This function should always be run in its own process to avoid polluting
    the worker process with a QApplication.
    """
    (sys_path, template, signal_mapping, data_filename, data_type,
     file_format, save_path, prefix, input_filenames) = json.loads(sys.argv[1])

    if six.PY2:
        fs_encoding = sys.getfilesystemencoding()
        sys_path = [p.encode(fs_encoding) for p in sys_path]
    sys.path[:] = sys_path

    from sympathy.api import adaf, table
    from sympathy.api import qt
    from sylib.report import data_manager
    from sylib.report import models
    from sylib.report import binding
    from sylib.report import plugins
    QtGui = qt.QtGui  # noqa

    fs_encoding = sys.getfilesystemencoding()

    def create_pdf(filename, pixmaps):
        printer = QtGui.QPrinter(QtGui.QPrinter.ScreenResolution)
        printer.setPaperSize(QtGui.QPrinter.A4)
        printer.setOutputFileName(filename)
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        painter = QtGui.QPainter(printer)
        for i, pixmap in enumerate(pixmaps):
            painter.drawPixmap(0, 0, pixmap)
            if i < len(pixmaps) - 1:
                printer.newPage()
        painter.end()

        if printer.printerState() == QtGui.QPrinter.Idle:
            return True
        else:
            return False

    def file_type(data_type):
        if data_type == 'adafs':
            return adaf.FileList
        elif data_type == 'tables':
            return table.FileList
        else:
            assert(False)

    def warn(msg):
        sys.stderr.write("__WARNING__ ({})\n".format(msg))

    def error(msg):
        sys.stderr.write("__ERROR__ ({})\n".format(msg))
        sys.exit()

    def check_status(status, filename):
        if not status:
            error("Could not write to file {}".format(filename))
    # In this process it is safe to create a QApplication.
    app = QtGui.QApplication([])  # noqa

    # Extract all pages manually to get minimal size images for all pages.
    model = models.Root(json.loads(template))
    page_models = model.find_all_nodes_with_class(models.Page)
    page_count = len(page_models)

    # Create filenames for all pages.
    pdf_file = None
    if input_filenames is None:
        if not save_path:
            error("Please specify a save path.")
        if file_format == 'pdf':
            pdf_file = '{}.{}'.format(prefix, file_format)
        basenames = ['{}_{}.{}'.format(prefix, i, file_format)
                     for i in range(page_count)]
        input_filenames = [os.path.join(save_path, basename)
                           for basename in basenames]
    elif file_format != 'pdf':
        if len(input_filenames) < page_count:
            error("Not enough filenames.")
        elif len(input_filenames) > page_count:
            warn("Too many filenames.")
    # Read the data from the transfer file.
    if isinstance(data_filename, six.binary_type):
        data_filename = data_filename.decode(fs_encoding)

    with file_type(data_type)(filename=data_filename, mode='r') as input_data:

        data_manager.init_data_source(input_data, data_type)
        data_manager.data_source.set_signal_mapping(json.loads(signal_mapping))

        QtGui.QApplication.processEvents()

        # Extract widgets.
        backend = plugins.backend_modules['mpl'].backend
        binding_context = binding.BindingContext()
        factory = backend.ItemFactory(binding_context)
        page_widgets = [factory._create_page(m) for m in page_models]

        # This hack is needed for matplotlib>=2.1.0. Without it all graphs
        # are empty when we grab the widgets again later.
        for page_widget in page_widgets:
            QtGui.QPixmap.grabWidget(page_widget)

        QtGui.QApplication.processEvents()

        # Write widgets to file.
        output_filenames = []
        pdf_pixmaps = []
        for i, (page_widget, filename) in enumerate(
                zip(page_widgets, input_filenames)):
            try:
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
            except (OSError, IOError):
                error("Could not create output directory {}".format(
                    os.path.dirname(filename)))
            pixmap = QtGui.QPixmap.grabWidget(page_widget)
            if file_format == 'pdf':
                pdf_pixmaps.append(pixmap)
            else:
                status = pixmap.save(filename, format=file_format)
                check_status(status, filename)
            output_filenames.append(filename)
        if file_format == 'pdf':
            if pdf_file is None:
                pdf_file = input_filenames[0]
            if os.path.splitext(pdf_file)[1] != '.pdf':
                error('Save filename is not a PDF.')
            status = create_pdf(pdf_file, pdf_pixmaps)
            check_status(status, pdf_file)
            output_filenames = [pdf_file]

        for page_widget in page_widgets:
            page_widget.deleteLater()

        QtGui.QApplication.processEvents()

        sys.stdout.write(marker)
        sys.stdout.write(json.dumps(output_filenames))


if __name__ == '__main__':
    main()
