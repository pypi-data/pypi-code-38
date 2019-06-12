#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""class for caching objects with timed expiry"""

# Copyright 2002, 2003 St James Software

import datetime
import time
import threading
import logging

# a global variable which makes all time caches behave as though they are empty, and remember no new data
GLOBAL_CACHE_DISABLED = False
# a global variable which makes all time caches that declare themselves as LOCAL_CACHE to behave as though they are empty, and remember no new data
LOCAL_CACHE_DISABLED = False
# a global variable which makes all time caches that declare themselves as LOCAL_CACHE have a maximum time period - this needs to be a datetime.timedelta
LOCAL_CACHE_TIMELIMIT = None

class timecache(dict):
  """caches objects, remembers time, and dumps when neccessary..."""
  # by default time caches are not LOCAL_CACHE. If this is set to True on a class or object, it will obey (LOCAL_CACHE_DISABLED or GLOBAL_CACHE_DISABLED) - otherwise, just GLOBAL_CACHE_DISABLED
  _LOCAL_CACHE = False
  def __init__(self, expiryperiod, local=False):
    """constructs a timecache dictionary with an expiryperiod given in seconds..."""
    dict.__init__(self)
    self.expiryperiod = datetime.timedelta(seconds=expiryperiod)
    self.LOCAL_CACHE = local
    self.last_purged = time.time()
    self.purge_period = min(expiryperiod / 2.0,120)
    self.purge_lock = threading.RLock()

  def _get_local_cache(self):
    return self._LOCAL_CACHE

  def _set_local_cache(self, local_cache):
    self._LOCAL_CACHE = local_cache

  LOCAL_CACHE = property(_get_local_cache, _set_local_cache)

  def is_disabled(self):
    """Returns whether this cache is currently disabled"""
    return GLOBAL_CACHE_DISABLED or (self._LOCAL_CACHE and LOCAL_CACHE_DISABLED)

  def expired(self, timestamp):
    """checks if self.timestamp is older than self.expiryperiod"""
    return timestamp < self.gettimestamp() - ((self._LOCAL_CACHE and LOCAL_CACHE_TIMELIMIT) or self.expiryperiod)

  def cleanup_key(self, key, value):
    """Performs any cleanup needed when a key is expired (for derived classes)"""
    pass

  def expire(self, key):
    """expires the key, removing the associated item. Calls self.cleanup_key(key, value) after removal"""
    timestamp, value = self.pop(key, (None, None))
    if timestamp:
        self.cleanup_key(key, value)

  def gettimestamp(self):
    """returns a new timestamp for the current time..."""
    return datetime.datetime.now()

  def purge(self):
    """removes all items that are older then self.expiryperiod"""
    with self.purge_lock:
        n = time.time()
        if not self.last_purged + self.purge_period < n:
            return
        self.last_purged = n
    try:
        keystodelete = []
        for key, (timestamp, value) in dict.items(self):
          if self.expired(timestamp):
            keystodelete.append(key)
        for key in keystodelete:
          self.expire(key)
    except RuntimeError:
        # our size changed during iteration, but we don't mind - we'll just purge next time
        logging.info("TimeCache purge interrupted")

  def __contains__(self, key):
    """in operator"""
    if self.is_disabled():
      return 0
    if dict.__contains__(self, key):
      timestamp, value = dict.__getitem__(self, key)
      if self.expired(timestamp):
        self.expire(key)
        # this allows expire to actually reset the value
        return dict.__contains__(self, key)
      return 1
    return 0

  def __getitem__(self, key):
    """[] access of items"""
    if self.is_disabled():
      raise KeyError(key)
    timestamp, value = dict.__getitem__(self, key)
    if self.expired(timestamp):
      self.expire(key)
      # this allows expire to actually reset the value
      if dict.__contains__(self, key):
        return dict.__getitem__(self, key)[1]
      raise KeyError(key)
    return value

  def __iter__(self):
    """iterator access of items"""
    if self.is_disabled():
      return dict.__iter__({})
    self.purge()
    return dict.__iter__(self)

  def __repr__(self):
    """x.__repr__() <==> repr(x)"""
    if self.is_disabled():
      return "<GLOBAL_CACHE_DISABLED>"
    self.purge()
    return repr(dict(list(self.items())))

  def __setitem__(self, key, value):
    """[] setting of items"""
    if self.is_disabled():
      return
    self.purge()
    timestamp = self.gettimestamp()
    dict.__setitem__(self, key, (timestamp, value))

  def has_key(self, key):
    """check if key is present"""
    if self.is_disabled():
      return False
    return self.__contains__(key)

  def get(self, key, default=None):
    """D.get(k[,d]) -> D[k] if D.has_key(k), else d.  d defaults to None."""
    if self.is_disabled():
      return default
    timestamp, value = dict.get(self, key, (None, default))
    if timestamp is None:
      return value
    elif self.expired(timestamp):
      self.expire(key)
      # this allows expire to actually reset the value
      return dict.get(self, key, (None, default))[1]
    return value

  def set(self, key, value):
      self[key] = value

  def clear(self):
      """ D.clear() -> None.  Remove all items from D. """
      with self.purge_lock:
          dict.clear(self)

  def items(self):
    """D.items() -> list of D's (key, value) pairs, as 2-tuples"""
    if self.is_disabled():
      return []
    self.purge()
    return [(key, value) for (key, (timestamp, value)) in dict.items(self)]

  def iteritems(self):
    """D.iteritems() -> an iterator over the (key, value) items of D"""
    if not GLOBAL_CACHE_DISABLED:
      self.purge()
      for key, (timestamp, value) in dict.items(self):
        yield (key, value)

  def iterkeys(self):
    """D.iterkeys() -> an iterator over the keys of D"""
    if self.is_disabled():
      return dict.keys({})
    self.purge()
    return dict.keys(self)

  def itervalues(self):
    """D.itervalues() -> an iterator over the values of D"""
    if not GLOBAL_CACHE_DISABLED:
      self.purge()
      for timestamp, value in dict.values(self):
        yield value

  def keys(self):
    """D.keys() -> list of D's keys"""
    if self.is_disabled():
      return []
    self.purge()
    return dict.keys(self)

  def values(self):
    """D.values() -> list of D's values"""
    if self.is_disabled():
      return []
    self.purge()
    return [value for (timestamp, value) in dict.values(self)]

  def popitem(self):
    """D.popitem() -> (k, v), remove and return some (key, value) pair as a
    2-tuple; but raise KeyError if D is empty"""
    if self.is_disabled():
      raise KeyError("popitem(): cache is disabled")
    self.purge()
    key, (timestamp, value) = dict.popitem(self)
    return (key, value)

  def setdefault(self, key, failobj=None):
    """D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D"""
    if self.is_disabled():
      return failobj
    self.purge()
    newtimestamp = self.gettimestamp()
    oldtimestamp, value = dict.setdefault(self, key, (newtimestamp, failobj))
    if self.expired(oldtimestamp):
      dict.__setitem__(self, key, (newtimestamp, failobj))
      return failobj
    return value

  def update(self, updatedict):
    """D.update(E) -> None.  Update D from E: for k in E.keys(): D[k] = E[k]"""
    if self.is_disabled():
      return
    self.purge()
    for key in list(updatedict.keys()):
      self[key] = updatedict[key]

  def size(self):
    return len(self)

