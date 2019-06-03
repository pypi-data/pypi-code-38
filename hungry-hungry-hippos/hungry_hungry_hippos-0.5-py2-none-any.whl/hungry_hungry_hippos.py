# -*- coding: utf-8 -*-
#!/usr/bin/python

import redis
import time
import threading
import signal
import sys, logging

class HungryHungryHippos(object):

    def __init__(self, host='redis', port=6379, db=0, logger=None, namespace='default', redis_client=None):
        
        if redis_client == None:
            self.r = redis.StrictRedis(host=host, port=port, db=db)
        else:
            self.r = redis_client
            
        self.namespace = namespace
        
        if logger == None:
            self.logger = logging.getLogger('hungry_hungry_hippos')
            self.logger.setLevel(logging.DEBUG)

            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(logging.ERROR)
            #ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        else:
            self.logger = logger
        
    def log(self, str):
        self.logger.info(str)    
    
    def _getkeys(self, k):
        lock_key = u'{}:{}:{}'.format(self.namespace, k, 'lock')
        keepalive_key = u'{}:{}:{}'.format(self.namespace, k, 'keepalive')
        freed_lock = u'{}:{}:{}'.format(self.namespace, k, 'freed_lock')
        
        return (lock_key, keepalive_key, freed_lock)

    def release_lock(self, v):
        # self.log(u'Releasing lock {}'.format(v)
        (lock_key, keepalive_key, freed_lock) = self._getkeys(v)

        pipe = self.r.pipeline()
        pipe.expire(lock_key, '0')
        pipe.expire(keepalive_key, '0')
        pipe.rpush(freed_lock, "DONE")  # freed_lock
        pipe.expire(freed_lock, 10)  # freed_lock expires in  10 seconds
        pipe.execute()
        
    def wait_for_lock(self, v, timeout=None):
        (lock_key, keepalive_key, freed_lock) = self._getkeys(v)
        
        pipe = self.r.pipeline()
        pipe.llen(lock_key)         # len of lock
        pipe.llen(keepalive_key)    # len of keepalive_key
        pipe.llen(freed_lock)       # len of freed_lock
        result = pipe.execute()
        
        if result[0] == 0:
            # lock does not exist, assume freed
            return
        
        if result[1] == 0:
            # keepalive_key no longer exists, assume freed
            return
        
        if result[2] > 0:
            # lock as been freed
            return
        
        # if we get this far then the lock exists and has not yet been freed
        # we use the brpoplpush to pop and repush to the same list so other
        # clients doing wait_for_lock will also get it
        if timeout > 0:
            # wait here with timeout
            self.r.brpoplpush(freed_lock, freed_lock, timeout)
        else:
            # wait here indefinitely
            self.r.brpoplpush(freed_lock, freed_lock)
            
        # lock ahs been freed
        
    def lock_keepalive(self, v, lock_uuid, sleep=10):
        self.log(u'Starting lock renewal thread for {} with uuid={}'.format(v, lock_uuid))
        (lock_key, keepalive_key, freed_lock) = self._getkeys(v)
        
        pipe = self.r.pipeline()
        pipe.llen(lock_key)  # len of lock
        pipe.lrem(keepalive_key, 0, lock_uuid)  # remove my unique key from lock to get the len
        pipe.rpush(keepalive_key, lock_uuid)  # put it back
        result = pipe.execute()
        
        # self.log(result
        
        while True:
            if result[0] == 0:
                # lock no longer exists
                self.log(u'lock {} disappeared'.format(lock_key))
                return
            
            if result[1] == 0:
                # my keepalive_key no longer exists
                self.log(u'keepalive_key {} disappeared'.format(keepalive_key))
                return
            
            # self.log(u'renewing lock {} to expire in {} seconds'.format(keepalive_key, sleep*2)
            # set it to expire further in the future
            self.r.expire(keepalive_key, sleep * 2)   
            time.sleep(sleep)

    def _get_lock_uuid(self):
        return "{}".format(float(time.time()))
        
    @property
    def thread(self):
        return self.t

    def blpop(self, keys=[]):
        (k, v) = self.r.blpop(keys, 0)
        self.log("got a {} {}".format(k,v))
        return (k, v)
    
    def blpop_lock(self, keys=[]):
        (k, v) = self.r.blpop(keys, 0)

        (lock_key, keepalive_key, freed_lock) = self._getkeys(v)
        
        self.log(u"got a {}".format(v))
        
        lock_uuid = self._get_lock_uuid()
        
        self.log("v={} lock_uuid={}".format(v, lock_uuid))
        
        pipe = self.r.pipeline()
        pipe.rpush(lock_key, lock_uuid)
        pipe.rpush(keepalive_key, lock_uuid)
        pipe.expire(keepalive_key, 3)  # queue for long expiry right away
        result = pipe.execute()
        
        # self.log(result
        
        if result[0] == 1:
            # lock queue only has one item in it (mine!)
            # I have the lock
            self.log("Got lock {}".format(lock_key))
            self.t = threading.Thread(target=self.lock_keepalive, args=(v, lock_uuid,))
            self.t.start()
    
            lock_success = True
            
            self.r.expire(freed_lock, '0') # expire out any preexisting freed locks NOW
        else :
            lock_success = False

            if result[1] == 1:
                # no previous keepalive lock, looks like I got a stale lock
                self.release_lock(v)
                
                # put it back on the shelf for the next person
                self.r.lpush(k, v)
                # I don't have the lock
                self.log("Found a stale lock {} putting it back in the front of the line".format(v))
                
            else:
                # I don't have the lock
                self.log("{} already locked".format(lock_key))
            
        return (lock_success, k, v)


class ExitSignalCaught(Exception):
    pass


class HungryHungryHipposCatchSignals(HungryHungryHippos):
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True

    def blpop(self, keys=[]):
        if self.kill_now == True:
            raise ExitSignalCaught()

        (k, v) = super(HungryHungryHipposCatchSignals, self).blpop(keys)
        
        if self.kill_now == True:
            self.r.rpush(k, v)
            raise ExitSignalCaught()
        
        return (k, v)
        
    def blpop_lock(self, keys=[]):
        if self.kill_now == True:
            raise ExitSignalCaught()
        
        (lock_success, k, v) = super(HungryHungryHipposCatchSignals, self).blpop_lock(keys)
        
        if self.kill_now == True:
            if lock_success == True:
                self.release_lock(v)
                
            self.r.rpush(k, v)  # put it back where you found it
            raise ExitSignalCaught()
        
        return (lock_success, k, v)
    
