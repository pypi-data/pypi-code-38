import paramiko
import time
import os
import subprocess
import telnetlib
import smtplib
import bs4
import requests
import json
import sys
from pyVim.connect import SmartConnectNoSSL
from pyVmomi import vim
from pyVim import *

def FindVMIP(IP, usern, passw, vIP="10.160.111.161"):

    def find_IP(virtual_machine, IPLook):

        summary = virtual_machine.summary
        for nic in virtual_machine.guest.net:

            if nic.ipConfig is not None:
                addresses = nic.ipConfig.ipAddress

                for adr in addresses:
                    #print(adr.ipAddress)
                    if IPLook == adr.ipAddress:
                        print("IP being used by: " + summary.config.name)
        return

    c = SmartConnectNoSSL(host=vIP, user=usern, pwd=passwd)

    content = c.RetrieveContent()
    container = content.rootFolder
    viewType = [vim.VirtualMachine]
    recursive = True
    containerView = content.viewManager.CreateContainerView(
                container, viewType, recursive)
    children = containerView.view

    for child in children:
        find_IP(child, IP)

def RESTGet(url, usern="", passw="", devicetype=""):

    import requests
    import sys
    import json

    authskip = False
    if devicetype.lower() == "dell":
        usern = "root"
        passw = "calvin"
    elif devicetype.lower() == "quanta":
        usern = "admin"
        passw = "cmb9.admin"

    if usern == "" and passw == "":
        authskip = True

    requests.packages.urllib3.disable_warnings()
    try:
        if not authskip:
            response = requests.get(url, verify=False, auth=(usern, passw))
        else:
            response = requests.get(url, verify=False)  

        JSONparsed = json.loads(response.text)
        JSONPrettyOutput = json.dumps(JSONparsed, indent=4, sort_keys=True)
        return JSONparsed, JSONPrettyOutput
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

def RESTPost(url, body, usern="", passw="", devicetype=""):

    import requests
    import sys
    import json

    authskip = False
    if devicetype.lower() == "dell":
        usern = "root"
        passw = "calvin"
    elif devicetype.lower() == "quanta":
        usern = "admin"
        passw = "cmb9.admin"

    if usern == "" and passw == "":
        authskip = True

    headers = {
        'Content-Type': "application/json",
        'Cache-Control': "no-cache",
        'Postman-Token': "119935c1-644c-419e-897a-be07c62f74bf"
        }

    requests.packages.urllib3.disable_warnings() #pylint: disable=E1101
    try:
        if not authskip:
            response = requests.post(url, headers=headers, json=body, verify=False, auth=(usern, passw))
        else:
            response = requests.post(url, headers=headers, json=body, verify=False)

        
        JSONparsed = json.loads(response.text)
        JSONPrettyOutput = json.dumps(JSONparsed, indent=4, sort_keys=True)
        return JSONparsed, JSONPrettyOutput
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)

def CMD(phrase):

    phrase = phrase.split(" ")
    output = subprocess.check_output(phrase)
    return output

def email(to, from_field, subject, message, IP="10.160.111.36"):

    subject = subject + "\r\n"
    message = 'Subject: {}\n\n{}'.format(subject, message)
    msg = ("From: " + from_field + "\r\nTo: " + ", ".join(to) + "\r\n" )
    msg = msg + message

    server = smtplib.SMTP(IP, "25")
    server.sendmail(from_field, to, msg)
    server.quit()

def ping(hostname, n=3):
    output = subprocess.run(["ping", hostname, "-n", str(n)], stdout=subprocess.PIPE)
    result = output.stdout.decode()

    #and then check the response...
    if 'Reply from ' + hostname + ': bytes=' in result:
        return True
    elif hostname.count('.') != 3:
        if ': bytes=' in result and 'Reply from ' in result:
            return True
    else:
        return False

def ZipToZone(zip, msgbox=False):

    import requests
    zip = str(zip)
    try:
        req = requests.get('http://www.zip-info.com/cgi-local/zipsrch.exe?tz=tz&zip=' + zip +'&Go=Go')
        req.raise_for_status()
        ZipObj = bs4.BeautifulSoup(req.text, "lxml")

        if "PST" in ZipObj.encode('ascii').decode():
            return("Pacific")
        elif "MST" in ZipObj.encode('ascii').decode():
            return("Mountain")
        elif "CST" in ZipObj.encode('ascii').decode():
            return("Central")
        elif "EST" in ZipObj.encode('ascii').decode():
            return("Eastern")

    except:
        try:
            if msgbox == True:
                messagebox.showerror("Error", "Couldn't pull the time zone, please make sure you're connected to the internet and try again.")
        except:
            print("Couldn't pull the time zone, please make sure you're connected to the internet and try again.")
            return
    return

def eprint(Sentence):

    SentLeng = len(Sentence)
    print("="* SentLeng *3)
    print(("=" * SentLeng) + Sentence + ("=" * SentLeng))
    print("="* SentLeng *3)

    return

def ssh_connect(device_ip, username, password, screenprint=False):
    if screenprint:
        print("Connecting to: " + device_ip)

    hostname = device_ip
    port = 22

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    channel = client.invoke_shell()

    if screenprint:
        print("Successfully connected to: " + device_ip)

    return client, channel

