# Version 4.0 testing ultrasonido
# -*- coding: utf-8 -*-

# Libreria Phi para usar python como raspberry
import time
import serial

gpuerto = "com7"
gvelocidad = 9600
g_arduino = serial.Serial()


def close():
    try:
        g_arduino.close()
        res = "OK"
        return res
    except ValueError:
        res = "ERR"
        return res


def down():
    # pone todos los puertos de salida en low
    try:
        g_arduino.write(b'D')
        time.sleep(0.1)
        res = "OK"
        return res
    except ValueError:
        res = "ERR"
        return res


def open():
    try:
        # se abre la comunicacion entre arduino y python
        global g_arduino
        g_arduino = serial.Serial(gpuerto, gvelocidad)
        # Reset manual del Arduino
        g_arduino.setDTR(False)
        time.sleep(0.3)
        # Se borra cualquier data que haya quedado en el buffer
        g_arduino.flushInput()
        g_arduino.setDTR()
        time.sleep(0.3)
        if (g_arduino.isOpen()):
            res = "OK"
        else:
            res = "ERR"
        time.sleep(2)
        return res
    except ValueError:
        res = "ERR"
        return res


def pwm(p, v):
    # donde p es el puerto a enviar puede ser
    # 1, 3 , 4, 7, 8 (3,5,6,9,10 del arduino)
    # v es el valor, numero de 0-9 que indica la
    # potencia(se lo multiplica por 25)
    try:
        lista = {1, 3, 4, 7, 8}
        if (p in lista):
            if (v >= 0 & v <= 9):
                g_arduino.write(b'P')
                envio = str(p).encode('utf-8')
                g_arduino.write(envio)
                envio = str(v).encode('utf-8')
                g_arduino.write(envio)
                print(p, v)
                res = "OK"
            else:
                res = "ERR"
        else:
            res = "ERR"
        return res
    except ValueError:
        res = "ERR"
        return res


def read(p):
    # p puede ser 0,1,2,3 (para indicar puertos individuales) O 9 para todos
    try:
        g_arduino.write(b'R')
        time.sleep(.1)
        l = g_arduino.readline().strip()
        dato = l.decode('ascii', errors='replace')
        if p == 9:
            return dato
        else:
            if (p >= 0 & p <= 7):
                datop = dato[p]
                return datop
            else:
                res = "ERR"
                return res
    except ValueError:
        res = "ERR"
        return res


def set(p, v):
    # define el puerto y la velocidad de conexion
    global gpuerto
    gpuerto = p
    global gvelocidad
    gvelocidad = v


def up():
    # pone todos los puertos de salida en high
    try:
        g_arduino.write(b'U')
        time.sleep(0.1)
        res = "OK"
        return res
    except ValueError:
        res = "ERR"
        return res


def write(dato):
    # el dato debe estar entre 0 y 255
    try:
        if (dato >= 0 & dato <= 255):
            g_arduino.write(b'W')
            # time.sleep(.1)
            envio = str(format(dato, 'b').zfill(8))
            g_arduino.write(envio.encode())
            res = "OK"
        else:
            res = "ERR"
        return res
    except ValueError:
        res = "ERR"
        return res


def write_l(puerto):
    # pone en un valor low en el puerto
    try:
        if (puerto >= 0 & puerto <= 7):
            g_arduino.write(b'L')
            envio = str(puerto).encode('utf-8')
            g_arduino.write(envio)
            res = "OK"
        else:
            res = "ERR"
        return res
    except ValueError:
        res = "ERR"
        return res


def write_h(puerto):
    # pone en un valor high en el puerto
    try:
        if (puerto >= 0 & puerto <= 7):
            g_arduino.write(b'H')
            envio = str(puerto).encode('utf-8')
            g_arduino.write(envio)
            res = "OK"
        else:
            res = "ERR"
        return res
    except ValueError:
        res = "ERR"
        return res


def us_read():
    # lee la distancia en cm del sensor ultrasonido
    try:
        g_arduino.write(b'S')
        time.sleep(.5)
        l = g_arduino.readline().strip()
        dato = l.decode('ascii', errors='replace')
        return dato
    except ValueError:
        res = "ERR"
        return res

def sm_write(dato):
    #el dato debe estar entre 0 y 180
    try:
        if (dato >= 0 & dato <= 180):
            g_arduino.write(b'M')
            #time.sleep(.1)
            envio = (str(dato)+"#").encode('utf-8')
            g_arduino.write(envio)
            res = "OK"
        else:
            res = "ERR"
        return res
    except ValueError:
        res = "ERR"
        return res
