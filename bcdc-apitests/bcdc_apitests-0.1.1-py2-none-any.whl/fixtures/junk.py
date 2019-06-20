

inList = ['1', 'b', '4a']

newList = [i for i in inList if not i.isdigit()]
print newList
import re


newList = [re.sub("[^0-9]", "", i) if not i.isdigit() else i for i in inList ]
print newList

newList = [0 if not i.strip() else i for i in newList ]
print newList


import re
re.sub("[^0-9]", "", "sdkjh987978asd098as0980a98sd")
