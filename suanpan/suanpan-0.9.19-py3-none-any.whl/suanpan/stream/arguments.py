# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import arguments as base
from suanpan.arguments import auto  # pylint: disable=unused-import
from suanpan.dw import arguments as dw
from suanpan.mq import arguments as mq  # pylint: disable=unused-import
from suanpan.mstorage import arguments as mstorage
from suanpan.storage import arguments as storage

Int = base.Int
Float = base.Float
Bool = base.Bool
String = base.String
List = base.List
ListOfString = base.ListOfString
ListOfInt = base.ListOfInt
ListOfFloat = base.ListOfFloat
ListOfBool = base.ListOfBool
IntOrFloat = base.IntOrFloat
IntFloatOrString = base.IntFloatOrString
BoolOrString = base.BoolOrString
StringOrListOfFloat = base.StringOrListOfFloat
Json = base.Json

File = storage.File
Folder = storage.Folder
Data = storage.Data
Csv = storage.Csv
Npy = storage.Npy
Visual = storage.Visual
Model = storage.Model
H5Model = storage.H5Model
Checkpoint = storage.Checkpoint
JsonModel = storage.JsonModel

Table = dw.Table
