# Copyright 2013 Kevin Ormbrek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .utils import *
from suds.wsse import Security
from suds.wsse import Token
from suds.wsse import Timestamp
from suds.wsse import UsernameToken
from suds.sax.element import Element
from random import random
from hashlib import sha1
import base64
import re
from datetime import timedelta
import robot

from logging import getLogger
from suds import *
from suds.xsd import *
import time
import datetime as dt

TEXT_TYPE = 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText'
DIGEST_TYPE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest"
BASE64_ENC_TYPE = "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary"
WSSENS = \
    ('wsse',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
WSUNS = \
    ('wsu',
     'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')

class Date:
    """
    An XML date object.
    Supported formats:
        - YYYY-MM-DD
        - YYYY-MM-DD(z|Z)
        - YYYY-MM-DD+06:00
        - YYYY-MM-DD-06:00
    @ivar date: The object value.
    @type date: B{datetime}.I{date}
    """
    def __init__(self, date):
        """
        @param date: The value of the object.
        @type date: (date|str)
        @raise ValueError: When I{date} is invalid.
        """
        if isinstance(date, dt.date):
            self.date = date
            return
        if isinstance(date, str):
            self.date = self.__parse(date)
            return
        raise ValueError(type(date))
    
    def year(self):
        """
        Get the I{year} component.
        @return: The year.
        @rtype: int
        """
        return self.date.year
    
    def month(self):
        """
        Get the I{month} component.
        @return: The month.
        @rtype: int
        """
        return self.date.month
    
    def day(self):
        """
        Get the I{day} component.
        @return: The day.
        @rtype: int
        """
        return self.date.day
        
    def __parse(self, s):
        """
        Parse the string date.
        Supported formats:
            - YYYY-MM-DD
            - YYYY-MM-DD(z|Z)
            - YYYY-MM-DD+06:00
            - YYYY-MM-DD-06:00
        Although, the TZ is ignored because it's meaningless
        without the time, right?
        @param s: A date string.
        @type s: str
        @return: A date object.
        @rtype: I{date}
        """
        try:
            year, month, day = s[:10].split('-', 2)
            year = int(year)
            month = int(month)
            day = int(day)
            return dt.date(year, month, day)
        except:
            log.debug(s, exec_info=True)
            raise ValueError('Invalid format "%s"' % s)
        
    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        return self.date.isoformat()


class Time:
    """
    An XML time object.
    Supported formats:
        - HH:MI:SS
        - HH:MI:SS(z|Z)
        - HH:MI:SS.ms
        - HH:MI:SS.ms(z|Z)
        - HH:MI:SS(+|-)06:00
        - HH:MI:SS.ms(+|-)06:00
    @ivar tz: The timezone
    @type tz: L{Timezone}
    @ivar date: The object value.
    @type date: B{datetime}.I{time}
    """
    
    def __init__(self, time, adjusted=True):
        """
        @param time: The value of the object.
        @type time: (time|str)
        @param adjusted: Adjust for I{local} Timezone.
        @type adjusted: boolean
        @raise ValueError: When I{time} is invalid.
        """
        self.tz = Timezone()
        if isinstance(time, dt.time):
            self.time = time
            return
        if isinstance(time, str):
            self.time = self.__parse(time)
            if adjusted:
                self.__adjust()
            return
        raise ValueError(type(time))
    
    def hour(self):
        """
        Get the I{hour} component.
        @return: The hour.
        @rtype: int
        """
        return self.time.hour
    
    def minute(self):
        """
        Get the I{minute} component.
        @return: The minute.
        @rtype: int
        """
        return self.time.minute
    
    def second(self):
        """
        Get the I{seconds} component.
        @return: The seconds.
        @rtype: int
        """
        return self.time.second
    
    def microsecond(self):
        """
        Get the I{microsecond} component.
        @return: The microsecond.
        @rtype: int
        """
        return self.time.microsecond
    
    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if hasattr(self, 'offset'):
            today = dt.date.today()
            delta = self.tz.adjustment(self.offset)
            d = dt.datetime.combine(today, self.time)
            d = ( d + delta )
            self.time = d.time()
        
    def __parse(self, s):
        """
        Parse the string date.
        Patterns:
            - HH:MI:SS
            - HH:MI:SS(z|Z)
            - HH:MI:SS.ms
            - HH:MI:SS.ms(z|Z)
            - HH:MI:SS(+|-)06:00
            - HH:MI:SS.ms(+|-)06:00
        @param s: A time string.
        @type s: str
        @return: A time object.
        @rtype: B{datetime}.I{time}
        """
        try:
            offset = None
            part = Timezone.split(s)
            hour, minute, second = part[0].split(':', 2)
            hour = int(hour)
            minute = int(minute)
            second, ms = self.__second(second)
            if len(part) == 2:
                self.offset = self.__offset(part[1])
            if ms is None:
                return dt.time(hour, minute, second)
            else:
                return dt.time(hour, minute, second, ms)
        except:
            log.debug(s, exec_info=True)
            raise ValueError('Invalid format "%s"' % s)
        
    def __second(self, s):
        """
        Parse the seconds and microseconds.
        The microseconds are truncated to 999999 due to a restriction in
        the python datetime.datetime object.
        @param s: A string representation of the seconds.
        @type s: str
        @return: Tuple of (sec,ms)
        @rtype: tuple.
        """
        part = s.split('.')
        if len(part) > 1:
            return (int(part[0]), int(part[1][:6]))
        else:
            return (int(part[0]), None)
        
    def __offset(self, s):
        """
        Parse the TZ offset.
        @param s: A string representation of the TZ offset.
        @type s: str
        @return: The signed offset in hours.
        @rtype: str
        """
        if len(s) == len('-00:00'):
            return int(s[:3])
        if len(s) == 0:
            return self.tz.local
        if len(s) == 1:
            return 0
        raise Exception()

    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        time = self.time.isoformat()
        if self.tz.local:
            return '%s%+.2d:00' % (time, self.tz.local)
        else:
            return '%sZ' % time

class DateTime(Date,Time):
    """
    An XML time object.
    Supported formats:
        - YYYY-MM-DDB{T}HH:MI:SS
        - YYYY-MM-DDB{T}HH:MI:SS(z|Z)
        - YYYY-MM-DDB{T}HH:MI:SS.ms
        - YYYY-MM-DDB{T}HH:MI:SS.ms(z|Z)
        - YYYY-MM-DDB{T}HH:MI:SS(+|-)06:00
        - YYYY-MM-DDB{T}HH:MI:SS.ms(+|-)06:00
    @ivar datetime: The object value.
    @type datetime: B{datetime}.I{datedate}
    """
    def __init__(self, date):
        """
        @param date: The value of the object.
        @type date: (datetime|str)
        @raise ValueError: When I{tm} is invalid.
        """
        if isinstance(date, dt.datetime):
            Date.__init__(self, date.date())
            Time.__init__(self, date.time())
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            return
        if isinstance(date, str):
            part = date.split('T')
            Date.__init__(self, part[0])
            Time.__init__(self, part[1], 0)
            self.datetime = \
                dt.datetime.combine(self.date, self.time)
            self.__adjust()
            return
        raise ValueError(type(date))
    
    def __adjust(self):
        """
        Adjust for TZ offset.
        """
        if not hasattr(self, 'offset'):
            return
        delta = self.tz.adjustment(self.offset)
        try:
            d = ( self.datetime + delta )
            self.datetime = d
            self.date = d.date()
            self.time = d.time()
        except OverflowError:
            log.warn('"%s" caused overflow, not-adjusted', self.datetime)

    def __str__(self):
        return unicode(self)
    
    def __unicode__(self):
        s = []
        s.append(Date.__unicode__(self))
        s.append(Time.__unicode__(self))
        return 'T'.join(s)

class UTC(DateTime):
    """
    Represents current UTC time.
    """
    
    def __init__(self, date=None):
        if date is None:
            date = dt.datetime.utcnow()
        DateTime.__init__(self, date)
        self.tz.local = 0
		
class AutoTimestamp(Timestamp):

    def __init__(self, validity=None):
        Token.__init__(self)
        self.validity = validity

    def xml(self):
        self.created = Token.utc()
        root = Element("Timestamp", ns=WSUNS)
        created = Element('Created', ns=WSUNS)
        created.setText(self._trim_to_ms(str(UTC(self.created))))
        root.append(created)
        if self.validity is not None:
            self.expires = self.created + timedelta(seconds=self.validity)
            expires = Element('Expires', ns=WSUNS)
            expires.setText(self._trim_to_ms(str(UTC(self.expires))))
            root.append(expires)
        return root

    def _trim_to_ms(self, datetime):
        return re.sub(r'(?<=\.\d{3})\d+', '', datetime)


class AutoUsernameToken(UsernameToken):

    def __init__(self, username=None, password=None, setcreated=False,
                 setnonce=False, digest=False):
        UsernameToken.__init__(self, username, password)
        self.autosetcreated = setcreated
        self.autosetnonce = setnonce
        self.digest = digest

    def setnonce(self, text=None):
        if text is None:
            hash = sha1()
            hash.update(str(random()))
            hash.update(str(UTC()))
            self.nonce = hash.hexdigest()
        else:
            self.nonce = text

    def xml(self):
        if self.digest and self.password is None:
            raise RuntimeError("Cannot generate password digest without the password.")
        if self.autosetnonce:
            self.setnonce()
        if self.autosetcreated:
            self.setcreated()
        root = Element('UsernameToken', ns=WSSENS)
        u = Element('Username', ns=WSSENS)
        u.setText(self.username)
        root.append(u)
        if self.password is not None:
            password = self.password
            if self.digest:
                password = self.get_digest()
            p = Element('Password', ns=WSSENS)
            p.setText(password)
            p.set('Type', DIGEST_TYPE if self.digest else TEXT_TYPE)
            root.append(p)
        if self.nonce is not None:
            n = Element('Nonce', ns=WSSENS)
            n.setText(base64.encodestring(self.nonce)[:-1])
            n.set('EncodingType', BASE64_ENC_TYPE)
            root.append(n)
        if self.created:
            c = Element('Created', ns=WSUNS)
            c.setText(str(UTC(self.created)))
            root.append(c)
        return root

    def get_digest(self):
        nonce = str(self.nonce) if self.nonce else ""
        created = str(UTC(self.created)) if self.created else ""
        password = str(self.password)
        message = nonce + created + password
        return base64.encodestring(sha1(message).digest())[:-1]


class _WsseKeywords(object):

    def apply_security_timestamp(self, duration=None):
        """Applies a Timestamp element to future requests valid for the given `duration`.

        The SOAP header will contain a Timestamp element as specified in the
        WS-Security extension. The Created and Expires values are updated
        every time a request is made. If `duration` is None, the Expires
        element will be absent.

        `duration` must be given in Robot Framework's time format (e.g.
        '1 minute', '2 min 3 s', '4.5').

        Example:
        | Apply Security Timestamp | 5 min |
        """
        if duration is not None:
            duration = robot.utils.timestr_to_secs(duration)
        wsse = self._get_wsse()
        wsse.tokens = [x for x in wsse.tokens if not isinstance(x, Timestamp)]
        wsse.tokens.insert(0, AutoTimestamp(duration))
        self._client().set_options(wsse=wsse)

    def apply_username_token(self, username, password=None, setcreated=False,
                             setnonce=False, digest=False):
        """Applies a UsernameToken element to future requests.

        The SOAP header will contain a UsernameToken element as specified in
        Username Token Profile 1.1 that complies with Basic Security Profile
        1.1. The Created and Nonce values, if enabled, are generated
        automatically and updated every time a request is made. If `digest` is
        True, a digest derived from the password is sent.

        Example:
        | Apply Username Token | ying | myPa$$word |
        """
        setcreated = to_bool(setcreated)
        setnonce = to_bool(setnonce)
        digest = to_bool(digest)
        if digest and password is None:
            raise RuntimeError("Password is required when digest is True.")
        token = AutoUsernameToken(username, password, setcreated, setnonce,
                                  digest)
        wsse = self._get_wsse()
        wsse.tokens = [x for x in wsse.tokens if not isinstance(x, UsernameToken)]
        wsse.tokens.append(token)
        self._client().set_options(wsse=wsse)

    # private

    def _get_wsse(self, create=True):
        wsse = self._client().options.wsse
        if wsse is None and create:
            wsse = Security()
            wsse.mustUnderstand = '1'
        return wsse
