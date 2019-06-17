"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import numpy as np
import scipy.io as sio
import json



def run_conversion_request(ses, conversion_request):
    config_name = conversion_request['config_name']
    command_id = conversion_request['command_id']
    print(command_id)
    temp_matlab_payload = conversion_request['waveform'] #retrieves list of lists
    matlab_payload = []
    for item in temp_matlab_payload:
        item = tuple(item)
        matlab_payload.append(item) #converts list of lists to list of tuples
    z = np.asarray(matlab_payload) #converts list of tuples to numpy array
    sio.savemat('temp.mat', {"temp":z}) #saves as matlab file
    d = open('temp.mat', 'rb').read()
    url_m = ("https://" + DOMAIN + "/matlab/" + str(command_id))
    headers = {'Content-Type': 'application/octet-stream'}
    result = ses.post(url_m, data = d, headers = headers)
    print("reason", result.reason)
    print("code", result.status_code)
    url_c = ("https://" + DOMAIN + "/matlab_complete/" +
             COMPANY_NAME + "/" + config_name + "/" + str(command_id))
    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    c = {'command':'instruments_conversion'}
    json_data = json.dumps(c, ensure_ascii=True)
    result = ses.post(url_c, data = json_data, headers = headers)
    print("reason", result.reason)
    print("code", result.status_code)
