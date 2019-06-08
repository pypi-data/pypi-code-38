import epics

print(epics.ca.find_libca())

print(epics.caget('13IDE:m1.VAL'))
