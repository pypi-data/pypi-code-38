#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import socket
import subprocess
import time
import traceback
from socket import gethostname

from OpenSSL import crypto

from Homevee.Helper import Logger
from Homevee.Helper.HomeveeCloud import HomeveeCloudWrapper
from Homevee.Item.User import User
from Homevee.Utils import Constants
from Homevee.Utils.Database import Database


def save_request_to_db(data, reply, db: Database = None):
    if db is None:
        db = Database()
    return
    if 'password' in data:
        del data['password']

    if data['action'] == "arcontrol":
        del data['imagedata']

        db.insert("INSERT INTO REQUEST_DATA (RESPONSE) VALUES (:response)",
            {'response': reply})

        request_id = cur.lastrowid

        for key in list(data.keys()):
            db.insert("INSERT INTO REQUEST_DATA_PARAMS (REQUEST_ID, PARAM_KEY, PARAM_VALUE) VALUES(:id, :key, :value)",
                {'id': request_id, 'key': key, 'value': data[key]})

        return True

def send_to_client(data, conn, is_http):
    if not is_http:
        Logger.log(("Sent Response: "+data))
    elif is_http:
        data = 'HTTP/1.1 200 OK\nContent-Type: text/html\n'+data+'\n'
        Logger.log(("Sent HTTP-Response: "+data))

    #Prüfen, ob alle Daten gesendet wurden
    len_send = conn.send(bytearray(str.encode(data)))
    #len_send = conn.send(compressed_data)
    Logger.log(("Data: "+str(len(data))+" | Sent: "+str(len_send)))

    #if(len_send is 0):
    #    send_to_client(json.dumps({'status': 'error'}), conn, is_http)

def verify_user(username, password):
    db = Database()

    user = User.load_username_from_db(username, db)

    return user.verify(password)

def update_ip_thread():
    last_ip = None

    db = Database()

    while(True):
        remote_id = db.get_server_data("REMOTE_ID")
        access_token = db.get_server_data("REMOTE_ACCESS_TOKEN")
        my_ip = get_my_ip()

        if my_ip != last_ip or my_ip != get_my_ip_from_cloud(remote_id):
            try:
                update_ip(my_ip, remote_id, access_token)
            except:
                pass

        last_ip = my_ip

        #wait some time
        time.sleep(5*60) #5 Minuten

def update_cert_thread():
    db = Database()

    while (True):
        remote_id = db.get_server_data("REMOTE_ID")
        access_token = db.get_server_data("REMOTE_ACCESS_TOKEN")

        # generate_cert

        check_cert(None, remote_id, access_token)

        # wait some time
        time.sleep(12 *60 * 60)  # 12 Stunden

def check_cert(db=None, remote_id=None, access_token=None):
    cert_data = get_local_cert()

    if db is not None:
        remote_id = db.get_server_data("REMOTE_ID")
        access_token = db.get_server_data("REMOTE_ACCESS_TOKEN")

    if cert_data is None:
        generate_cert()

    if cert_data is not None and cert_data != get_my_cert_from_cloud(remote_id):
        update_cert(cert_data, remote_id, access_token)

def update_ip(ip, remote_id, access_token):

    MAX_RETRIES = 10
    retries = 0

    contents = None

    # update local ip in cloud
    homevee_cloud = HomeveeCloudWrapper(remote_id, access_token)
    homevee_cloud.set_cert(ip)
    '''
    try:
        url = "https://cloud.homevee.de/server-api.php?action=updatelocalip&remoteid=" + remote_id + "&accesstoken=" + access_token + "&localip=" + ip
        #Logger.log(remote_id+" - "+access_token+" - "+ip)
        while (contents != "ok" and retries < MAX_RETRIES):
            try:
                contents = urllib.request.urlopen(url).read()
                return True
            except:
                #if(Logger.IS_DEBUG):
                traceback.print_exc()
                Logger.log(translations.translate("no_cloud_connection"))
            retries += 1
        return False
    except:
        return False
    '''

def update_cert(cert_data, remote_id, access_token):
    Logger.log("updating local cert...")

    cert_data = cert_data.replace("\n", "")
    cert_data = cert_data.replace("-----BEGIN CERTIFICATE-----", "")
    cert_data = cert_data.replace("-----END CERTIFICATE-----", "")

    MAX_RETRIES = 10
    retries = 0
    contents = None

    #print(remote_id, access_token, cert_data)

    # update cert in cloud
    try:
        homevee_cloud = HomeveeCloudWrapper(remote_id, access_token)
        homevee_cloud.set_cert(cert_data)
    except:
        Logger.log("Could not update local cert...")

    '''
    try:
        url = "https://cloud.homevee.de/server-api.php?action=updatecert&remoteid=" + remote_id + "&accesstoken=" + access_token + "&cert=" + urllib.parse.quote(
        cert_data)
        #print(url)

        while (contents != "ok" and retries < MAX_RETRIES):
            try:
                contents = urllib.request.urlopen(url).read()
                Logger.log(contents)
                return True
            except:
                if(Logger.IS_DEBUG):
                    traceback.print_exc()
            retries += 1
        return False
    except:
        return False
    '''

def get_my_ip():
    if Database().get_server_data("REMOTE_ID") == "VX6FLAYZN":
        return "192.168.2.130"

    try:
        cmd = "hostname -i"
        data = subprocess.check_output(cmd, shell=True).decode('utf-8')
        ip, mac = data.split(" ")
    except:
        if(Logger.IS_DEBUG):
                traceback.print_exc()
        ip = socket.gethostbyname(socket.gethostname())

    Logger.log("my ip address: " + ip)

    return ip

def generate_cert():
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "DE"
    cert.get_subject().ST = "Germany"
    cert.get_subject().L = "Germany"
    cert.get_subject().O = "Homevee"
    cert.get_subject().OU = "Homevee"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    open(Constants.LOCAL_SSL_CERT, "wt").write(
        crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))
    open(Constants.LOCAL_SSL_PRIVKEY, "wt").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode('utf-8'))

def get_local_cert():
    if(os.path.isfile(Constants.LOCAL_SSL_CERT)):
        file = open(Constants.LOCAL_SSL_CERT, "r")
        content = file.read()
        if content is not None and content != '':
            return content

    return None

def get_my_ip_from_cloud(remote_id):
    '''
    try:
        url = "http://cloud.homevee.de/server-api.php?action=getlocalip&remoteid="+remote_id
        #print(url)
        contents = urllib.request.urlopen(url).read()

        data = json.loads(contents)

        if 'ip' in data and data['ip'] is not None:
            return data['ip']
        else:
            return None
    except:
        if(Logger.IS_DEBUG):
                traceback.print_exc()
        return None
    '''
    homevee_cloud = HomeveeCloudWrapper(remote_id, Database().get_server_data("REMOTE_ACCESS_TOKEN"))
    try:
        return homevee_cloud.get_ip()
    except:
        return None

def get_my_cert_from_cloud(remote_id):
    '''
    try:
        url = "http://cloud.homevee.de/server-api.php?action=getcert&remoteid="+remote_id
        contents = urllib.request.urlopen(url).read()

        data = json.loads(contents)

        if 'cert' in data and data['cert'] is not None:
            return data['cert']
        else:
            return None
    except:
        if(Logger.IS_DEBUG):
            traceback.print_exc()
        return None
    '''
    homevee_cloud = HomeveeCloudWrapper(remote_id, Database().get_server_data("REMOTE_ACCESS_TOKEN"))
    try:
        return homevee_cloud.get_cert()
    except:
        return None
