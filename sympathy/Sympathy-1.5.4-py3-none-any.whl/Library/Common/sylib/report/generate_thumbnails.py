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
import json
import sys
import six


THUMBNAIL_WIDTH = 64


def main():
    """This function should always be run in its own process to avoid polluting
    the worker process with a QApplication.
    """
    (sys_path_json, template, data_filename, data_type) = sys.argv[1:]
    sys.path[:] = json.loads(sys_path_json)

    from sympathy.api import adaf, table
    from sympathy.api import qt
    from sylib.report import data_manager
    from sylib.report import models
    from sylib.report import binding
    from sylib.report import plugins
    QtGui = qt.QtGui  # noqa
    QtCore = qt.QtCore  # noqa

    def file_type(data_type):
        if data_type == 'adafs':
            return adaf.FileList
        elif data_type == 'tables':
            return table.FileList
        else:
            assert(False)

    # In this process it is safe to create a QApplication.
    app = QtGui.QApplication([])  # noqa

    # Read the data from the transfer file.
    with file_type(data_type)(filename=data_filename, mode='r') as input_data:

        data_manager.init_data_source(input_data, data_type)
        model = models.Root(json.loads(template))
        backend = plugins.backend_modules['mpl'].backend
        binding_context = binding.BindingContext()
        factory = backend.ItemFactory(binding_context)
        page_models = model.find_all_nodes_with_class(models.Page)
        page_count = len(page_models)

        # Generate thumbnails.
        thumbnails = []
        if page_count > 0:
            for page_index, page_model in enumerate(page_models):
                page_widget = factory._create_page(page_model)
                QtGui.QApplication.processEvents()

                pixmap = QtGui.QPixmap.grabWidget(page_widget)
                pixmap = pixmap.scaledToWidth(THUMBNAIL_WIDTH,
                                              QtCore.Qt.SmoothTransformation)
                bytes = QtCore.QByteArray()
                buffer = QtCore.QBuffer(bytes)
                buffer.open(QtCore.QIODevice.WriteOnly)
                pixmap.save(buffer, 'PNG')
                buffer.close()
                thumbnails.append(six.text_type(bytes.toBase64()))
    print(json.dumps(thumbnails))


if __name__ == '__main__':
    main()
