import socket

def add_host_alias(app, host, domain='syncloud.info', hosts_file='/etc/hosts'):
    ip = socket.gethostbyname(host)
    with open(hosts_file, "a") as hosts:
        hosts.write("{0} {1}.{2}\n".format(ip, host, domain))
        hosts.write("{0} {1}.{2}.{3}\n".format(ip, app, host, domain))
