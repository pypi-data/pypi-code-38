# server.py 
import socket                                         
import time
import pygame
import pygame.camera
import base64

def runserver():
    # create a socket object
    serversocket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)

    #Sets reusator so previous executions doesn't blocks the address with waiting packets
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # get local machine name
    host = socket.gethostname()                           

    port = 8081                                          

    # bind to the port
    serversocket.bind((host, port))                                  

    # queue up to 5 requests
    serversocket.listen(5)                                           

    #initialize camera
    pygame.camera.init()
    cams = pygame.camera.list_cameras()
    cam = pygame.camera.Camera(cams[0])
    cam.start()

    while True:
        try:
            # establish a connection
            clientsocket,addr = serversocket.accept()      

            print("Got a connection from %s" % str(addr))
            img = cam.get_image()
            pygame.image.save(img, "current_image.jpg")
            image_data = open('current_image.jpg', 'rb')
            current_data = image_data.read(1024)

            while (current_data):
                try:
                    clientsocket.send(current_data)    
                except:

                    break
                current_data = image_data.read(1024)

            clientsocket.close()

        except KeyboardInterrupt:
            break


    cam.stop()

    print("Service closed")