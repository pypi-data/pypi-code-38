"""
Data Science Work Space Duct

duct contains all the hadoop component libraries for
connecting to the environment. 'duct' was deliberately chosen to 
represent the collection of connection components, but avoid names
like pipe, connection, stream to avoid naming confusion as well as
to not limit the types of work space components included"""


import os                                               as _os
from os                 import environ                  as _env
from pydoc              import locate                   as _locate
from IPython.core.magic import register_line_cell_magic as _register_line_cell_magic
from dsws.util          import qry_type                 as _qry_type
from dsws.util          import sp                       as _sp
from IPython.display    import HTML                     as _HTML
from dsws.util          import launch_term              as _launch_term


@_register_line_cell_magic
def imp(line='', cell=''):
    qry=str('\n'.join([line,cell]).strip())
    if qry=='':
        _launch_term(_WS_MAGIC_MAP["imp_cli"].command)
    else: 
        _WS_MAGIC_MAP["imp_"+_qry_type(qry)].qry(qry,"disp")
        
@_register_line_cell_magic
def hive(line='', cell=''):
    qry=str('\n'.join([line,cell]).strip())
    if qry=='':
        _launch_term(_WS_MAGIC_MAP["hive_cli"].command+" --hiveconf hive.execution.engine=mr")
    else: 
        _WS_MAGIC_MAP["hive_"+_qry_type(qry)].qry(qry,"disp",engine="mr")

@_register_line_cell_magic
def hos(line='', cell=''):
    qry=str('\n'.join([line,cell]).strip())
    if qry=='':
        _launch_term(_WS_MAGIC_MAP["hive_cli"].command+" --hiveconf hive.execution.engine=spark")
    else: 
        _WS_MAGIC_MAP["hive_"+_qry_type(qry)].qry(qry,"disp",engine="spark")

@_register_line_cell_magic
def tez(line='', cell=''):
    qry=str('\n'.join([line,cell]).strip())
    if qry=='':
        _launch_term(_WS_MAGIC_MAP["hive_cli"].command+" --hiveconf hive.execution.engine=tez")
    else:
        _WS_MAGIC_MAP["hive_"+_qry_type(qry)].qry(qry,"disp",engine="tez")

@_register_line_cell_magic
def sql(line='', cell=''):
    qry=str('\n'.join([line,cell]).strip()) 
    spark.qry(qry,"disp")
        
del imp, hive, hos, tez, sql

# Magic Map dict is used to handle conditions when WS configurations are not provided
_WS_MAGIC_MAP={}
if "WS_IMPALA_IMP" in _env:
    _WS_MAGIC_MAP.update({"imp_cli":"imp",})
if "WS_IMPALA_IMPYLA" in _env:
    _WS_MAGIC_MAP.update({"imp_conn":"impyla",})
if "WS_HIVE_HBL" in _env:
    _WS_MAGIC_MAP.update({"hive_cli":"hbl",})
if "WS_HIVE_HIMPYLA" in _env:
    _WS_MAGIC_MAP.update({"hive_conn":"himpyla",})

# Instantiate all configured WorkSpaces, define in duct namespace
for ws in [e for e in _env if e[:3]=="WS_"]:
    mod=ws.lower();inst=mod.split("_")[2];cls=inst.title();
    exec("%s=_locate('dsws.%s.%s')"%(cls,mod,cls))
    exec("%s=%s()"%(inst,cls))
    exec("del %s"%cls)

# Convert str:str map to str:inst map
for k,v in _WS_MAGIC_MAP.items():
    exec("_WS_MAGIC_MAP['%s']=%s" % (k,v))

del ws, k, v, mod, inst, cls
#del mod, inst, cls, v, k, ws
