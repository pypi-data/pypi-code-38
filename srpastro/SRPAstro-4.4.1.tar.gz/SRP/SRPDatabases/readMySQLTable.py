""" Utility functions and classes for SRP

Context : SRP
Module  : Databases.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 29/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (21/02/2017) First version.
        : (29/04/2017) 1mi timeout added.
"""

import mysql.connector as pm
from astropy.table import Table


def readMySQLTable (ihost, idbase, iuser, ipwd, icmd):
    db = pm.connect(user=iuser, password=ipwd, host=ihost, database=idbase, connect_timeout=60)
    cursor = db.cursor()
    cursor.execute(icmd)
    cols = cursor.column_names
    dt = [a for a in cursor]
    t = Table(rows=dt,names=cols)
    return t

