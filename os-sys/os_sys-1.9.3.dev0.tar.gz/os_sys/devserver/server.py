import socket
import argparse

class Request(object):
	"A simple http Request object"
	
	def __init__(self, raw_request):
		self._raw_request = raw_request
		
		self._method, self._path, self._protocol, self._headers = self.parse_request()
	
	def parse_request(self):
		"Turn basic request headers in something we can use"
		temp = [i.strip() for i in self._raw_request.splitlines()]
		
		if -1 == temp[0].find('HTTP'):
			raise InvalidRequest('Incorrect Protocol')
		
		# Figure out our request method, path, and which version of HTTP we're using
		method, path, protocol = [i.strip() for i in temp[0].split()]
		
		# Create the headers, but only if we have a GET reqeust
		headers = {}
		if 'GET' == method:
			for k, v in [i.split(':', 1) for i in temp[1:-1]]:
				headers[k.strip()] = v.strip()
		else:
			raise InvalidRequest('Only accepts GET requests')
		
		return method, path, protocol, headers
	
	def __repr__(self):
		return repr({'method': self._method, 'path': self._path, 'protocol': self._protocol, 'headers': self._headers})

def run(port=8082, **files):
    
    HOST,PORT = '127.0.0.1',port
     
    my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    my_socket.bind((HOST,PORT))
    my_socket.listen(1)
     
    print('Serving on port ',PORT)
     
    while True:
        connection,address = my_socket.accept()
        Request = connection.recv(1024).decode('utf-8')
        string_list = Request.split(' ')     # Split request from spaces
     
        method = string_list[0]
        requesting_file = string_list[1]
     
        print('Client request ',requesting_file)
     
        myfile = requesting_file.split('?')[0] # After the "?" symbol not relevent here
        myfile = myfile.lstrip('/')
        if(myfile == ''):
            myfile = 'index.html'    # Load index file as default
     
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
            response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')#EFWJIU
     
        final_response = header.encode('utf-8')
        final_response += response
        connection.send(final_response)

def isset(array, item):
    try:
        array[item]
    except KeyError:
        return False
    else:
        return True
def exec_return(code, re):
    import sys
    from io import StringIO
    import contextlib
    class Proxy(object):
        def __init__(self,stdout,stringio):
            self._stdout = stdout
            self._stringio = stringio
        def __getattr__(self,name):
            if name in ('_stdout','_stringio','write'):
                object.__getattribute__(self,name)
            else:
                return getattr(self._stringio,name)
        def write(self,data):
             self._stdout.write(data)
             self._stringio.write(data)

    @contextlib.contextmanager
    def stdoutIO(stdout=None):
        old = sys.stdout
        if stdout is None:
            stdout = StringIO()
        sys.stdout = Proxy(sys.stdout,stdout)
        yield sys.stdout
        sys.stdout = old


    with stdoutIO() as s:
        request = re
        exec(code)
    return s.getvalue()

import signal
import time
import sys

def run_program():
    while True:
        time.sleep(1)
        print("a")

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nReally quit? (y/n)> ").lower().startswith('y'):
            print('breaking...')
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

from pynput import keyboard
import threading
class break_(threading.Thread):
    def __init__(self):
        self.HOST = None
        self.PORT = None
        super().__init__()
    def run(self):
        pass
