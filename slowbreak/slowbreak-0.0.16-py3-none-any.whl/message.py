"""FIX messages, as we understand them in slowbreak"""

import itertools
from .comm import MockSocket
from .constants import Tag, MsgType
import ssl
import logging
import socket
import errno
import select
import six
import decimal
import datetime

LOG = logging.getLogger(__name__)
TAG2NAME = { v: k for k,v in six.iteritems(Tag.__dict__) if "_" != k[0] }
MSGTYPE2NAME = { v: k for k,v in six.iteritems(MsgType.__dict__) if "_" != k[0] }

class AllInclusiveType(object):
    "Returns True to o in self for all o"
    def __contains__(self, _):
        return True
        
AllInclusive = AllInclusiveType()

def from_bool(b):
    "Generate bool value to be included in fix message"
    return b'Y' if b else b'N'

def to_bool(v):
    "Convert bool value included in fix message"
    return True if v == b'Y' else False

def from_int(i):
    "Generate int value to be included in fix message"
    return b'%d' % i

def to_int(v):
    "Convert int value included in fix message"
    return int(v)

def from_decimal(d):
    "Generate decimal.Decimal value to be included in fix message"
    return from_str(str(d))

def to_decimal(v):
    "Convert decimal.Decimal value included in fix message"
    return decimal.Decimal(to_str(v))

def from_str(s, encoding='ascii'):
    """\
Generate string (unicode) value to be included in fix message

:param s: string
:param encoding: encoding to be used (default ascii)
:returns: bytes
"""
    return s.encode(encoding=encoding)

def to_str(v, encoding='ascii'):
    """\
Convert string (unicode) value included in fix message

:param v: bytes
:param encoding: encoding to be used (default ascii)
:returns: str
"""
    return v.decode(encoding=encoding)

def timestamp(dt=None):
    """\
Generate fix timestamp for datetime

:param dt: Datetime object (utcnow if None)
:returns: bytes
"""
    if dt is None:
        dt = datetime.datetime.utcnow()
    return from_str( dt.strftime('%Y%m%d-%H:%M:%S.%f')[:-3] )
        

class InvalidPart(Exception): pass

class InvalidMessage(Exception):
    def __init__(self, parts, cause):
        self.parts = parts
        self.cause = cause
        super(InvalidMessage, self).__init__("Invalid message %r. Cause: %s" % (parts, cause))

class InvalidChecksum(InvalidMessage):
    def __init__(self, checksum, parts):
        self.checksum = checksum
        super(InvalidChecksum, self).__init__(parts = parts, cause="Invalid checksum. Expected %s" % checksum)

class MultipleTags(Exception):
    def __init__(self, fix_message, tag_number):
        self.fix_message = fix_message
        self.tag_number = tag_number
        
        super(MultipleTags, self).__init__('Tag %s repeated in %r' % (tag_number, fix_message))
        
class TagNotFound(Exception):
    def __init__(self, fix_message, tag_number):
        self.fix_message = fix_message
        self.tag_number = tag_number
        
        super(TagNotFound, self).__init__('Tag %s not found in %r' % (tag_number, fix_message))
        
class InvalidGroup(Exception):
    def __init__(self, group, first_tag, other_tags):
        self.group = group
        self.first_tag = first_tag
        self.other_tags = other_tags
        
        super(InvalidGroup, self).__init__('Invalid group %r with first tag %s and other tags %r' % (group, first_tag, other_tags))
        
class NotEnoughGroups(Exception):
    def __init__(self, fix_message, count_tag, first_tag, other_tags):
        self.fix_message = fix_message
        self.count_tag = count_tag
        self.first_tag = first_tag
        self.other_tags = other_tags
        
        super(NotEnoughGroups, self).__init__('Not enough groups for count tag %s first tag %s other_tags %r in %r' (count_tag, first_tag, other_tags, fix_message ))

NO_DEFAULT = object()
        
