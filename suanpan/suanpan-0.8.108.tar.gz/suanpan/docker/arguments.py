# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import arguments as base
from suanpan.dw import arguments as dw
from suanpan.storage import arguments as storage

Int = base.Int
String = base.String
Float = base.Float
Bool = base.Bool
List = base.List
ListOfString = base.ListOfString
ListOfInt = base.ListOfInt
ListOfFloat = base.ListOfFloat
ListOfBool = base.ListOfBool
IntOrFloat = base.IntOrFloat
IntFloatOrString = base.IntFloatOrString
BoolOrString = base.BoolOrString
StringOrListOfFloat = base.StringOrListOfFloat
File = storage.File
Folder = storage.Folder
Data = storage.Data
Json = storage.Json
Csv = storage.Csv
Npy = storage.Npy
Model = storage.Model
H5Model = storage.H5Model
Checkpoint = storage.Checkpoint
JsonModel = storage.JsonModel
SklearnModel = storage.SklearnModel
Table = dw.Table
