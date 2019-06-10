import time
import uuid
from argparse import ArgumentParser

from tqdm import tqdm
from termcolor import colored
from mk8sconfig.ssh_connection import SSHConnect

__version__ = "0.0.6"

user = ""
password = ""
host = ""


def get_cert_password(connection):
    out = connection.exec("ls -la | grep .ssl_certs_password")
    if len(out) == 0:
        hash = str(uuid.uuid4()).replace("-", "")
        connection.exec(" echo '" + hash + "' >> .ssl_certs_password")
    out = connection.exec("cat .ssl_certs_password")
    return out


def main():
    parser = ArgumentParser(
        prog="mk8sconfig.py",
        description='tool for configure microk8s on ubuntu VPS over SSH \
            distribution for can be installed with pip. app version: ' + __version__

    )
    parser.add_argument("-u", "--user", dest="user", help="ssh user", metavar="USERNAME", default="root", required=True)
    parser.add_argument("-p", "--pass", dest="password", help="ssh password", metavar="PASSWORD", default="", required=True)
    parser.add_argument("-i", "--host", dest="host", help="server host", metavar="HOST", default="", required=True)
    parser.add_argument("-P", "--port", dest="port", help="ssh port", metavar="PORT", default=22, type=int)
    parser.add_argument("-d", "--domain", dest="domain", help="domain name", metavar="DOMAIN_NAME", default="")

    args = parser.parse_args()

    user:str = args.user
    password = args.password
    host = args.host
    port = args.port
    _domain = args.domain if len(args.domain) > 0 else args.host
    connection = None
    try:
        connection= SSHConnect(user, password, host, port=port)
    except Exception as err:
        print("Error in connection....")
        exit(1)

    if user.lower() != "root":
        # TODO: logic for sudo group user's
        print("This version only support root user")
        exit(1)
    # ---------- #
    # update system
    connection.exec('source  .bashrc')
    print(colored("update ubuntu ....", "green", attrs=['bold']))
    out = connection.exec("apt update")
    print(out.split("\n")[-2])

    # ---------- #
    # install snap microk8s
    print(colored("install microk8s ....", "green", attrs=['bold']))
    out = connection.exec("snap install microk8s --classic --channel=1.14/stable")
    out = "installed. " if out.find("installed") > 0 else "Not installed"
    print(out)
    print(colored("install helm ....", "green", attrs=['bold']))
    out = connection.exec("snap install helm --classic")
    out = "installed. " if out.find("installed") > 0 else "Not installed"
    print(out)
    connection.exec("snap alias microk8s.kubectl kubectl")

    # ---------- #
    # start microk8s
    print(colored("init microk8s ....", "green", attrs=['bold']))
    out = connection.exec("microk8s.start")
    if out.find("command not found") > 0:
        print(colored(" - adding snap to path", "blue"))
        out = connection.exec("cat .bashrc | grep /snap/bin")
        if len(out) == 0:
            connection.exec('echo "export PATH=/snap/bin:$PATH" >> ~/.bashrc')
            connection.exec('echo "alias kubectl=microk8s.kubectl" >> ~/.bashrc')
            connection.exec('echo "alias k=microk8s.kubectl" >> ~/.bashrc')
            connection.exec('echo "alias docker=microk8s.docker" >> ~/.bashrc')
            connection.exec('source .bashrc')
            print("   done")
        else:
            print("   already added into PATH")
        print(colored(" - start service", "blue"))
        out = connection.exec("/snap/bin/microk8s.start")
        print("  ", out.rstrip())
        out = connection.exec("ls -la | grep .flag_reset")
        if len(out) == 0:
            out = connection.exec("/snap/bin/microk8s.reset")
            print("  ", out.split("\n")[-2])
            connection.exec("touch .flag_reset")

    # ---------- #
    # enabled docker registry
    print(colored(" - enable plugins registry", "blue"))
    out = connection.exec("/snap/bin/microk8s.enable registry")
    print("  ", out.split("\n")[-2])
    print(colored(" - enable plugins dns", "blue"))
    out = connection.exec("/snap/bin/microk8s.enable dns")
    print("  ", out.split("\n")[-2])
    print(colored(" - enable plugins dashbaord", "blue"))
    out = connection.exec("/snap/bin/microk8s.enable dashboard")
    print("  ", out.split("\n")[-2])

    # ---------- #
    # enabled docker registry for external push
    print(colored("configure docker for external connections", "green", attrs=['bold']))

    # create ssh certs
    # TODO: solved error EOF in docker registry
    """
    print(colored(" - Generating SSL for docker registry", "blue"))
    certs_password = get_cert_password(connection)
    print(colored("   Downloading script for generate certs", "yellow"), out.strip())
    out = connection.exec(
        "wget https://raw.githubusercontent.com/kekru/linux-utils/master/cert-generate/create-certs.sh")
    print(out)
    print(colored("   chmod +x create-certs.sh", "yellow"), out.strip())
    connection.exec("chmod +x create-certs.sh")
    print(colored("   1.creating CA ", "yellow"), out.strip())
    out = connection.exec("./create-certs.sh -m ca -pw " + certs_password + " -t certs -e 900")
    print(out)
    print(colored("   2.Creating server certificate and key with the password", "yellow"), out.strip())
    out = connection.exec(
        "./create-certs.sh -m server -h " + _domain + " -pw " + certs_password + " -t certs -e 365 " + certs_password + " -t certs -e 900")
    print(out)
    print(colored("   3.Create client certificate and key with the password of step 1", "yellow"), out.strip())
    # out = connection.exec("./create-certs.sh -m client -h testClient -pw "+certs_password+" -t certs -e 365")
    # print(out)
    """
    # creating docker daemon config
    print(colored(" - writing new docker-daemon.json", "blue"))
    file = " /var/snap/microk8s/current/args/docker-daemon.json"
    home_folder = connection.exec("echo $HOME").rstrip()
    connection.exec("echo "" > " + file)
    connection.exec('echo    "{" >> ' + file)

    # TODO: solved error EOF in docker registry
    """
    connection.exec('echo   \'   "hosts": ["unix:///var/snap/microk8s/current/docker.sock", "tcp://0.0.0.0:2376"], \' >> ' + file)
    connection.exec('echo   \'  "tls": true, \' >> ' + file)
    connection.exec('echo   \'  "tlscacert": "'+home_folder+'/ca.pem", \' >> ' + file)
    connection.exec('echo   \'  "tlscert": "' + home_folder + '/server-cert.pem", \' >> ' + file)
    connection.exec('echo   \'  "tlskey": "' + home_folder + '/server-key.pem", \' >> ' + file)
    connection.exec('echo   \'  "tlsverify": true, \' >> ' + file)
    """
    connection.exec('echo   \'  "debug" : true, \' >> ' + file)
    connection.exec('echo   \'  "insecure-registries" : ["localhost:32000","' + _domain + ':32000"],\' >> ' + file)
    connection.exec(
        'echo   \'  "allow-nondistributable-artifacts" : ["localhost:32000","' + _domain + ':32000"],\' >> ' + file)
    connection.exec('echo   \'  "disable-legacy-registry": true \' >> ' + file)
    connection.exec('echo    "}" >> ' + file)
    print("   Done")
    # restart docker daemon
    print(colored(" - restart docker systemctl service", "blue"))
    out = connection.exec("sudo systemctl restart snap.microk8s.daemon-docker.service")
    print("   Done" if len(out) == 0 else "Error : ", out)
    # print(out)

    print(colored("PROCESS DONE", "green", attrs=['bold']))





if __name__ == "__main__":
    main()
