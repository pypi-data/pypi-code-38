""" Utility functions and classes for SRP

Context : SRP
Module  : Databases.py
Version : 1.2.1
Author  : Stefano Covino
Date    : 29/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (21/02/2017) First version.
        : (13/03/2017) Wrtten symmetrically with the MySQL version.
        : (14/03/2017) Rewritten in a more efficient way for the given library.
        : (29/04/2017) 1min timeout added.
"""

import postgresql as ps
from astropy.table import Table


def readPostgresTable (ihost, idbase, iuser, ipwd, icmd):
    db = ps.open(host=ihost,database=idbase,user=iuser,password=ipwd,connect_timeout=60)
    cursor = db.prepare(icmd)
    cols = cursor.column_names
    dt = [a for a in cursor]
    t = Table(rows=dt,names=cols)
    return t

