import re, os
from time import sleep
import subprocess


def add_wifi(ssid, psw):
    MyOut2 = subprocess.Popen(['sudo', 'killall', 'dhclient'])
    print('scripts.py : add_wifi start')
    print('scripts.py : copying wpa_supplicant.conf')
    MyOut = subprocess.Popen(['sudo', 'cp', '/usr/local/lib/python3.5/dist-packages/zumidashboard/wpa_supplicant.conf',
                                '/etc/wpa_supplicant/wpa_supplicant.conf'])
    MyOut.wait()
    print('scripts.py : copyed wpa_supplicant.conf')

    if len(psw) == 0:
        print('no password')
        fa = open("/etc/wpa_supplicant/wpa_supplicant.conf", "a")
        fa.write("\nnetwork={")
        fa.write("\nssid=\"" + ssid + "\"")
        fa.write("\nkey_mgmt=NONE")
        fa.write("\n}")
        fa.close()

    else:
        MyOut2 = subprocess.Popen(['wpa_passphrase', ssid, psw],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
        stdout,stderr = MyOut2.communicate()
        raw_psk = str(stdout[-67:][:-3], 'utf-8')
        wpa_psk = "\npsk="+raw_psk
        print(stderr)
        if len(stdout) == 0:
            pass

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as f:
           f.write("\nnetwork={")
           f.write("\nssid=\"" + ssid + "\"")
           f.write(wpa_psk)
           f.write("\nid_str=\"AP1\"")
           f.write("\npriority=100")
           f.write("\n}")
           f.close()
    print('added wifi information to wpa_supplicant')
    sleep(3)
    print('force all rogue wpa_supplicant ...')

    print('kill all wpa_supplicant')
    MyOut2 = subprocess.Popen(['sudo', 'killall', 'wpa_supplicant'])
    MyOut2.wait()
    print('finish kill all wpa_supplicant')

    print('spa_supplicant setup')
    MyOut2 = subprocess.Popen(['sudo', 'wpa_supplicant','-B', '-iwlan0', '-c/etc/wpa_supplicant/wpa_supplicant.conf'])
    #sudo wpa_supplicant -B -iwlan0 -c/etc/wpa_supplicant/wpa_supplicant.conf

    MyOut2.wait()
    print('wpa_supplicant finished')

    print('dhclient start')
    MyOut3 = subprocess.Popen(['sudo', 'dhclient',  'wlan0'])
    sleep(4)
    print('dhclient end')
    os.popen('sudo echo "nameserver 8.8.8.8">/etc/resolv.conf') 
    print('getting an ip address')
    print('scripts.py : add_wifi end')


def OSinfo(runthis):
    try:
        osstdout = subprocess.check_call(runthis.split())
    except (subprocess.CalledProcessError) as err:
        return 1
    return osstdout


def check_wifi():
    print('scripts.py : check_wifi start')
    ssid = os.popen("sudo iwconfig wlan0 \
                    | grep 'ESSID' \
                    | awk '{print $4}' \
                    | awk -F\\\" '{print$2}'").read()
    print(ssid)

    if len(ssid) <= 1:
        MyOut2 = subprocess.Popen(['sudo', 'killall', 'dhclient'])

        return False, "None"
    return True, ssid
    print('scripts.py : check_wifi end')


def check_internet():
    #curl -m 12 --fail https://raw.githubusercontent.com/RobolinkInc/zumi-version/master/version.txt

    output = os.popen('curl -m 10 --fail https://raw.githubusercontent.com/RobolinkInc/zumi-version/master/version.txt').read()
    output = os.popen('curl -m 12 --fail https://raw.githubusercontent.com/RobolinkInc/zumi-version/master/version.txt').read() 

    print(output)
    print('check internet script method finish')
    return output

    #if output == 0:
    #    print('connected to internet')
    #    return True
    #else:
    #    print('internet not available')
    #    return False

def shutdown_ap():
    print('shutting down AP mode')
    subprocess.Popen(['sudo', 'ifdown', '--force', 'ap0'])

def get_ssid_list():
    MyOut = subprocess.Popen(['sudo', 'sh', os.path.dirname(os.path.abspath(__file__)) + '/shell_scripts/scan-ssid.sh', '.'],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT)
    stdout,stderr = MyOut.communicate()
    #print('getting ssid list')
    return stdout


def ap_connected_ip():
    result = os.popen("arp -a").read()
    result = re.findall("(192.168.10.[^)]*)", result)
    return result


def change_hostname(name):
    var = 0
    with open("/etc/hosts") as f:
        for num, line in enumerate(f, 0):
            if '127.0.1.1' in line:
                var = num
    with open("/etc/hosts", "r") as f:
        lines = f.readlines()
    with open("/etc/hosts", "w") as f:
        for i, line in enumerate(lines):
            if var != 0 and i == var:
                f.write("127.0.1.1       " + name + "\n")
            else:
                f.write(line)
    with open("/etc/hostname", "w") as f:
        f.write(name)


def reboot():
    subprocess.call(["sudo", "reboot", "now"])


def shutdown():
    subprocess.call(["sudo", "shutdown", "now"])


def change_ap_name(ssid, psw):
    ind = 0
    ind2 = 0
    with open("/etc/hostapd/hostapd.conf") as f:
        for num, line in enumerate(f, 0):
            if 'ssid=' in line:
                ind = num
            elif 'wpa_passphrase=' in line:
                ind2 = num
    with open("/etc/hostapd/hostapd.conf", "r") as f:
        lines = f.readlines()
    with open("/etc/hostapd/hostapd.conf", "w") as f:
        for i, line in enumerate(lines):
            if ind != 0 and i == ind:
                f.write("ssid=" + ssid + "\n")
            elif ind2 != 0 and i == ind2:
                f.write("wpa_passphrase=" + psw + "\n")
            else:
                f.write(line)


def is_device_connected():
    if ap_connected_ip().__len__() == 0:
        return False
    return True



def show_wifi_screen(_screen):
    print("Wifi Mode")
    _screen.draw_text("you are on internet already", font_size=15)
    sleep(3)


if __name__=='__main__':
    print(check_wifi())