class Message(object):
    
    """\
FIX Message.

We think of FIX messages as lists of (tag, value) pairs, where tag is a number and value is a binary string.
"""
    
    @classmethod
    def from_socket(cls, socket, begin_string=b'FIXT.1.1'):
        """\
Read a FIX message from a socket

:param socket: socket to be read
:returns: A Message object
"""
        for ps in cls._parts(socket):
            if ps is None: # timeout
                yield None
                continue
            parts = map(lambda p: p.split(b"=",1), ps)
            parts = [(to_int(n), v[:-1]) for n,v in parts]
            
            if len(parts) < 3:
                raise InvalidMessage(parts=parts, cause="Not enough parts. At least fields 8,9 and 10 must be present")
            
            if (8, begin_string) != parts[0]:
                raise InvalidMessage(parts=parts, cause="Invalid BeginString")
            
            if 9 != parts[1][0]:
                raise InvalidMessage(parts=parts, cause="No BodyLength")
            
            declared_body_length = to_int(parts[1][1])
            real_body_length = sum(len(p) for p in ps[2:-1])
            
            if declared_body_length != real_body_length:
                raise InvalidMessage(parts=parts, cause="Declared length: %s. Real length: %s" % (declared_body_length, real_body_length))
            
            if parts[-1][0] != 10:
                raise InvalidMessage(parts = parts, cause="Does not end with 10 group")
            
            checksum = cls._checksum(*ps[:-1])
            
            if checksum != to_int(parts[-1][1]):
                raise InvalidChecksum(parts=parts, checksum=checksum)
            
            m = cls(*parts[2:-1])
            yield m 
    
    @classmethod
    def from_bytes(cls, s, begin_string=b'FIXT.1.1'):
        """\
Construct a FIX message from a binary string

:param s: bytes to be read (str in python2, bytes in python3)
:returns: A Message object
"""

        return cls.from_socket(MockSocket(s), begin_string=begin_string)
    
    def __init__(self, *args):
        """\
Constructor.

:param args: List of pairs (tag, value)
"""        
        for p in args:
            self.check_part(p)
        self.parts = list(args)
        
    def __add__(self, other):
        """\
Concatenate 2 FIX messages

:returns: A new fix message, which contains the concatenation of the 2 messages
"""
        return Message( *itertools.chain(self, other) )
    
    def __eq__(self, other):
        return self.parts == other.parts
        
    def __iter__(self):
        return iter(self.parts)
    
    def __getitem__(self, key):
        """
Return the (tag, value) in key position

:param key: position to be extracted.
:returns: (key, value) pair if single position. New message object if a range is given.
"""
        item = self.parts.__getitem__(key)
        return self.__class__(*item) if isinstance(item, list) else item

    def __len__(self):
        """\
:returns: Number of tags in message
"""
        return len(self.parts)
    
    def __repr__(self):
        """\
:returns: Object representation
"""
        def repr_part(part):
            tag = part[0]
            value = b'<removed password>' if tag == Tag.Password else part[1]
            return "(%d, %s)" % (tag, repr(value)) 
        
        # * to handle messages with more than 256 parts
        return "Message(*(%s))" % ",".join( map(repr_part, self.parts))
    
    def pprint(self): # Podria usar __str__
        """\
:returns: Human-readable representation of this message.
"""
        
        rv = ''    
        for tag, value in self.parts:
            tag_legend = TAG2NAME.get(tag, "Unknown") + " ("  + str(tag) + ")"
            if Tag.MsgType == tag:
                value_legend = MSGTYPE2NAME.get(value, "Unknown") + " (" + value.decode('ascii') + ")"
            elif Tag.Password == tag:
                value_legend = '<removed password>'
            else:
                value_legend = value.decode('iso8859-1')
            rv += u'{}: {}\n'.format(tag_legend, value_legend)         
        
        return rv

    def append(self, n, v):
        """\
Append tag and value to message.

:param n: tag number
:param v: value
"""
        return self.parts.append((n,v))
    
    def to_buf(self, begin_string=b"FIXT.1.1"):
        """\
Write message to a buffer.
:param begin_string: String used in field 8 to signal the beginning of the message 

:returns: binary representation of the message.
"""
        body = b"".join( b"%d=%s\x01" % (n,v) for n,v in self.parts )
        header = b"8=" + begin_string + b"\x019=%d\x01" % len(body)
        trailer = b"10=%03d\x01" % self._checksum(header + body)
        
        return header + body + trailer
    
    def get_field(self, n, default=NO_DEFAULT):
        """\
Get field value indexed by tag number.

:param n: Tag number.
:param default: Value to be returned if tag is not found.
:returns: The value of the tag in the message.
:raises TagNotFound: if not found and default not set.
:raises MultipleTags: if the tag appears more than once in the message.
""" 
        parts = [ v for k,v in self if k == n ]
        
        if 0 == len(parts):
            if default is NO_DEFAULT:
                raise TagNotFound(self, n)
            else:
                return default
        
        if 1 < len(parts):
            raise MultipleTags(self, n)
        
        return parts[0] 
    
    @classmethod
    def group(cls, counting_tag, *args):
        """\
Create a FIX group

:param counting_tag: number of the tag used to count the number of parts in the group
:param args: each group part, as a Message object.
:returns: a new Message object starting with the (counting_tag, count) pair and then all the parts of the message.
"""
        rv = cls((counting_tag, six.text_type(len(args)).encode('ascii')))
        for g in args:
            rv += g
        
        return rv
    
    def get_groups(self, count_tag, first_tag, other_tags):
        """\
Extract a group from a message

:param count_tag: Tag that shows the number of groups
:param first_tag: First tag number for each group
:param other_tag: List of other tag numbers in the group
:returns: List of fix messages, one for each group
:raises TagNotFound: if the count_tag is not found
:raises MultipleTags: if the count_tag is found several times
:raises NotEnoughGroups: if cannot extract the expected number of groups as indicated with the count_tag
:raises InvalidGroup: if a non-authorized tag is found inside a group
""" 
        
        count_tags = [(pos, to_int(part[1])) for pos , part in list(enumerate(self)) if part[0] == count_tag]
        
        if 0 == len(count_tags):
            raise TagNotFound(self, count_tag)
        
        if 1 < len(count_tags):
            raise MultipleTags(self, count_tag)
        
        pos, count = count_tags[0] 
        
        if count == 0:
            return []

        pos += 1 # Advance to avoid count field
        if pos >= len(self.parts):
            raise NotEnoughGroups(fix_message=self, count_tag=count_tag, first_tag=first_tag, other_tags=other_tags)
        
        if first_tag != self[pos][0]:
            raise InvalidGroup(group=self[pos:pos+1], first_tag=first_tag, other_tags=other_tags)
        
        starts = [pos]
        
        pos += 1
         
        while len(starts) < count :
            if pos >= len(self):
                raise NotEnoughGroups(fix_message=self, count_tag=count_tag, first_tag=first_tag, other_tags=other_tags)
            if self[pos][0] == first_tag:
                starts.append(pos)
            elif not self[pos][0] in other_tags:
                raise InvalidGroup(group=self[starts[-1]: pos + 1], first_tag=first_tag, other_tags = other_tags) 
            
            pos += 1
            
        last_end = pos
        
        while last_end < len(self) and self[last_end][0] in other_tags:
            last_end += 1
            
        ends = starts[1:] + [last_end]
        
        return [self[s:e] for s,e in zip(starts, ends)]
            
         
            
    @staticmethod
    def _parts(s):
        
        def fetch_next_chunk():
            while True:
                try:
                    return s.read()
                except ssl.SSLWantReadError as e:
                    # Somehow our blocking socket gets non-blocking some times!!!!
                    select.select([s], [], [], 0.1)
                except socket.error as e:
                    if errno.EWOULDBLOCK == e.errno:
                        # Somehow our blocking socket gets non-blocking some times!!!!
                        select.select([s], [], [], 0.1)  
                    else:
                        raise
                         
        """Iterate through messages, yields a list of strings (one for each part) as read from the socket"""
        buf = b""
        current =  []
        while True:
            while True:
                pos = buf.find(b'\x01')
                if -1 == pos: 
                    break
                part = buf[:pos+1]
                if not b"=" in part:
                    raise InvalidPart(part)
                current.append( part )
                n = part.split(b"=",1)[0]
                if b"10" == n: # checksum
                    yield current
                    current = []
                     
                buf = buf[pos+1:]
            
            try: 
                next_chunk = fetch_next_chunk()
                if b"" == next_chunk:
                    return
                
            except ssl.SSLError as e:
                if 'timed out' in str(e):
                    LOG.info("Time out reading FIX messages")
                    yield None
                    next_chunk = b""
                else:
                    raise e
                
            buf += next_chunk
            
    @staticmethod
    def check_part(part):
        if not isinstance(part, tuple):
            raise InvalidPart(repr(part) + " is not a tuple")
        
        if 2 != len(part):
            raise InvalidPart(repr(part) + " has len different than 2")
        
        if int != type(part[0]):
            raise InvalidPart(repr(part) + " tag not an integer")
        
        if six.binary_type != type(part[1]):
            raise InvalidPart(repr(part) + " value not a binary string")
        
        if b'\x01' in part[1]:
            raise InvalidPart(repr(part) + " value has a 1 (separator value) in it")

    @staticmethod
    def _checksum(*args):
        return sum( sum(c for c in six.iterbytes(buf)) for buf in args ) % 256
