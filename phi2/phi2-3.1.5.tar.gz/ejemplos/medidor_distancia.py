##sensor ultrasonido
from time import *
from os import *

import phi2.phi2 as phi2

phi2.set("com8", 9600)
phi2.open()
sleep(1)
system('cls')
while True:
    d = phi2.us_read()
    print("Distancia: " + d)
    sleep(4)
