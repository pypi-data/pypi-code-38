# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import os
import sys

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class PidLock(models.Model):
    """
    Table to store process IDs, so we can have only 1 copy of a management
    command running.
    
    Usage:
    from commonstuff.models import PidLock
    pid_lock = PidLock(process=__file__)
    pid_lock.save_or_die()
    # code here maybe won't run because of die at the previous line
    # clean up at the very end (e.g. at destructor) is a good idea
    if pid_lock.pk:
        pid_lock.delete()
    
    Based on
    http://blog.tplus1.com/blog/2012/08/08/python-allow-only-one-running-instance-of-a-script/
    but we use DB here because:
    1) django does not have default dir that is 100% writable for a management
    command, file permisssions are always a pain,
    2) lock files with pids in project dir can be deleted then you (r)sync from
    dev to prod,
    3) /tmp can be cleaned by another process.
    """
    process = models.CharField('process', editable=False, blank=False,
                               unique=True, max_length=255)
    pid = models.PositiveIntegerField('pid', blank=False, editable=False)
    
    class Meta:
        verbose_name = 'PID lock'
        verbose_name_plural = 'PID locks'
    
    def __str__(self):
        return '%(verbose_name)s for "%(process)s"' % {
            'verbose_name': self._meta.verbose_name,
            'process': self.process,
        }
    
    def pid_is_running(self):
        try:
            os.kill(self.pid, 0)
        except OSError:
            return False
        return True
    
    def save_or_die(self, *args, **kwargs):
        try:
            another_lock = PidLock.objects.get(process=self.process)
            if another_lock.pid_is_running():
                sys.exit(0)  # ooops, we are a copy
            else:
                another_lock.delete()
        except PidLock.DoesNotExist:
            pass
        return self.save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.pid = os.getpid()
        return super(PidLock, self).save(*args, **kwargs)
