# Copyright (c) 2013, Combine Control Systems AB
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
    DataImporterLocator, ADAFDataImporterBase, TableDataImporterBase,
    TextDataImporterBase)


def table_importer_from_filename_factory(fq_filename):
    dil = DataImporterLocator(TableDataImporterBase)
    importer = dil.importer_from_sniffer(fq_filename)
    return importer


def adaf_importer_from_filename_factory(fq_filename):
    dil = DataImporterLocator(ADAFDataImporterBase)
    importer = dil.importer_from_sniffer(fq_filename)
    return importer


def text_importer_from_filename_factory(fq_filename):
    dil = DataImporterLocator(TextDataImporterBase)
    importer = dil.importer_from_sniffer(fq_filename)
    return importer


def table_importer_from_datasource_factory(datasource, importer_type):
    return importer_from_datasource_factory(
        datasource, importer_type, TableDataImporterBase)


def adaf_importer_from_datasource_factory(datasource, importer_type):
    return importer_from_datasource_factory(
        datasource, importer_type, ADAFDataImporterBase)


def text_importer_from_datasource_factory(datasource, importer_type):
    return importer_from_datasource_factory(
        datasource, importer_type, TextDataImporterBase)


def importer_from_datasource_factory(datasource, importer_type,
                                     importer_base_class):
    dil = DataImporterLocator(importer_base_class)
    assert(importer_type is not None)
    importer = dil.importer_from_name(importer_type)
    return importer


def available_adaf_importers():
    dil = DataImporterLocator(ADAFDataImporterBase)
    return dil.available_importers()


def available_table_importers(datasource_compatibility=None):
    dil = DataImporterLocator(TableDataImporterBase)
    return dil.available_importers(datasource_compatibility)


def available_text_importers():
    dil = DataImporterLocator(TextDataImporterBase)
    return dil.available_importers()


def available_adaf_importer_names():
    dil = DataImporterLocator(ADAFDataImporterBase)
    return sorted(dil.available_importers().keys())


def available_table_importer_names():
    dil = DataImporterLocator(TableDataImporterBase)
    return sorted(dil.available_importers().keys())
