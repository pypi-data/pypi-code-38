#!/usr/bin/env python

import pandas as pd

from funpack import sniffer, loader, Column

# Sniffer and loader functions are defined in
# pairs. A pair is denoted by its functions
# being given the same label, passed to the
# @sniffer/@loader decorators
# ("my_datefile_loader" in this example). The
# function names are irrelevant.

@sniffer('my_datefile_loader')
def columns_datefile(infile):

    # A sniifer function must return a
    # sequence of Column objects which
    # describe the file (after it has
    # been loaded by the loader function).
    #
    # The values passed to a Column object
    # are:
    #   - file name
    #   - column name
    #   - column index (starting from 0)
    return [Column(infile, 'eid',              0),
            Column(infile, 'acquisition_date', 1)]

@loader('my_datefile_loader')
def load_datefile(infile):

    def create_date(row):
        return pd.Timestamp(row['year'], row['month'], row['day'])

    df = pd.read_csv(infile, index_col=0, delim_whitespace=True)

    df['acquisition_date'] = df.apply(create_date, axis=1)

    df.drop(['year', 'month', 'day'], axis=1, inplace=True)

    return df
