import json

def json_read(fn):
    with open(fn,'r') as fin:
        return json.load(fin)

def json_write(fn,data):
    with open(fn,'w') as fout:
        json.dump(data,fout,sort_keys=True,indent=2)
        fout.write('\n')
