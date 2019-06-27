import socket
def run(port=9999, location='cd'):
    import os
    path = ''
    if location != 'cd':
        path = location
    HOST,PORT = '127.0.0.1',port
     
    my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    my_socket.bind((HOST,PORT))
    my_socket.listen(1)
     
    print('Serving on port ',PORT)
     
    while True:
        connection,address = my_socket.accept()
        request = connection.recv(1024).decode('utf-8')
        string_list = request.split(' ')     # Split request from spaces
     
        method = string_list[0]
        requesting_file = string_list[1]
     
        print('Client request ',requesting_file)
     
        myfile = requesting_file.split('?')[0] # After the "?" symbol not relevent here
        myfile = myfile.lstrip('/')
        if(myfile == ''):
            myfile = 'index.html'    # Load index file as default
        if path != '':
            myfile = os.path.join(path, myfile)
        try:
            file = open(myfile,'rb') # open file , r => read , b => byte format
            response = file.read()
            file.close()
     
            header = 'HTTP/1.1 200 OK\n'
     
            if(myfile.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif(myfile.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'
     
            header += 'Content-Type: '+str(mimetype)+'\n\n'
     
        except Exception as e:
            header = 'HTTP/1.1 404 Not Found\n\n'
            response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
     
        final_response = header.encode('utf-8')
        final_response += response
        connection.send(final_response)
if __name__ == '__main__':
    run()
    connection.close()
