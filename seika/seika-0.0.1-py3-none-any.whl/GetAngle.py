import serial
import time

def read_sensor(port = '/dev/ttyUSB0',  
                address = 178,
                baudrate = 9600,               
                bytesize = 8,                    
                parity = 'N',                    
                stopbits = 1):
                    
    with serial.Serial(port, baudrate, bytesize, parity, stopbits) as s:
        time.sleep(0.1)
        t0 = time.time()
        s.timeout=0.1
        while True:
            time.sleep(0.001)
            s.setRTS(1)  
            s.write(bytes((address,int("05",16))))
            time.sleep(0.003)
            s.setRTS(0)  
            d = s.read(11) 
            if d == b'': print('Sensor is not answering', '\n' , 'Try other address')
            else: 
                if checksum(d)==True: print('Time: %ss , Message: %s , Angle: %s°' %('{:.3f}'.format(time.time()-t0), str(d), float(d[1:7])))
                else: print('Checksum wrong')
            
def read_sensor_to_file(filename,
                        nreadings,
                        port = '/dev/ttyUSB0',  
                        address = 178,
                        baudrate = 9600,               
                        bytesize = 8,                    
                        parity = 'N',                    
                        stopbits = 1):
                            
    with serial.Serial(port, baudrate, bytesize, parity, stopbits) as s , open(filename, 'w') as f:
        time.sleep(0.1)
        t0 = time.time()
        s.timeout=0.1
        for i in range(nreadings):
            time.sleep(0.001)
            s.setRTS(1)  
            s.write(bytes((address,int("05",16))))
            time.sleep(0.003)
            s.setRTS(0)  
            d = s.read(11) 
            if d == b'': 
                print('Sensor is not answering', '\n' , 'Try other address')
                i-=1
            else:
                if checksum(d)==True: 
                    x = '{:6d}'.format(i) + '\t' + '{:10.3f}'.format(time.time()-t0) + '\t' + str(d) + '\t' + str(float(d[1:7])) + '\n'
                    f.write(x)
                else: 
                    print('Checksum wrong')
                    i-=1
            
def search_sensor(port = '/dev/ttyUSB0',  
                  baudrate = 9600,               
                  bytesize = 8,                    
                  parity = 'N',                    
                  stopbits = 1):
                      
    addresslist = []
    with serial.Serial(port, baudrate, bytesize, parity, stopbits) as s:
        time.sleep(0.1)
        s.timeout=0.1
        for address in range(178,256):
            time.sleep(0.001)
            s.setRTS(1)  
            s.write(bytes((address,int("05",16))))
            time.sleep(0.003)
            s.setRTS(0)  
            d = s.read(11) 
            if d != b"": addresslist.append("%s" %address)
    print('Sensoraddresses: %s' %addresslist)
            
def checksum(d):
    
    try:
        if d[8:10].decode("ascii") == "{:02x}".format(d[0] ^d[1]^d[2]^d[3]^d[4]^d[5]^d[6]^d[7]).upper(): return True 
        else: return False
    except: return False