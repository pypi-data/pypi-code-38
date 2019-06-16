#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Base parser class
#
from enum import Enum
import numpy as np
import pandas as pd
from ... import util

__all__ = ['ParserType', 'Parser']


class ParserType(Enum):
    """ Enum for differentiating between different parser types. """
    UNDEFINED = 0       #: Undefined parsertype. Do not use this!
    SINGLE_FILE = 1     #: One single file contains all annotations
    MULTI_FILE = 2      #: One annotation file per :any:`brambox.io.parser.Parser.serialize_group`
    EXTERNAL = 3        #: External type that takes care of its own IO. Use this type sparingly as it is harder to test!


class Parser:
    """ This is a generic parser class. """
    parser_type = ParserType.UNDEFINED  #: Type of parser. Derived classes should set the correct value.
    extension = '.txt'                  #: Extension of the files this parser parses or creates. Derived classes should set the correct extension.
    read_mode = 'r'                     #: Reading mode this parser uses when it parses a file. Derived classes should set the correct mode.
    write_mode = 'w'                    #: Writing mode this parser uses when it generates a file. Derived classes should set the correct mode.
    pre_serialize = None                #: Function that runs before serialization and can modify the dataframe (takes a copy of the df as argument and must return a df)
    post_deserialize = None             #: Function that runs after deserialization and can modify the dataframe (takes a copy of the df as argument and must return a df)
    serialize_group = 'image'           #: Controls on what column the dataframe gets grouped for serialization.
    serialize_group_separator = ''      #: Only for ParserType.SINGLE_FILE! Controls what character to place in between the different groups of text (usually images)
    header = ''                         #: Header string to put at the beginning of each file
    footer = ''                         #: Footer string to put at the end of each file

    def __init__(self):
        self.images = set()

    def append_image(self, image):
        """ Call this function if there are no bounding boxes for a certain image.
        If you added a bounding box of an image with the `append` method, it is not necessary to call this function,
        but doing so does not hurt either.
        """
        self.images.add(image)

    def get_df(self):
        """ This function generates a pandas dataframe from the dictionary in `self.data`,
        after the deserialize function generated that dictionary.
        """
        if isinstance(self.data, pd.DataFrame):
            return self.data

        df = util.from_dict(self.data, self.images)

        if self.post_deserialize is not None:
            df = self.post_deserialize(df)

        return df

    def deserialize(self, rawdata, file_id=None):
        """ This function needs to be implemented by the custom parser.
        It gets the rawdata from the file (eg. string) and needs to fill in the `self.data` dictionary
        with the correct values.
        """
        raise NotImplementedError('This function should be implemented in the custom parser')

    def serialize(self, df):
        """ This function needs to be implemented by the custom parser.
        Its goal is to return the rawdata (eg. string) from the bounding boxes of one `self.serialize_group`.
        """
        raise NotImplementedError('This function should be implemented in the custom parser')
