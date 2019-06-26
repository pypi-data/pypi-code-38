import logging
import decimal
import json
import uuid
import base64
import datetime
import importlib

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GuidUrlSafe:

    @classmethod
    def generate(cls):
        id_uuid = uuid.uuid4()
        id_string = base64.urlsafe_b64encode(id_uuid.bytes).decode("utf-8")
        start_of_padding = id_string.find('=')
        if (start_of_padding >= 0):
            id_string = id_string[:start_of_padding]

        return id_string



class ExtendedJsonEncoder(json.JSONEncoder):

    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This code permits the class to handle pandas timestamp when the module is present
        # and skip it when pandas is not present.
        #
        # Consider: This seems like a ton of work for a constructor
        #
        self.pandas_dynamic = None

        try:
            self.pandas_dynamic = importlib.import_module('pandas')
        except ImportError as err:
            #pandas not found, leave as null so it can be skipped below
            pass

        self.np_dynamic = None
        try:
            self.np_dynamic = importlib.import_module('numpy')
        except ImportError as err:
            # numpy not found, leave as null so it can be skipped below
            pass


    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o % 1) > 0:  # without abs() negative float values were being converted to int
                return float(o)
            else:
                return int(o)
        elif isinstance(o, set):
            return list(o)
        elif ((self.pandas_dynamic is not None) and ( isinstance(o, self.pandas_dynamic.Timestamp)) ):
            posix_float_timestamp = o.timestamp()
            timestamp_as_millis = int(1000.0 * posix_float_timestamp)
            return int(timestamp_as_millis)
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif (self.np_dynamic is not None):
            np =self.np_dynamic
            if isinstance(o, (np.int_, np.intc, np.intp, np.int8,
                              np.int16, np.int32, np.int64, np.uint8,
                              np.uint16, np.uint32, np.uint64)):
                return int(o)
            elif isinstance(o, (np.float_, np.float16, np.float32,
                                np.float64)):
                return float(o)
            elif isinstance(o, (np.ndarray,)):  #### This is the fix
                return o.tolist()



        return super(ExtendedJsonEncoder, self).default(o)
