import datetime
def log(caller, message):
    caller = str(caller).split()[1].replace("'", "")[:-1]
    curtime = str(datetime.datetime.now())
    print(f"[{curtime}] [{caller}]: {message}")