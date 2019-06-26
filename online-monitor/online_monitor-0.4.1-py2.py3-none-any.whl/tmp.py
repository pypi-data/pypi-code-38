# import pyqtgraph.examples
# pyqtgraph.examples.run()

import numpy as np
import blosc
import zmq
import json
import base64


class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        """If input object is an ndarray it will be converted into a dict 
        holding dtype, shape and the data, base64 encoded.
        """
        if isinstance(obj, np.ndarray):
            if obj.flags['C_CONTIGUOUS']:
                obj_data = obj.data
            else:
                cont_obj = np.ascontiguousarray(obj)
                assert(cont_obj.flags['C_CONTIGUOUS'])
                obj_data = cont_obj.data
            obj_data = blosc.compress(obj_data, typesize=8)
            data_b64 = base64.b64encode(obj_data)
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder(self, obj)


def json_numpy_obj_hook(dct):
    """Decodes a previously encoded numpy ndarray with proper shape and dtype.

    :param dct: (dict) json encoded ndarray
    :return: (ndarray) if input was an encoded ndarray
    """
    if isinstance(dct, dict) and '__ndarray__' in dct:
        data = base64.b64decode(dct['__ndarray__'])
        data = blosc.decompress(data)
        return np.frombuffer(data, dct['dtype']).reshape(dct['shape'])
    return dct


a = np.ones((1000, 100))
print a

import StringIO
output = StringIO.StringIO()

np.save(output, a)

#arr = np.asanyarray(a)

#from numpy.lib import format

#print np.lib.format.write_array(output, arr)


print 'XXXX', len(output.getvalue())
# 
# comp = blosc.compress(output.getvalue(), typesize=8)
# print '1', len(comp)
# 
# 
# input = StringIO.StringIO()
# input.write(blosc.decompress(comp))
# input.seek(0)
# 
# print np.load(input)


#c = zmq.Context()
#sender = c.socket(zmq.PUB)
#sender.bind('tcp://127.0.0.1:5680')

msg = {'test': '23'}


f = json.dumps(msg, cls=NumpyEncoder)
# 
test = json.loads(f, object_hook=json_numpy_obj_hook)

print type(test)

a = np.random.randint(0, 1000, 1000).reshape((50, 20))