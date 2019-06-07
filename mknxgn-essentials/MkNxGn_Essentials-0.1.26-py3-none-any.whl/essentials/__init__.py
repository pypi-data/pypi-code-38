dpr = True #Change to false to ignore module warnings

def dprint(prints):
    try:
        dpr
    except:
        print("dpr varible was deleted?")
        dpr = True
    if dpr:
        print(prints)

try:
    import json
except:
    dprint("JSON module error")

try:
    import datetime
except:
    dprint("datetime module error")

try:
    import random
except:
    dprint("random module")

try:
    from flask import request
except:
    dprint("flask module not found - pip install flask")
try:
    import requests
except:
    dprint("requests module not found - pip install requests")
try:
    import base64
except:
    dprint("base64 module error")

try:
    import collections
except:
    dprint("collections module error")

try:
    import tarfile
except:
    dprint("tarfile module error")

try:
    import os
except:
    dprint("os module error")

try:
    from PIL import Image
except:
    dprint("Pillow not found - pip install pillow")

try:
    import cv2
except:
    dprint("opencv not found - pip install opencv-python")

def cv2_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def pil_to_cv2(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def DecompressTar(file, dirs=False):
    tfile = tarfile.open(file, "r")
    if dirs == False:
        dirs = file.split(".")[0]
    os.makedirs(dirs, exist_ok=True)
    tfile.extractall(dirs)
    return dirs

def ShrinkLink(link):
    return json.loads(requests.get("https://mknxgn.pro/tools/LinkShrink?url=" + link).text)

def SortDictOfDict(Dict, key, reverseOrder=False):
    r = collections.OrderedDict(sorted(Dict.items(), key=lambda t:t[1][key], reverse=reverseOrder))
    data = {}
    for item in r:
        data[item] = Dict[item]
    return data

def DictToArgs(Dict):
    "Give a dictionary of keys and values to convert it to a url applyable string"
    args = []
    for item in Dict:
        args.append(item + "=" + Dict[item])
    args = "&".join(args)
    return "?" + args

def EncodeWithKey(key, string):
    enc = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(string[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def DecodeWithKey(key, string):
    dec = []
    enc = base64.urlsafe_b64decode(string).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def TimeStamp():
    """Get a timestamp for the current time"""
    return datetime.datetime.now().timestamp()

def Base64ToString(base64data):
    return base64.b64decode(base64data).decode('utf-8')

def StringToBase64(string):
    return base64.b64encode(string.encode('utf-8'))

def GetPublicIP():
    return json.loads(requests.get('https://api.ipify.org/?format=json').text)['ip']

def GetOrdinal(number):
    if type(number) != type(1):
        try:
            number = int(number)
        except:
            raise ValueError("This number is not an Int!")
    lastdigit = int(str(number)[len(str(number))-1])
    last2 = int(str(number)[len(str(number))-2:])
    if last2 > 10 and last2 < 13:
        return str(number) + "th"
    if lastdigit == 1:
        return str(number) + "st"
    if lastdigit == 2:
        return str(number) + "nd"
    if lastdigit == 3:
        return str(number) + "rd"
    return str(number) + "th"

def AssembleToken(length):
    """Create a randomly generated 'Token' with a-z 1-0 characters
    
    length - int: How long you want the Token to be"""

    TokenChars = ["a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F", "g", "G", "h", "H", "i", "I", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "o", "O",
                  "p", "P", "q", "Q", "r", "R", "s", "S", "t", "T", "u", "U", "v", "V", "w", "W", "x", "X", "y", "Y", "z", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    start = 0
    Token = ""
    while start < length:
        start += 1
        Random = random.randint(0, len(TokenChars) - 1)
        character = TokenChars[Random]
        Token = Token + character
    return Token

def CreateToken(length, AllTokens=[]):
    """Uses AssembleToken To create a token with nth characters (length), compares against a list of provided tokens(AllTokens)

    length - int: How long you want the Token to be
    AllTokens - List/Dict: Your List/Dict of tokens to create against"""

    Token = AssembleToken(length)
    while Token in AllTokens:
        Token = AssembleToken(length)
    return Token

def read_json(path, encrypt=False):
    """Read and returns JSON From a file

    path - String: Dir of the json file
    encrypt - Bool/String: If the file was encrypted with MkEncrypt, use the string that encrypted it."""

    if encrypt:
        return json.loads(DecodeWithKey(encrypt, read_file(path)))

    return json.loads(read_file(path))

def read_file(path, byte=False, encrypt=False):
    """Read and returns data From a file optionally gives bytes to read in bytes format

    path - String: Dir of the json file
    byte - Bool, False: Read as bytes, defaults to false."""
    if byte:
        file = open(path, "rb")
    else:
        file = open(path, "r")
    data = file.read()
    file.close()
    if encrypt:
        return DecodeWithKey(encrypt, data)
    return data

def write_file(path, data, append=False, byte=False, encrypt=False):
    """Writes data to a file optionally gives bytes to write in bytes format, includes append

    path - String: Dir of the file,
    append - Bool, False: Append to the current file,
    byte - Bool, False: Read as bytes, defaults to false."""
    otype = "w"
    if append:
        otype = "a"
    if byte:
        otype += "b"
    else:
        data = str(data)
    file = open(path, otype)
    if encrypt:
        data = EncodeWithKey(encrypt, data)
    file.write(data)
    file.close()
    return data

def write_json(path, data, pretty=True, encrypt=False):
    """Uses write_file, writes JSON data to a file. For use with Lists/Dicts

    path - String: Dir of the json file,
    data - Dict/List: What you'd like to be written to the file,
    pretty - Bool, True: Pretty Print the file for reading.
    encrypt - Bool/String, False: Will encrypt the file with the string given in place. If True, replaces pretty print with false."""

    if encrypt:
        return write_file(path, EncodeWithKey(encrypt, json.dumps(data)))

    if pretty:
        return write_file(path, json.dumps(data, indent=4, sort_keys=True))
    else:
        return write_file(path, json.dumps(data))

def StringFromTime(time=""):
    """Converts a datetime object to string for storage using a system type format

    time - Datetime Object, Current Time: the datetime object you'd like to convert. Defaults to the current date and time."""
    if time == "":
        time = datetime.datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S")

def StringToTime(time):
    """Converts a string, provided by essentials or in same format, to a time for storage use in a program

    time - String: the string you'd like to convert to a datetime object."""
    return datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

def ReadableTime(time=""):
    """Converts a datetime object to user readable time formatted string

    time - Datetime Object, Current Time: the datetime object you'd like to convert. Defaults to the current date and time."""
    if time == "":
        time = datetime.datetime.now()
    return time.strftime("%a %b %e %I:%M %p")

def DictData(request):
    return json.loads(request.data.decode("utf-8"))

def DictArgs(request):
    data = {}
    for item in request.args:
        data[item] = request.args.get(item)
    return data

def DictHeaders(request):
    data = {}
    for item in request.headers:
        data[item[0]] = request.headers.get(item[0])
    return data

def DictForm(request):
    data = {}
    for item in request.form:
        data[item] = request.form.get(item)
    return data

class ESRequestObject:
    """Creates a MkNxGn Essentails Request Object, for use with flask. Simplifies request data into dicts ({}). Pass your request like
    var requestdata = EsRequestObject(request)
    
    Use data like
    
    if 'Some_data' in requestdata.args:
        do_something
        
    Creates a Dict for the form, args, headers and data. Gives access to request address, json, and memetype."""

    def __init__(self, request):
        try:
            self.form = DictForm(request)
        except:
            self.form = None
        try:
            self.args = DictArgs(request)
        except:
            self.args = None
        try:
            self.headers = DictHeaders(request)
        except:
            self.headers = None
        try:
            self.data = DictData(request)
        except:
            self.data = None
        try:
            self.address = request.remote_addr
        except:
            self.address = None
        self.json = request.get_json(force=True, silent=True)
        try:
            self.meme = request.mimetype
        except:
            self.meme = None
    

class EsTimeObject:
    """Creates a MkNxGn Essentials Time Object, Use var = EsTimeObject(time) to create the time object. If time is left empty, it will use the current system time.
    time can be the MkNxGn preferred formatted string or a datetime object.

    On creation, you can use
    var.time: to get the datetime object associated with this object,
    var.string: to get the time in a MkNxGn perferred format,
    var.readable: to get the time in a user readable format"""

    def __init__(self, time=datetime.datetime.now()):
        try:
            self.string = StringFromTime(time)
            self.time = time
        except:
            self.time = StringToTime(time)
            self.string = time
        self.readable = ReadableTime(self.time)   

class EsFileObject:
    """Creates a MkNxGn Essentials File Object, Use var = EsFileObject(filedir) to create the file object. if filedir doesnt exisit, it will create it on save
    
    JSON Capabilities: On creation the object will try to create a json version if the file has json,
    You can access this at var.json,
    You can set the object json with var.setjson(json)
    Update a json key: var.json[key] = value
    You can access the object data at var.data
    You can set the objectt data with var.setdata(data)
    Save the EsFileObject with var.save(), by default this will try to save to the location it came from, unless dirs is set. if json is avalible, it will use json unless json=False
    """
    def __init__(self, dirs):
        self.dirs = dirs
        try:
            self.data = read_file(dirs)
        except:
            self.data = ""
        try:
            self.json = read_json(dirs)
        except:
            self.json = False

    def savedata(self, dirs=False):
        if (dirs == False):
            write_file(self.dirs, self.data)
        else:
            write_file(dirs, self.data)

    def savejson(self, dirs=False):
        if (dirs == False):
            write_json(self.dirs, self.json)
        else:
            if self.json == False:
                raise ValueError("Json Data is not set")
            write_json(dirs, self.json)

    def setdata(self, data):
        self.data = data
        try:
            self.json = json.loads(data)
        except:
            self.json = False

    def setjson(self, jsondata):
        try:
            self.data = json.dumps(jsondata, indent=4, sort_keys=True)
            self.json = jsondata
        except Exception as e:
            raise ValueError("Given 'JSON' is not JSON seriable-" + str(e))

    def save(self, dirs=False, asjson=True):
        if dirs == False:
            dirs = self.dirs
        if self.json != False and asjson:
            write_json(dirs, self.json)
        else:
            write_file(self.dirs, self.data)

