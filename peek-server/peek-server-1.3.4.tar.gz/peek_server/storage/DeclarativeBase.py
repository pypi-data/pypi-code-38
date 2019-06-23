""" 
 * orm.Base.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData

metadata = MetaData(schema="peek_server")
DeclarativeBase = declarative_base(metadata=metadata)
