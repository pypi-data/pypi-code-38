#Muestra el comando de 2 motores conectados a la salida 0-1 (pin 2 y 3)
#y controlados por las flechas del cursor

from msvcrt import getch
import os
import phi2.phi2 as phi2


def pantalla():
    os.system("cls")
    print("***********************************")
    print("Teclas en accion ")
    print("***********************************")
    print("Use las flechas de cursor para manejar ")
    print("")
    print("")

pantalla()
#conectamos a phi2
phi2.set("com8", "9600")
phi2.open()



while True:
    key = ord(getch())
    if (key == 80):
        print("Parar --> paran los dos motores")
        phi2.write(0)
    if (key == 72):
        print("Adelante --> encienden los dos motores")
        phi2.write(255)
    if (key == 77):
        print("Derecha  --> Se detiene el de la derecha y se enciende el de la izquierda")
        phi2.write(2)
    if (key == 75):
        print("Izquierda --> se detiene el de la izquierda y se enciende el de la derecrach")
        phi2.write(1)