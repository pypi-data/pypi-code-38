# -*- coding: utf-8 -*-

#Ejemplo permite detectar puerta abierta o cerrada a partir de un switch
import time
import phi2.phi2 as phi2 #Importa libreria phi2(la carpeta phi2 debe
                               #estar dentro de la carpeta del proyecto
phi2.set("com8", "9600")  #define el puerto de comunicacion
phi2.open()  #abre la conexion con phi2
time.sleep(1) #espera 1 seg para asegurarse que la conexion esta establecida
i = 0
while True:
    p = phi2.read(0)
    if (p=="0"):
        print("Puerta cerrada")
    else:
        print("Puerta abierta")
    time.sleep(1)