def psend(command, channel):

    channel.send(command)

def pwait(waitstr, channel, tout=0, screenprint=False):
    startTime = int(time.time())
    stroutput = ''
    while waitstr not in stroutput:
        currentTime = int(time.time())
        if channel.recv_ready():
            try:
                current = channel.recv(9999).decode()
                stroutput += current
                if current.strip() != '':
                    if screenprint:
                        print(current, end='')
            except:
                continue

        if tout != 0:
            if (currentTime - startTime) > tout:
                try:
                    if current.strip() != '':
                        if screenprint:
                            print(current, end='')
                except:
                    pass
                return stroutput

    return stroutput

def twait(phrase, tn, tout = -1, logging = 'off', rcontent = False, screenprint = False):

    # Adding code to allow lists for phrase
    finalcontent = ' '

    #This is the time of the epoch
    startTime = int(time.time())
    while True:
        # This is the current time
        currentTime = int(time.time())
        if tout != -1:

            # This is the time since the start of this loop
            # if it exceeds the timeout value passed to it
            # then exit with a return of 0
            if (currentTime - startTime) > tout:
                if logging == 'on':
                    #Adding the -e-e-> to differentiate from device output
                    if screenprint:
                        print('-e-e->It has been ' + str(tout) +  ' seconds. Timeout!')
                if rcontent == False:
                    return 0
                else:
                    return 0, finalcontent
        # Eager reading back from the device
        content = (tn.read_very_eager().decode().strip())

        if content.strip() != '':
            finalcontent += content
        # if the returned content isn't blank. This stops
        # it from spamming new line characters
        if content.strip() != '':
            if screenprint:
                print (content, end='')
        # content was found! Return a 1 for success
        if type(phrase) is str:
            if phrase in content:
                if rcontent == False:
                    return 1
                else:
                    return 1, finalcontent

        if type(phrase) is list:

            count = 1
            for p in phrase:
                if p in content:
                    if rcontent == False:
                        return count
                    else:
                        return count, finalcontent
                count+=1

def wait(phrase, con, tout = -1, logging = 'off', rcontent = False, screenprint = False):

    whatami = ''
    try:
        con.get_id()
        whatami = 'ssh'
    except:
        try:
            con.get_socket()
            whatami = 'telnet'
        except:
            print("Could not determine if telnet or ssh")
    # Adding code to allow lists for phrase
    finalcontent = ' '

    #This is the time of the epoch
    startTime = int(time.time())
    while True:
        # This is the current time
        currentTime = int(time.time())
        if tout != -1:

            # This is the time since the start of this loop
            # if it exceeds the timeout value passed to it
            # then exit with a return of 0
            if (currentTime - startTime) > tout:
                if logging == 'on':
                    #Adding the -e-e-> to differentiate from device output
                    if screenprint:
                        print('-e-e->It has been ' + str(tout) +  ' seconds. Timeout!')
                if rcontent == False:
                    return 0
                else:
                    return 0, finalcontent

        if whatami == 'telnet':
            # Eager reading back from the device
            content = (con.read_very_eager().decode().strip())
        elif whatami == 'ssh':
            content = con.recv(99999).decode()

        if content.strip() != '':
            finalcontent += content
        # if the returned content isn't blank. This stops
        # it from spamming new line characters
        if content.strip() != '':
            if screenprint:
                print (content, end='')
        # content was found! Return a 1 for success
        if type(phrase) is str:
            if phrase in content:
                if rcontent == False:
                    return 1
                else:
                    return 1, finalcontent

        if type(phrase) is list:

            count = 1
            for p in phrase:
                if p in content:
                    if rcontent == False:
                        return count
                    else:
                        return count, finalcontent
                count+=1

def send(phrase, con):

    whatami = ''
    try:
        con.get_id()
        whatami = 'ssh'
    except:
        try:
            con.get_socket()
            whatami = 'telnet'
        except:
            print("Could not determine if telnet or ssh")


    if whatami == 'ssh':
        con.send(phrase)
    elif whatami == 'telnet':
        con.write(phrase.encode())



def tsend(phrase, tn):

    #Sends the phrase that was passed to it as bytes
    tn.write(phrase.encode())

    return

def shortfiles(parentdir, extensions=[]):
    TotalFiles = []
    if extensions == []:
        for root, directories, filenames in os.walk(parentdir):
            for filename in filenames:
                TotalFiles.append(filename)

    elif extensions != []:
        for root, directories, filenames in os.walk(parentdir):
            for filename in filenames:
                for ext in extensions:
                    if ext in filename:
                        TotalFiles.append(filename)

    return TotalFiles

def longfiles(parentdir, extensions=[]):
    TotalFiles = []
    if extensions == []:
        for root, directories, filenames in os.walk(parentdir):
            for filename in filenames:
                TotalFiles.append(os.path.join(root, filename))

    elif extensions != []:
        for root, directories, filenames in os.walk(parentdir):
            for filename in filenames:
                for ext in extensions:
                    if ext in os.path.join(root, filename):
                        TotalFiles.append(os.path.join(root, filename))

    return TotalFiles