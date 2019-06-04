import os
import logging
import subprocess
import re


def remote_network_by_id(network_id):
    p = subprocess.Popen('docker network rm ' + network_id, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        logging.error("Failed to remove docker network: %s", network_id)
        exit(1)


def remove_ambiguous_network(network_name):
    p = subprocess.Popen('docker network ls | grep ' + network_name, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        logging.error("Failed to get all docker network named: %s", network_name)
        exit(1)
    for line in stdout.decode().splitlines():
        network_id = line.split()[0]
        remote_network_by_id(network_id)


def docker_compose_down():
    p = subprocess.Popen('docker-compose down', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    r = p.returncode
    if r != 0:
        for line in stderr.decode().splitlines():
            m = re.search(r'(\d+) matches found based on name: network (.+) is ambiguous', line)
            if m is not None:
                network_name = m.group(2)
                remove_ambiguous_network(network_name)
                docker_compose_down()
            else:
                exit(1)


def main(network):
    if os.path.exists("docker-compose.yml"):
        logging.info("Clean up the {} environment".format(network))
        docker_compose_down()
