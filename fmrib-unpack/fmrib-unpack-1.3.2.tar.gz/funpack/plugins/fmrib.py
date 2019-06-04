#!/usr/bin/env python
#
# fmrib.py - Custom loaders for FMRIB-speciifc files.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module contains custom loaders for data files used in FMRIB,
which contain data on imaged subjects.
"""


import functools as ft
import datetime  as dt
import              calendar

import pandas    as pd
import numpy     as np

import funpack


@funpack.sniffer('FMRIBImaging')
@ft.lru_cache()
def columns_FMRIBImaging(infile):
    """Return a list of columns describing the contents of the
    ``FMRIB_internal_info.txt`` file.
    """

    names = ['eid',
             'acq_time',
             'acq_phase',
             'processing_phase',
             'flipped_SWI']

    return [funpack.Column(infile,
                           n,
                           i,
                           200000 + i,
                           0,
                           0) for i, n in enumerate(names)]


@funpack.loader('FMRIBImaging')
def load_FMRIBImaging(infile):
    """Load a file with the same format as the ``FMRIB_internal_info.txt``
    file.
    """

    def parse_acq_date(date):
        year  = int(date[ :4])
        month = int(date[4:6])
        day   = int(date[6:8])
        return dt.date(year, month, day)

    def parse_acq_time(time):
        hour       = int(time[ :2])
        minute     = int(time[2:4])
        second     = int(time[4:6])
        micro      = int(time[7:])
        return dt.time(hour, minute, second, micro,
                       dt.timezone(dt.timedelta(0)))

    def combine_datetime(date, time):
        date = date.to_pydatetime().date()
        time = time.to_pydatetime().timetz()
        return dt.datetime.combine(date, time)

    names = ['eid',
             'acq_date',
             'acq_time',
             'acq_phase',
             'processing_phase',
             'flipped_SWI']

    converters = {'acq_date' : parse_acq_date,
                  'acq_time' : parse_acq_time}

    df = pd.read_csv(infile,
                     header=None,
                     names=names,
                     index_col=0,
                     parse_dates=['acq_time', 'acq_date'],
                     converters=converters,
                     delim_whitespace=True)

    df['acq_time'] = df['acq_date'].combine(df['acq_time'], combine_datetime)
    df.drop('acq_date', axis=1, inplace=True)

    return df


def dateAsYearFraction(d):
    """Normalise dates so they are represented as a year plus year fraction.
    """
    try:
        # this normalisation results in
        # a non-linear representation of
        # time, but this is apparently
        # not important.
        d          = d.timetuple()
        daysinyear = 366 if calendar.isleap(d.tm_year) else 365
        return d.tm_year + (d.tm_yday - 1) / float(daysinyear)
    except Exception:
        return np.nan


@funpack.formatter('FMRIBImagingDate')
def format_dateAsYearFraction(dtable, column, series):
    """Formats dates using :func:`dateAsYearFraction`. """
    return series.apply(dateAsYearFraction)


def normalisedAcquisitionTime(t):
    """Normalises timestamps so they are represented as a year plus year
    fraction, where days are normalised to lie between 7am and 8pm (as
    no scans take place outside of these hours).
    """

    try:

        # see note about non-linearity
        # in dateAsYearFaction. This
        # could also potentially be non-
        # monotonic because we are not
        # taking into account leap-seconds.
        t          = t.timetuple()
        daysinyear = 366 if calendar.isleap(t.tm_year) else 365
        dayfrac    = ((t.tm_hour - 7)    +
                      (t.tm_min  / 60.0) +
                      (t.tm_sec  / 3600.0)) / 13.0

        return t.tm_year + ((t.tm_yday - 1) + dayfrac) / float(daysinyear)
    except Exception:
        return np.nan


@funpack.formatter('FMRIBImagingTime')
def format_normalisedAcquisitionTime(dtable, column, series):
    """Formats timestamps using :func:`normalisedAcquisitionTime`. """
    return series.apply(normalisedAcquisitionTime)