def is_port_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
def run_(port=8082, host='127.0.0.1', *_files):
    _f = list(_files)
    files = {}
    for item in _f:
        try:
            files[item[0]] = item[1]
        except:
            files[item[0]] = 'error'
    import pickle
    import __main__ as ma
    global HOST, PORT
    if __name__ == 'gfhdsuyvsdjhkjgsfsgbhgdfk':
        return
    else:
        HOST,PORT = '127.0.0.1',port
        my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        my_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        my_socket.bind((HOST,PORT))
        my_socket.listen(1)
        print('Serving on port ',PORT)
    while True:
        class r():
            def __init__(self):
                self.GET = {}
                self.POST = {}
        req = r()
        try:
                # store the original SIGINT handler
            connection,address = my_socket.accept()
        except KeyboardInterrupt:
            print('breaking...')
            
            raise SystemExit
        _request = connection.recv(4096)
        Request = _request.decode('utf-8')
        start = Request
        data = start.split('\n')
        string_list = Request.split(' ')     # Split request from spaces
        try:
            requesting_file = string_list[1]
        except:
            continue


        print('Client request ',requesting_file.split('?')[0])
        file = requesting_file
        if isset(files, str(file + '-settings')):
            settings = files[str(file + '-settings')]
            assert type(data) == type({})
            settings['normal'] = False
            items_list = []
        else:
            settings = {}
            settings['normal'] = True
        try:
            _POST = data[len(data) - 1]
            POST = _POST.split('\\n')[-1]
        except Exception as ex:
            print('WARNING:',ex)
            POST = ''
        else:
            if POST != '' and POST != []:
                LIST = POST.split('&')
                for item in LIST:
                    if item != '':
                        key, data = item.split('=')
                        req.POST[key] = data
            print('POST: ' + str(req.POST))
        myfile = requesting_file.split('?')[0] # After the "?" symbol not relevent here
        if '?' in requesting_file:
            get = requesting_file.split('?')[1:]
            get = ''.join(get)
            get_list = get.split('&')
            for get_item in get_list:
                if get_item != '' and '=' in get_item:
                    get_key, get_data = get_item.split('=')
                    req.GET[get_key] = get_data
            print('GET: ' + str(req.GET))
        if(myfile == '/'):
            myfile = 'index'    # Load index file as default
        ex = None 
        try:
            try:
                file = files[myfile]
            except:
                try:
                    my = myfile + 'index'
                    file = files[my]
                except:
                    myfile += '/index'
                    file = files[myfile]

            response = file(req)
            codet = 200
            name = 'Windows'
            import platform
            plat = platform.system()
            if '<?py' in response and 'py?>' in response:
                request = req
                code = response.split('<?py')[1:]
                for p in code:
                    to_do = p.split('py?>')[0]
                    try:
                        a = exec_return(to_do, request)
                    except Exception as ex:
                        a = 'python internal server error Traceback: %s' % ex
                        codet = 500
                    print('python:', a)
                    response = response.replace('<?py'+to_do+'py?>', a, 1)
            windows = name in plat
            if '<?php' in response and '?>' in response:
                import subprocess
                import os
                from distutils.sysconfig import get_python_lib as gpl
                request = req
                code = response.split('<?php')[1:]
                php_done = True
                why = ''
                if __name__ != 'fg':
                    with open('script.php', 'wb') as file:
                        file.write(str(response).encode('utf-8'))
                    try:
                        if windows:
                            proc = subprocess.Popen(r"%s\os_sys\devserver\core\php\php script.php" % gpl(), shell=True, stdout=subprocess.PIPE)
                        else:
                            proc = subprocess.Popen(r"%s\os_sys\devserver\core\php_osx\php\main\php script.php" % gpl(), shell=True, stdout=subprocess.PIPE)
                        a = proc.stdout.read().decode('utf-8')
                    except Exception as ex:
                        codet = 500
                        print('WARNING:', ex)
                        php_done = False
                        a = ''
                        why = 'WARNING: error while trying to execute php code traceback: %s' %  ex
                    if "is not recognized as an internal or external command" in a:
                        codet = 500
                        a=''
                        php_done = False
                        if name != plat:
                            why = 'WARNING: php runner only tested on this moment on windows not on %s yet' % plat
                        else:
                            why = 'WARNING: internal server error php can\'t be loaded'
                    if php_done:
                        response = a
                    else:
                        response = response.replace('<?php'+to_do+'?>', '<script>alert("%s");</script>' % why, 1)
                        php_done = True
            header = 'HTTP/1.1 200 OK\n'
            response = response.encode('utf-8')
            if(myfile.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif(myfile.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'
            
            header += 'Content-Type: '+str(mimetype)+'\n\n'
        
        except (KeyError, KeyboardInterrupt) as e:
            print(e)
            if e == KeyboardInterrupt:
                raise SystemExit
            codet = 404
            header = 'HTTP/1.1 404 Not Found\n\n'
            response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
        except Exception as e:
            print(e)
            if e == KeyboardInterrupt:
                raise SystemExit
            codet = 500
            header = 'HTTP/1.1 500 Internal Server Error\n\n'
            response = '<html><body><center><h3>Error 500: Internal Server error</h3><p>Python HTTP Server</p></center></body></html>'.encode('utf-8')
        from time import strftime
        final_response = header.encode('utf-8')
        final_response += response
        connection.send(final_response)
        connection.close()
        stamp = strftime("%Y-%m-%d %H:%M:%S")
        code = codet
        file = requesting_file.split('?')[0]
        port = PORT
        host = HOST
        type_req = string_list[0]
        print('[%s] - method: %s - client request: %s - on: %s:%s - status: %s' % (stamp, type_req, file, host, str(port), str(code)))
