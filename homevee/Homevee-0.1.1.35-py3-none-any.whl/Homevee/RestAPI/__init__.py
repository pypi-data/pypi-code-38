#!flask/bin/python
from flask import Flask

from Homevee.Helper import Logger
from Homevee.Helper.helper_functions import get_my_ip
from Homevee.RestAPI.ProcessDataAPI import ProcessDataAPI

app = Flask("Homevee")

#def update_cert(file):
    #cert_data = open(file).read()
    #cert_data = cert_data.replace("\n", "")
    #cert_data = cert_data.replace("-----BEGIN CERTIFICATE-----", "")
    #cert_data = cert_data.replace("-----END CERTIFICATE-----", "")

    #Database().do_query("REPLACE INTO CLOUD_CERTS (IP, CERTIFICATE) VALUES (%s, %s)",
    #                    (args.ip, cert_data))

def start_rest_api():
    # HOST = "test-cloud.homevee.de"
    # CERT_FILE = "/etc/letsencrypt/live/" + HOST + "/cert.pem"
    # CHAIN_FILE = "/etc/letsencrypt/live/" + HOST + "/chain.pem"
    # FULLCHAIN_FILE = "/etc/letsencrypt/live/" + HOST + "/fullchain.pem"
    # KEY_FILE = "/etc/letsencrypt/live/" + HOST + "/privkey.pem"

    blueprints = [ProcessDataAPI]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    #app.run(host='0.0.0.0', port=8080, debug=True)

    my_ip = get_my_ip()

    Logger.log("Starting API on "+str(my_ip))

    app.run(threaded=True, host=my_ip, port=8080)
    # app.run(threaded=True, host=HOST, port=443, ssl_context=(FULLCHAIN_FILE, KEY_FILE))

if __name__ == '__main__':
    start_rest_api()