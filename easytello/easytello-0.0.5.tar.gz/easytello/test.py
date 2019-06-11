import tello

d = tello.Tello()

d.streamon() 
d.wait(10)
d.streamoff()