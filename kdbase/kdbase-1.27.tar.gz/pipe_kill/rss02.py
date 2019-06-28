import os

if __name__ == '__main__':
    pid = 21916
    pidfile = os.path.join("/proc/", str(pid), "status") 
    with open(pidfile) as f: 
        for mem in f: 
            if mem.startswith("VmRSS"): 
              pidmem = int(mem.split()[1])
              print pidmem
              break
