# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import arguments as base
from suanpan.dw import arguments as dw
from suanpan.mq import arguments as mq
from suanpan.mstorage import arguments as mstorage
from suanpan.storage import arguments as storage

Int = base.Int
String = base.String
Float = base.Float
Bool = base.Bool
List = mq.List
Json = base.Json
File = storage.File
Folder = storage.Folder
Npy = mstorage.Npy
Table = dw.Table
