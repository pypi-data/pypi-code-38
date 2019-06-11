# client.py  
import socket
import time
import pygame.camera
import base64
import pygame
from pygame.locals import*


def runclient():
    white = (255, 64, 64)
    w = 640
    h = 480
    screen = pygame.display.set_mode((w, h))

    while True:        
        try:
            # create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

            # get local machine name
            host = socket.gethostname()                           

            port = 8081

            # connection to hostname on the port.
            s.connect((host, port))                               

            # Receive no more than 1024 bytes
            with open('recieved_file.jpg', 'wb') as image_file:            
                while True:
                    try:
                        encoded_image_data = s.recv(1024)    
                    except:
                        s.close()    
                        break
                    
                    if not encoded_image_data:
                        break
                    
                    image_file.write(encoded_image_data)
            
            s.close()
            
            try:
                img = pygame.image.load('recieved_file.jpg')    
            except:
                break
            

            screen.fill((white))
            screen.blit(img,(0,0))
            pygame.display.flip()
            
        except KeyboardInterrupt:
            pygame.display.quit()
            pygame.quit()
            break

    print("Connection closed")
        