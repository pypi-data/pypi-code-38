import sys
import requests
import simplejson
from PIL import Image as PILImage
import base64
if sys.version_info[0] >= 3:
    from io import BytesIO
else:
    import cStringIO


def send_requests(cmd, jsdata, argdata, address):
    """cmd is a string specifying what kind of action
    we want the server to do.
    jsdata is some jsonable metadata associated with the cmd.
    argdata is data that could have images or files or anything in it.
    We offer encoding and decoding for a range of possibilities.
    """
    req = {}
    req['cmd'] = cmd
    req['jsdata'] = jsdata
    req['kind'], req['data'] = encode_argdata(argdata)

    try:
        return requests.post(address, json=req)
    except requests.exceptions.ConnectionError as e:
        raise type(e)(
            str(e) + ' Unable to connect to address {}'.format(address))


def receive_tornado(req):
    req = simplejson.loads(req.body)
    if req['cmd'] == 'get_info':
        argdata = {}
    elif req['cmd'] == 'get_method':
        argdata = parse_argdata(req['kind'], req['data'])
    return req['cmd'], req['jsdata'], argdata


def send_tornado(jsdata, argdata):
    res = {}
    res['jsdata'] = jsdata
    res['kind'], res['data'] = encode_argdata(argdata)

    return simplejson.dumps(res)


def receive_requests(res):
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise type(e)(str(e) + ' "{}"'.format(res.content))
    res = simplejson.loads(res.content)
    argdata = parse_argdata(res['kind'], res['data'])
    return res['jsdata'], argdata


def encode_argdata(argdata):
    if isinstance(argdata, tuple):
        data = []
        for val in argdata:
            data.append(encode_arg(val))
        kind = 'tuple'
    elif isinstance(argdata, dict):
        data = {}
        for k in argdata:
            data[k] = encode_arg(argdata[k])
        kind = 'dict'
    else:
        kind = 'arg'
        data = encode_arg(argdata)
    return kind, data


def parse_argdata(kind, data):
    if kind == 'tuple':
        argdata = tuple((parse_arg(arg) for arg in data))
    elif kind == 'dict':
        argdata = {}
        for k in data:
            argdata[k] = parse_arg(data[k])
    elif kind == 'arg':
        argdata = parse_arg(data)
    return argdata


def encode_arg(arg):
    try:
        simplejson.dumps(arg)
        return {'arg': arg, 'type': 'json'}
    except TypeError:
        if isinstance(arg, PILImage.Image):
            return {'arg': pil_to_b64(arg), 'type': 'pilimage'}


def parse_arg(arg):
    if arg['type'] == 'json':
        return arg['arg']
    elif arg['type'] == 'pilimage':
        return b64_to_pil(arg['arg'])


def pil_to_b64(img):
    if sys.version_info[0] >= 3:
        buffer = BytesIO()
    else:
        buffer = cStringIO.StringIO()
    img.save(buffer, 'PNG')
    return base64.b64encode(buffer.getvalue())


def b64_to_pil(b64):
    img = base64.b64decode(b64)
    if sys.version_info[0] >= 3:
        return PILImage.open(BytesIO(img)).convert('RGB')
    else:
        return PILImage.open(cStringIO.StringIO(img)).convert('RGB')
