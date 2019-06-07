
from sqlalchemy.types import TypeDecorator, String, Integer, UnicodeText

from .. import yaml_load, yaml_dump


# TODO move custom types to nao
class MAC(TypeDecorator):
    """Represents a MAC address in 6 bytes.

    """
    impl = String(6)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return ''.join([chr(int(i, 16)) for i in value.split(':')])

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return ':'.join(['{:0>2x}'.format(ord(i)).upper() for i in value])


class HexID(TypeDecorator):
    """Represents an 8 digit hexadecimal ID

    """
    impl = Integer

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return int(value, 16)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return '{:0>8x}'.format(value).upper()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# SQLAlchemy custom types


from sqlalchemy.types import TypeDecorator, UnicodeText
from .. import yaml_dump, yaml_load

class YAML(TypeDecorator):
    """Represents an 8 digit hexadecimal ID

    """
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        return yaml_dump(value)


    def process_result_value(self, value, dialect):
        if value is None:
            return value
        
        return yaml_load(value)


from sqlalchemy.types import TypeDecorator, Integer



# from sqlalchemy.types import TypeDecorator, Text
# import pandas as pd
# import io

# class DF(TypeDecorator):
#     """Represents a Pandas DataFrame object as a csv text

#     """

#     impl = Text  # UnicodeText might be better (pandas encodes?)

#     def process_bind_param(self, value, dialect):
#         if value is None:
#             return value

#         if isinstance(value, pd.DataFrame):
#             return value.to_csv(index=False)
        
#         raise ValueError('need Pandas DataFrame or None')


#     def process_result_value(self, value, dialect):
#         if value is None:
#             return value
        
#         return pd.read_csv(io.StringIO(value))



# somecolumn.op('&')(1) == 1

class Mask(Integer):
    """implement a binary mask based on int
    
    use the like operator to decide weather other
    is contained in the mask
    """
    class comparator_factory(Integer.Comparator):
        def like(self, other, escape=None):
            print('USED', self, other)
            return self.op("&")(other) == other  # a & b == b  <-- b contained in a



# special password hash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.types import TypeDecorator, Text

class Password(str):

    def __eq__(self, other):
        # print('CAAAAALLLLLEEEEEEEDDDDDD', self, other)

        # print('COMP', check_password_hash(generate_password_hash('valami'), 'valami'))
        return check_password_hash(self, other)


class PasswordHash(TypeDecorator):

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if isinstance(value, str):
            return generate_password_hash(value)
        
        raise ValueError('need str or None')


    def process_result_value(self, value, dialect):
        
        print('proc res val', value, dialect)
        if value is None:
            return value
        
        return Password(value)



    # class comparator_factory(Text.Comparator):
    #     def __eg__(self, other):
    #         print('CAAAAALLLLLEEEEEEEDDDDDD')
    #         return check_password_hash(self, other)

    # class comparator_factory(Text.Comparator):
    #     def __eq__(self, other):
    #         return check_password_hash(self, other)


    # def compare_values(self, x, y):
    #     """determine that the password has changed"""
    #     return check_password_hash(x, y)


# @event.listens_for(User.password, 'set')
# def hash_pass(target, value, oldvalue, initiator):
#     target.password = 
#     available = [s['name'] for s in sensors]
#     enabled = [s['name'] for s in sensors if s['enable'] == True]
#     target.sensors_available = sum([2**i for i,n in enumerate(sensor_names) if n in available])
#     target.sensors_enabled = sum([2**i for i,n in enumerate(sensor_names) if n in enabled])
#     # return sensors

from sqlalchemy.types import TypeDecorator, Integer, Enum

class PythonEnum(TypeDecorator):
    """
    This might be accomplished via sqlalchemy standard enum


    """
    impl = Enum

    def __init__(self, enumtype, **kwds):
        super().__init__(*[e.name for e in enumtype], **kwds)
        self._enumtype = enumtype


    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, self._enumtype):
            return value.name
        if isinstance(value, int):
            return self._enumtype(value).name
        if isinstance(value, str):
            return self._enumtype[value].name

        # consider it an enum member
        return value.name


    def process_result_value(self, value, dialect):
        if value is None:
            return value
        # additional check constraint...
        return self._enumtype[value].name


    class comparator_factory(TypeDecorator.Comparator):
        """override to allow int comparisons"""

        def __eq__(self, other):

            print('EQ', self, type(self), other)

        def __le__(self, other):

            print('LE', self, type(self), other)

        def __ge__(self, other):

            print('GE', self, type(self), other)

        # def operate(self, op, other):

        #     print('COMPARE', self, type(self), op, other)
        #     print(dir(self))

        #     return True

    # #         if isinstance(value, int):
    # #             o = self._enumtype(value).name
    # #         if isinstance(value, str):
    # #             o = self._enumtype[value].name

    # #         return op(self, o)

    #     def reverse_operate(self, op, other):

    #         print('RCOMPARE', self, type(self), op, other)





# # store arbitrary numpy structure
# from sqlalchemy.types import TypeDecorator, LargeBinary
# import numpy as np


# class NumpyType(TypeDecorator):
#   impl = LargeBinary

#   def process_bind_param(self, value, dialect):
#     return zlib.compress(value.dumps(), 9)

#   def process_result_value(self, value, dialect):
#     return np.loads(zlib.decompress(value))


import zlib
import pickle
from sqlalchemy.types import TypeDecorator, LargeBinary

class PythonData(TypeDecorator):
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
      return zlib.compress(pickle.dumps(value))
      # use 1 for best speed, 9 for best compression

    def process_result_value(self, value, dialect):
      return pickle.loads(zlib.decompress(value))

