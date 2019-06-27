# -*- coding: utf-8 -*-
from . import presentation_line
import zipfile
import io
import time
import base64


class Presentation(object):

    def __init__(self, presentation, presentation_type):
        self._lines = []
        self._presentation = presentation
        self._presentation_type = presentation_type

    def get_encoded_string(self):
        """ return: String en base 64 """
        return base64.b64encode(self.get_string().encode())

    def get_string(self):
        """
        :return: String con todas las lineas de esa lista
        """
        eol = '\r\n'
        presentation_string = eol.join(line.get_line_string() for line in self.lines) + eol
        return presentation_string

    def create_line(self):
        line = presentation_line.PresentationLine.factory(self.presentation, self.presentation_type)
        self.add_line(line)
        return line

    @property
    def lines(self):
        return self._lines

    def add_line(self, item):
        self.lines.append(item)

    @property
    def presentation(self):
        return self._presentation

    @property
    def presentation_type(self):
        return self._presentation_type


class PresentationZipExporter(object):

    def __init__(self):
        # Lista de presentaciones
        self._presentations_to_export = []

    def export_elements(self):
        """ Exporta las presentaciones a un archivo ZIP en base 64 """

        zip_buffer = io.BytesIO()
        zf = zipfile.ZipFile(zip_buffer, mode='a', compression=zipfile.ZIP_DEFLATED)

        for presentation in self.presentations_to_export:

            if not presentation.file_name:
                raise AttributeError("La presentacion no tiene nombre para el archivo")

            info = zipfile.ZipInfo(presentation.file_name, date_time=time.localtime(time.time()), )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 0
            zf.writestr(info, presentation.get_string())

        zf.close()
        return base64.b64encode(zip_buffer.getvalue())

    @property
    def presentations_to_export(self):
        return self._presentations_to_export

    def add_element(self, presentation):
        self.presentations_to_export.append(presentation)
