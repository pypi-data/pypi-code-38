#agrego scale para regular la velocidad del semaforo
#uso phi2 para controlar el encendido de los leds que
#representan a los semaforo(uso 6 salidas)

#semaforo1 conexionado:
    #rojo: salida0 phi2 ----> pin2 arduino
    #amarillo: salida1 phi2 ----> pin3 arduino
    #verde: salida2 phi2 ----> pin4 arduino

#semaforo2 conexionado:
    #rojo: salida4 phi2 ----> pin6 arduino
    #amarillo: salida5 phi2 ----> pin7 arduino
    #verde: salida6 phi2 ----> pin8 arduino



from tkinter import *
from time import  *
import phi2



def rojo():
    canvas.create_oval(100, 10, 180, 80, width=2, fill='red', outline='')
    canvas.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')


def amarillo():
    canvas.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas.create_oval(100, 90, 180, 160, width=2, fill='yellow', outline='')
    canvas.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')


def verde():
    canvas.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas.create_oval(100, 170, 180, 240, width=2, fill='green', outline='')


def rojo2():
    canvas2.create_oval(100, 10, 180, 80, width=2, fill='red', outline='')
    canvas2.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')


def amarillo2():
    canvas2.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 90, 180, 160, width=2, fill='yellow', outline='')
    canvas2.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')


def verde2():
    canvas2.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 170, 180, 240, width=2, fill='green', outline='')





def apagar():
    canvas.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 10, 180, 80, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 90, 180, 160, width=2, fill='gray', outline='')
    canvas2.create_oval(100, 170, 180, 240, width=2, fill='gray', outline='')


vent1 = Tk()
vent1.title("Mi primer ventana")
vent1.geometry("600x600")
etiq1 = Label(vent1, text="Sistema de Semáforos")
etiq1.pack()
canvas = Canvas(width=200, height=300, bg='blue')
canvas.pack(side = LEFT)
canvas.create_text(50,10,text="Semáforo 1")

canvas.update()

canvas2 = Canvas(width=200, height=300, bg='blue')
canvas2.pack(side = RIGHT)
canvas2.create_text(50,10,text="Semáforo 2")


#checkbox
cboxvar = IntVar()  #creo una variable entera(puede ser BooleanVar) para almacenar el estado del control
cbox = Checkbutton(vent1, text="Intermitente", variable = cboxvar)  #creo el control
cbox.place(x=20, y=70) #coloco el checkbox en la ventana(lo puedo poner en el canvas tamb ien)

#scale
scalevar = IntVar()
scale = Scale(vent1, variable = scalevar, from_=1, to=10, label = "Velocidad en segundos", orient = HORIZONTAL )
scale.pack()

label = Label(vent1)
label.pack()



#variable de retardo
t = 4

apagar()
canvas.update()
canvas2.update()
sleep(t)
LOOP_ACTIVE = True
led = "R"
phi2.set("com9", 9600)
phi2.open()
sleep(1)

while LOOP_ACTIVE:
    t = scalevar.get()
    if cboxvar.get()==0:   #con get obtengo el estado del check
        if led == "V":
            verde()
            rojo2()
            vent1.update()
            phi2.write(20) # 20 binario es 00010100 enciende puerto 2 y 4
            sleep(t)       #verde semaforo 1 y rojo semaforo 2
            amarillo()
            rojo2()
            phi2.write(18)
            vent1.update()
            sleep(t)
            led = "R"
        else:
            rojo()
            verde2()
            phi2.write(65)
            vent1.update()
            sleep(t)
            amarillo2()
            rojo()
            phi2.write(33)
            vent1.update()
            sleep(t)
            led = "V"
    else:
        #intermitente
        amarillo()
        amarillo2()
        phi2.write(34)
        vent1.update()
        sleep(t)
        apagar()
        phi2.down()
        vent1.update()
        sleep(t)

#        ROOT.quit()
#        LOOP_ACTIVE = False








