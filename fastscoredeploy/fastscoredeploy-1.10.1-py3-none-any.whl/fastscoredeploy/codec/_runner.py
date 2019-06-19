
##  See https://opendatagoup.atlassian.net/wiki/x/UpDhAg (recordsets only).

import json
import fastavro
from io import BytesIO
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd

class _Codec(object):

    codecs = {}

    INPUT   = 0
    OUTPUT  = 1

    NULL = 0  ## what a clumsy constant
    UTF8 = 1
    JSON = 2
    AVRO = 3
    SOAP = 4

    MARKERS = {
      NULL: b'\xfastscore.set',
      UTF8: b'\u262efastscore.set',
      JSON: b'{"$fastscore": "set"}',
      AVRO: b'\x1c\x24\x66\x61\x73\x74\x73\x63\x6f\x72\x65\x2e\x73\x65\x74\x00\x00\x00',
      SOAP: b'<fastscore-set />'
    }

    def __init__(self, direction):
        self._direction = direction
        self._encoding = _Codec.NULL
        self._schema = None
        self._recordsets = False
        self.prepare()

    @staticmethod
    def slot_to_codec(slot):
        if not slot in _Codec.codecs:
            direction = slot & 1
            _Codec.codecs[slot] = _Codec(direction)
        return _Codec.codecs[slot]

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, enc):
        ## called for each batch of record -- be careful
        if self._encoding != enc:
            self._encoding = enc
            self.prepare()

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, schema):
        if self._schema != schema:
            self._schema = schema
            self.prepare()

    @property
    def recordsets(self):
        return self._recordsets

    @recordsets.setter
    def recordsets(self, flag):
        if self._recordsets != flag:
            self._recordsets = flag
            self.prepare()

    @property
    def encode(self):
        return self._encode
    
    @property
    def decode(self):
        return self._decode

    def prepare(self):
        if self._direction == _Codec.INPUT:
            self.prepare_input()
        else:
            self.prepare_output()

    def prepare_input(self):
        self._encode = None
        if self._encoding == _Codec.NULL:
            basic_decode = lambda x: x
        elif self._encoding == _Codec.UTF8:
            basic_decode = lambda x: x.decode('utf-8')
        elif self._encoding == _Codec.JSON:
            basic_decode = lambda x: json.loads(x)
        elif self._encoding == _Codec.AVRO:
            if self._schema == None:
                def schema_not_set(x):
                    raise Exception("Avro schema not set")
                basic_decode = schema_not_set
            else:
                basic_decode = lambda x: list(fastavro.reader(BytesIO(x), self._schema))
        elif self._encoding == _Codec.SOAP:
            basic_decode = soap_decode
        else:
            raise Exception("BERT Serialization not supported")
        
        if not self._recordsets:
            def decode(g):
                for x in g:
                    yield basic_decode(x)
        else:
            def decode(g):
                rr = [ basic_decode(x) for x in g ]
                if len(rr) == 0:
                    yield pd.DataFrame(rr)
                elif type(rr[0]) is list:
                    ## array records
                    yield np.matrix(rr)
                elif type(rr[0]) is not dict:
                    ## scalar records
                    yield pd.Series(rr)
                else:
                    ## proper records
                    yield pd.DataFrame(rr)
        
        self._decode = decode

    def prepare_output(self):
        self._decode = None
        if self._encoding == _Codec.NULL:
            basic_encode = lambda x: x if isinstance(x, str) else repr(x)
        elif self._encoding == _Codec.UTF8:
            basic_encode = lambda x: x.encode('utf-8')
        elif self._encoding == _Codec.JSON:
            def default(o):
                 if isinstance(o, np.generic): return o.item()
                 raise TypeError
            basic_encode = lambda x: json.dumps(x, default=default).encode()

        if not self._recordsets:
            def encode(g):
                for x in g:
                    yield basic_encode(x)
        else:
            recordset_marker = _Codec.MARKERS[self._encoding]
            def encode(g):
                for datum in g:
                    if isinstance(datum, np.matrix):
                        for x in datum.tolist():
                            yield basic_encode(x)
                    elif isinstance(datum, pd.Series):
                        for x in datum:
                            yield basic_encode(x)
                    else:
                        assert isinstance(datum, pd.DataFrame)
                        recordsOut = None
                        if datum.index.name is None:
                            recordsOut = datum.to_dict('records')
                        else:
                            dct = datum.to_dict('index')
                            recordsOut = [{x[0]: x[1]} for x in list(dct.items())]
                        for x in recordsOut:
                            yield basic_encode(x)
                    yield recordset_marker

        self._encode = encode

## EXPERIMENTAL
## EXPERIMENTAL
## EXPERIMENTAL

SOAP_NS = {
  "env": "http://schemas.xmlsoap.org/soap/envelope/",
  "xsd": "http://www.w3.org/1999/XMLSchema",
  "xsi": "http://www.w3.org/1999/XMLSchema-instance"
}

def soap_decode(s):
  env = ET.fromstring(s)
  op = env.find("env:Body", SOAP_NS)[0]
  att = "{%s}type" % SOAP_NS["xsi"]
  x = {}
  for arg in op:
    x[arg.tag] = soap_value(arg.text, arg.attrib[att])
  return x

def soap_value(s, type):
  if type == "xsd:string":
    return s
  if type == "xsd:int":
    return int(s)
  if type == "xsd:integer":
    return int(s)
  if type == "xsd:decimal":
    return float(s)
  if type == "xsd:float":
    return float(s)
  if type == "xsd:double":
    return float(s)
  else:
    raise Exception("type '%s' not supported" % type)

def soap_encode(x):
  env = ET.Element("env:Envelope")
  b = ET.SubElement(env, "env:Body")
  r = ET.SubElement(b, "return")
  for arg in x:
     e = ET.SubElement(r, arg)
     e.text = str(x[arg])
     e.attrib["xsi:type"] = soap_type(arg, x[arg])

  for name in SOAP_NS:
    env.attrib["xmlns:" + name] = SOAP_NS[name]

  return ET.tostring(env)

def soap_type(arg, v):
  if isinstance(v, str):
    return "xsd:string"
  if isinstance(v, int):
    return "xsd:integer"
  if isinstance(v, float):
    return "xsd:decimal"
  else:
    raise Exception("'%s' value not supported" % arg)

## EXPERIMENTAL
## EXPERIMENTAL
## EXPERIMENTAL

