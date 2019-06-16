import sys,os
 # print("\033[1;31m failed \033[0m")
    # print("\033[1;32m success \033[0m")
def faillog(content):
    print("\033[1;31m" + str(content) + "\033[0m")

def successlog(content):
    print("\033[1;32m" + str(content) + "\033[0m")

def warninglog(content):
    print("\033[1;33m" + str(content) + "\033[0m")

def printandresult(command, print_msg=True):
    import subprocess
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = []
    for line in iter(p.stdout.readline, b''):
        line = line.rstrip().decode('utf8')
        if print_msg:
            print(line)
        lines.append(line)
    return ','.join(lines)

class logitem:
    def failitem(self,content,bold=False):
        boldstr = "1" if bold else "0"
        return "\033["+ boldstr +";31m" + str(content) + "\033[0m"

    def successitem(self,content,bold=False):
        boldstr = "1" if bold else "0"
        return "\033["+ boldstr +";32m" + str(content) + "\033[0m"
    
    def warningitem(self,content,bold=False):
        boldstr = "1" if bold else "0"
        return "\033["+ boldstr +";33m" + str(content) + "\033[0m"

class Log:
    def __init__(self, filename="log.text"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass

    def save_log_in_lines(self,lines=None):
        pass