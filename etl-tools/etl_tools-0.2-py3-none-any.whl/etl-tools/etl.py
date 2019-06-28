from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import math
import time
import getpass
from datetime import datetime, timedelta

import pandas as pd

import logging
logger = logging.getLogger('etl')

BASE_PATH = os.path.abspath(os.path.join('..'))


class Etl:
    def __init__(self):
        pass

    @staticmethod
    def set_datetime():
        dt = datetime.now()
        dt_str = '{}{:02d}{:02d}_{:02d}{:02d}{:02d}'.format(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        # logger.debug('Current system time: {}'.format(dt_str))
        print('Current system time: {}'.format(dt_str))
        return dt, dt_str

    @staticmethod
    def set_yesterday(dt):
        dt_yesterday = dt - timedelta(days=1)
        result = '{}-{:02d}-{:02d}'.format(
            dt_yesterday.year,
            dt_yesterday.month,
            dt_yesterday.day)
        logger.debug('Setting yesterday date for {}'.format(result))
        return result

    @staticmethod
    def calculate_execution_time(dt_start):
        dt_end, _ = set_datetime()
        return (dt_end - dt_start).seconds

    @staticmethod
    def create_date_dimension(self, start='2000-01-01', end='2050-12-31'):
        df = pd.DataFrame({'date': pd.date_range(start, end)})
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
        df['date_int'] = df['date'].apply(lambda x: int(x.strftime('%Y%m%d')))
        df['day_of_month'] = df['date'].dt.day
        df['days_in_month'] = df['date'].dt.days_in_month
        df['days_in_month_remaining'] = df['days_in_month'] - df['day_of_month']
        df['day_of_week'] = df['date'].dt.dayofweek
        df['weekday'] = df['date'].dt.weekday_name
        df['is_weekend'] = (
            df['day_of_week'].apply(lambda x: True if x in [5, 6] else False))
        df['week_of_year'] = df['date'].dt.weekofyear
        df['month_of_year'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.month_name()
        df['month_str'] = df['date'].dt.strftime('%Y-%m')
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        df['year_half'] = (df['quarter'] + 1) // 2
        # Starts-ends.
        df['is_month_start'] = df['date'].dt.is_month_start
        df['is_month_end'] = df['date'].dt.is_month_end
        df['is_quarter_start'] = df['date'].dt.is_quarter_start
        df['is_quarter_end'] = df['date'].dt.is_quarter_end
        df['is_year_start'] = df['date'].dt.is_year_start
        df['is_year_end'] = df['date'].dt.is_year_end
        df['is_leap_year'] = df['date'].dt.is_year_end
        return df

    @staticmethod
    def retry(tries, delay=30, backoff=1.5):
        """Retries a function or method until it returns True."""
        if backoff <= 1:
            raise ValueError('Backoff must be greater than 1')
        tries = math.floor(tries)
        if tries < 0:
            raise ValueError('Tries must be 0 or greater')
        if delay <= 0:
            raise ValueError('Delay must be greater than 0')
        def deco_retry(f):
            def f_retry(*args, **kwargs):
                mtries, mdelay = tries, delay
                rv = f(*args, **kwargs)  # First attempt.
                while mtries > 0:
                    if rv is True:
                        return True
                    mtries -= 1
                    time.sleep(mdelay)  # In seconds
                    mdelay *= backoff
                    print('Delay set to {} seconds'.format(mdelay))
                    rv = f(*args, **kwargs)  # Try again.
                print(str(tries) + ' attempts. Abandoning.')
                return False  # Ran out of tries.
            return f_retry
        return deco_retry

    @staticmethod
    def create_directory(path):
        if not os.path.exists(path):
            print('Creating directory: {}'.format(path))
            os.makedirs(path)

    def local_timezone(self):
        result = {}
        if time.daylight:
            offset_hour_tmp = time.altzone / 3600
        else:
            offset_hour_tmp = time.timezone / 3600
        result['offset_hour'] = 'Etc/GMT%+d' % offset_hour_tmp
        result['timezone_name'] = time.tzname
        return result        

    def log_process_info(self, environment, logfile):
        logger.info('Process ID: {}'.format(os.getpid()))
        logger.info('Environment: {}'.format(environment))
        logger.info('Environment user: {}'.format(os.getlogin()))
        logger.info('Effective user: {}'.format(getpass.getuser()))
        timezone_info = self.local_timezone()
        logger.info('Timezone name: {}'.format(timezone_info['timezone_name']))
        logger.info('Timezone offset: {}'.format(timezone_info['offset_hour']))
        logger.info('Setting log file to: {}'.format(logfile))
