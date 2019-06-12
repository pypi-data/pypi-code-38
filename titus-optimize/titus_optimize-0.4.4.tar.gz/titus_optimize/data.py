import numpy as np

class Query(object):
    
    def __init__(
        self,
        user,
        app_name,
        cpu_requested,
        ram_requested,
        disk_requested,
        network_requested,
        job_type,
        region,
        env,
        hour,
        ts_feats):
        self.user = user
        self.app_name = app_name
        self.cpu_requested = cpu_requested
        self.ram_requested = ram_requested
        self.disk_requested = disk_requested
        self.network_requested = network_requested
        self.job_type = job_type
        self.region = region
        self.env = env
        self.hour = hour
        self.ts_feats = ts_feats

class Query2(object):

    def __init__(
        self,
        image_name,
        user,
        app_name,
        cpu_requested,
        ram_requested,
        disk_requested,
        network_requested,
        job_type,
        region,
        env,
        hour,
        ts_feats):
        self.image_name = image_name
        self.user = user
        self.app_name = app_name
        self.cpu_requested = cpu_requested
        self.ram_requested = ram_requested
        self.disk_requested = disk_requested
        self.network_requested = network_requested
        self.job_type = job_type
        self.region = region
        self.env = env
        self.hour = hour
        self.ts_feats = ts_feats

def build_ts_features(x):
    x0 = x[-1]
    x1 = x[-2] if len(x) > 1 else None
    x2 = x[-3] if len(x) > 2 else None
    x3 = x[-4] if len(x) > 3 else None
    x4 = x[-5] if len(x) > 4 else None
    
    res = [x0, x1, x2, x3, x4]
    windows = [10, 15, 20, 25, 30, 40, 50, 60]
    for i, window_min in enumerate(windows):
        if len(x) >= window_min:
            win_start = 5 if i == 0 else windows[i-1]
            res.append(np.mean(x[-window_min:-win_start]))
            res.append(np.median(x[-window_min:-win_start]))
        else:
            res.extend([None] * 2)
    
    return res