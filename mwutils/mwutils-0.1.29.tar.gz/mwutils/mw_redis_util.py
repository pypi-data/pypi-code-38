import time


def mwbytes_to_float(data):
    f =mwbytes_to_str(data)
    if f is None:
        return None
    else:
        return float(f)

def mwbytes_to_str(data):
    if data is None:
        return None
    else:
        return data.decode()

#
def redis_key_exist(rds,key,waittime):
    if (waittime<=0):
        return False
    else:
        exists =rds.exists(key)
        if exists:
            return True
        else:
            time.sleep(1)
            return redis_key_exist(rds,key,waittime-1)