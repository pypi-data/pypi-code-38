from .abstractalephmarcreader import AbstractAlephMarcReader
import pymarc
import codecs
import sys


class AlephMarc21Reader(AbstractAlephMarcReader):
    """
    Represents the record read from a Marc21 file.
    :param pymarc.record.Record __record record read from a Marc21 file.
    """
    def __init__(self, file_path):
        """
        :param str file_path: the path to the Marc21 file.
        """
        super(AlephMarc21Reader, self).__init__('0')
        marc21 = self.__get_marc21(file_path)
        self.__record = self.__get_record(marc21)

    def __get_marc21(self, file_path):
        """
        Returns the contents of a Marc21 file as binary data.
        :param str file_path: the path to the Marc21 file.
        :return: bytes
        """

        try:
            marc_file = codecs.open(file_path, 'rb')
            marc21 = marc_file.read()
            marc_file.close()

            return marc21

        except Exception as e:
            sys.stderr.write("Getting Marc21 failed: " + str(e) + " for file_path: " + file_path + "\n")
            raise
    __get_marc21.__annotations__ = {'file_path': str, 'return': bytes}

    def __get_record(self, marc21):
        """
        Parses the given Marc21 data and returns the record.
        :param bytes marc21: Marc21 data.
        :return: pymarc.record.Record
        """
        try:
            reader = pymarc.MARCReader(marc21, force_utf8=True, to_unicode=True)
            return next(reader)
        except Exception as e:
            sys.stderr.write("Error reading Marc21 data: " + str(e) + '\n')
            raise
    __get_record.__annotations__ = {'marc21': bytes, 'return': pymarc.record.Record}

    def _AbstractAlephMarcReader__get_subfield_texts(self, marc_field, index):
        """
        Given a marc field, get the indicated subfield's text or False if it does not exist.
        :param marc_field: marc field.
        :param index: index of the subfield.
        :return: [str].
        """

        return marc_field.get_subfields(index)

    _AbstractAlephMarcReader__get_subfield_texts.__annotations__ = {'index': str, 'marc_field': pymarc.field.Field, 'return': [str]}

    def _AbstractAlephMarcReader__get_field(self, index):
        """
        Returns marc fields corresponding to the given index.
        :param index: index of marc field.
        :return: [pymarc.field.Field]
        """
        elements = self.__record.get_fields(index)
        return elements
    _AbstractAlephMarcReader__get_field.__annotations__ = {'index': str, 'return': [pymarc.field.Field]}

