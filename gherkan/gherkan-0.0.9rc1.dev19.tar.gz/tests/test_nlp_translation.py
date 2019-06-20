# coding: utf-8
from gherkan.processing import Temp2NL_nomajka
fill_action = Temp2NL_nomajka.FillActions()

VarsVals = ['robotR1', '4']
Type = "equality"
Values = "4"
PhraseStr = "ProgramNumber"

TempData = [VarsVals, Type, Values, PhraseStr]
output = fill_action.ParseMainAction(data=TempData)
print(output)

