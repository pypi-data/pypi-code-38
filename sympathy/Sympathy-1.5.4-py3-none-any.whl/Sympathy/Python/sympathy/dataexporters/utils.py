# Copyright (c) 2016, Combine Control Systems AB
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
from . base import (
    DataExporterLocator, TableDataExporterBase, TextDataExporterBase,
    ADAFDataExporterBase, DatasourceDataExporterBase, FigureDataExporterBase)


def table_exporter_factory(exporter_type):
    dil = DataExporterLocator(TableDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def text_exporter_factory(exporter_type):
    dil = DataExporterLocator(TextDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def adaf_exporter_factory(exporter_type):
    dil = DataExporterLocator(ADAFDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def datasource_exporter_factory(exporter_type):
    dil = DataExporterLocator(DatasourceDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def figure_exporter_factory(exporter_type):
    dil = DataExporterLocator(FigureDataExporterBase)
    exporter = dil.exporter_from_name(exporter_type)
    return exporter


def available_table_exporters():
    exporter_locator = DataExporterLocator(TableDataExporterBase)
    return exporter_locator.available_exporters()


def available_text_exporters():
    exporter_locator = DataExporterLocator(TextDataExporterBase)
    return exporter_locator.available_exporters()


def available_adaf_exporters():
    exporter_locator = DataExporterLocator(ADAFDataExporterBase)
    return exporter_locator.available_exporters()


def available_datasource_exporters():
    exporter_locator = DataExporterLocator(DatasourceDataExporterBase)
    return exporter_locator.available_exporters()


def available_figure_exporters():
    exporter_locator = DataExporterLocator(FigureDataExporterBase)
    return exporter_locator.available_exporters()
