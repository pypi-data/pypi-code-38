# coding: utf-8
from gherkan.processing import Temp2NL

fill_action = Temp2NL.FillActions()
Name = "PNStart"
VarsVals = ['robotR1', 2]
Type = "equality"
Values = "1"
TempStr="start"

TempData = ["PNStart", ['robotR1', 2], "equality", "1", "start"]
print(TempData)
sentence_core_part = fill_action.ParseMainAction(TempData)
print(sentence_core_part)

TempData = ["sDest", ['shuttleXY', 2], "equality", "1", "destination is"]
print(TempData)
sentence_core_part = fill_action.ParseMainAction(TempData)
print(sentence_core_part)

TempData = ["sState", ['storageXY'], "bool", "1", "free"]
print(TempData)
sentence_core_part = fill_action.ParseMainAction(TempData)
print(sentence_core_part)

TempData = ["sAct", ['shuttleX'], "bool", "1", "move"]
print(TempData)
sentence_core_part = fill_action.ParseMainAction(TempData)
print(sentence_core_part)

TempData = ["sAct", ['shuttleX', "stationZ"], "bool", "1", "move to"]
print(TempData)
sentence_core_part = fill_action.ParseMainAction(TempData)
print(sentence_core_part)

# TempData = ["sCount", ['storageX', "5"], "equality", "5", "count is"]
# print(TempData)
# sentence_core_part = fill_action.ParseMainAction(TempData)
# print(sentence_core_part)


