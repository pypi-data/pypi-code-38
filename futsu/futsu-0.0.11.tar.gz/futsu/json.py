import json
import warnings

def file_to_data(fn):
    with open(fn,'r') as fin:
        return json.load(fin)

def data_to_file(fn,data):
    with open(fn,'w') as fout:
        json.dump(data,fout,sort_keys=True,indent=2)
        fout.write('\n')

def json_read(fn):
    warnings.warn('deprecated, use file_to_data(fn)', DeprecationWarning)
    return file_to_data(fn)

def json_write(fn,data):
    warnings.warn('deprecated, use data_to_file(fn,data)', DeprecationWarning)
    data_to_file(fn,data)
