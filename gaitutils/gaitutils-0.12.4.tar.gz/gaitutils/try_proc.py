import psutil

nprocs = 0
script_name = 'gaitmenu-script.py'
for proc in psutil.process_iter():
    try:
        cmdline = proc.cmdline()
        if cmdline:
            if 'python' in cmdline[0] and len(cmdline) > 1:
                if script_name in cmdline[1]:
                    print cmdline
                    nprocs += 1
                    if nprocs == 2:
                        pass
    # catch NoSuchProcess for procs that disappear inside loop
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
