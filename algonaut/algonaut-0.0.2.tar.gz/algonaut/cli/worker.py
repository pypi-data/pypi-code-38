import subprocess
import click
import re
import os
import tempfile

from algonaut.settings import settings


@click.group("worker")
def worker():
    """
    Worker-related functionality.
    """
    pass

@worker.command("run")
def run_worker():
    """
    Run the celery worker.
    """
    argv = [
        'worker',
        '--loglevel=INFO',
        '-B',
    ]
    settings.celery.worker_main(argv)

@worker.command("initialize-rabbitmq")
def initialize_rabbitmq():
    """
    Initializes the local RabbitMQ node. This only works for a locally running
    RabbitMQ instance.
    """
    script = """#!/bin/bash
    #reset all currently active tasks
    rabbitmqctl stop_app
    rabbitmqctl reset
    rabbitmqctl start_app

    #set the time-to-live policy of the messages
    rabbitmqctl set_policy TTL ".*" '{{"message-ttl":1200000}}' --apply-to queues
    #delete the guest user
    rabbitmqctl delete_user guest
    #create virtualhost algonaut
    rabbitmqctl add_vhost {vhost}
    #create user
    rabbitmqctl add_user {user} {password}
    #grant all permission to user on virtualhost
    rabbitmqctl set_permissions -p {vhost} {user} ".*" ".*" ".*"
    echo "Done"
"""
    broker_url = settings.get('worker.config.broker_url', '')
    match = re.match(r"^amqp://([\w\d\-]+):([\w\d\-]+)@([\w\d\.\-]+):(\d+)/([\w\d\-]+)$", broker_url)
    if not match:
        print("Invalid Broker URL!")
        exit(-1)
    user, password, hostname, port, vhost = match.groups()
    if hostname not in ("localhost", "127.0.0.1"):
        print("This script only works for a locally installed RabbitMQ instance")
        exit(0)
    file, filename = tempfile.mkstemp(suffix='.sh')
    os.write(file, script.format(vhost=vhost, user=user, password=password).encode("utf-8"))
    os.close(file)
    os.chmod(filename, 700)
    p = subprocess.Popen([filename])
    p.wait()
