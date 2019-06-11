# -*- coding: utf-8 -*-
import time
import phi2.phi2 as phi2
phi2.set("com8", 9600)
phi2.open()
time.sleep(1)
while True:
    k = int(input("Ingrese un numero para comenzar o 0 para terminar"))
    if (k != 0):
        for i in range(10):
            print("Intensidad" + str(i))
            phi2.pwm(1, i)
            time.sleep(3)
            phi2.down()
    else:
        print("FIN")
        break

