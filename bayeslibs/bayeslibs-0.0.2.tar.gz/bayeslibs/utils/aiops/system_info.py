"""
@project:medical_robot_backend
@language:python3
@create:2019/4/26
@author:qianyang@aibayes.com
@description:none
"""
import pywifi

wifi = pywifi.PyWiFi()
iface = wifi.interfaces()[1]
print(iface.colors())
iface.scan()
result = iface.scan_results()
print(iface.name())

MIN_WIFI_RSSI = -100
MAX_WIFI_RSSI = -55
wifi_rssi_dict = dict()

for i in range(len(result)):
    if result[i].bssid == '9c:a6:15:9f:3d:4c':
        print(result[i].ssid, result[i].bssid, result[i].signal)
    if result[i].signal > MAX_WIFI_RSSI:
        rssi_label = 4
    elif result[i].signal < MIN_WIFI_RSSI:
        rssi_label = 0
    else:
        rssi_label = round(4 * (result[i].signal + 100) / 45)
    wifi_rssi_dict['{0}-{1}'.format(result[i].ssid, result[i].bssid)] = rssi_label
print(wifi_rssi_dict)
