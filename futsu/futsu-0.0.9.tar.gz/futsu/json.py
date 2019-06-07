import json
import warnings

def file_input(fn):
    with open(fn,'r') as fin:
        return json.load(fin)

def file_output(fn,data):
    with open(fn,'w') as fout:
        json.dump(data,fout,sort_keys=True,indent=2)
        fout.write('\n')

def json_read(fn):
    warnings.warn('deprecated, use file_input(fn)', DeprecationWarning)
    return file_input(fn)

def json_write(fn,data):
    warnings.warn('deprecated, use file_output(fn,data)', DeprecationWarning)
    file_output(fn,data)
