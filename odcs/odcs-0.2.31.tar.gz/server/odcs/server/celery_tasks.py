# -*- coding: utf-8 -*-
# Copyright (c) 2019  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import ssl
import os
from celery import Celery
from six.moves.urllib.parse import urlparse

from odcs.server import conf, db
from odcs.server.backend import (
    generate_compose as backend_generate_compose,
    ComposerThread,
    RemoveExpiredComposesThread)
from odcs.server.utils import retry
from odcs.server.models import Compose, COMPOSE_STATES


# Prepare the instances of classes with worker methods.
composer_thread = ComposerThread()
remove_expired_compose_thread = RemoveExpiredComposesThread()


# Create the Celery app.
if os.environ.get("ODCS_CELERY_BROKER_URL"):
    broker_url = os.environ["ODCS_CELERY_BROKER_URL"]
elif conf.celery_broker_url:
    broker_url = conf.celery_broker_url
else:
    broker_url = "amqp://localhost"

# Although the Celery handles amqps using Kombu Python module,
# it does not do that correctly.
#
# When using "amqps://" protocol, Kombu uses SSLTransport which effectively
# sets the `amqp.Connection.ssl = True`. This enables SSL, but it does it
# in a way when we cannot set any other SSL options like client cert/key
# or for example SNI hostname which needs to be used.
#
# This is done in this commit:
# In the https://github.com/celery/kombu/commit/701672c2ba732883869a42f061a10dbfc8fe2f30
#
# To workaround this, we detect "amqps" here and sets the `broker_use_ssl`. This
# allows us to set any SSL options like client cert/key or SNI header.
# The `broker_use_ssl` is directly passed to `amqp.Connection.ssl` which handles
# it.
#
# In the end, we change the `broker_url` protocol from "amqps" to "amqp", so
# the Celery wont' override the `amps.Connection.ssl` with `True`.
if broker_url.startswith("amqps://"):
    netloc = urlparse(broker_url).netloc
    host_port = netloc.split("@")[-1]
    host = host_port.split(":")[0]

    ssl_ctx = {}

    broker_use_ssl = {
        "server_hostname": host,
        "context": {"purpose": ssl.Purpose.SERVER_AUTH},
    }
    conf.celery_config.update({"broker_use_ssl": broker_use_ssl})
    broker_url = broker_url.replace("amqps://", "amqp://")

celery_app = Celery("backend", broker=broker_url)
celery_app.conf.update(conf.celery_config)
celery_app.conf.update({
    'task_routes': ('odcs.server.celery_tasks.TaskRouter')
})


class TaskRouter:
    """ Custom Celery router """

    def __init__(self):
        self.config = conf.celery_router_config

    def route_for_task(self, task_name, *args, **kwargs):
        """
        Method which celery expects to be defined on a custom router. Returns the payload
        with the queue selected for task
        """
        if task_name == self.config["cleanup_task"]:
            return {"queue": conf.celery_cleanup_queue}

        compose_id = args[0][0]
        compose = get_odcs_compose(compose_id)
        compose_md = compose.json()

        queue = self.__get_queue_for_compose(compose_md, task_name)

        return {"queue": queue}

    def __get_queue_for_compose(self, compose_md, task_name):
        """ Goes through routing rules configured for a task returns a queue on the first match. """
        rules = {}
        if self.config["routing_rules"].get(task_name):
            rules.update(self.config["routing_rules"][task_name])

        for queue, rule in rules.items():
            # if the rule has no properties its an automatic match.
            if rule:
                for key, value in rule.items():
                    if not compose_md.get(key):
                        raise ValueError(
                            ("Task Router: Routing rule for queue %s for task %s contains an "
                             "invalid property: %s") % (queue, task_name, key))

                    # if the value of the property from the rule and compose does not match, the
                    # whole rule is ignored and we go to the next rule
                    if type(value) is list:
                        if compose_md[key] not in value:
                            break
                    else:
                        if compose_md[key] != value:
                            break
                else:
                    # if all of the properties and values match then the whole rule match
                    return queue
            else:
                # if the rule is emtpy its an wildcard and an automatic match
                return queue

        # if none of the rules applies the default queue is returned
        return self.config["default_queue"]


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Add the cleanup task every 10 minutes. This can be hardcoded here.
    # It is just internal task to clean up the expired composes, mark
    # stuck composes as failed and so on.
    sender.add_periodic_task(10 * 60, run_cleanup.s())


@retry(wait_on=RuntimeError)
def get_odcs_compose(compose_id):
    """
    Gets the compose from ODCS DB.
    """
    compose = Compose.query.filter(Compose.id == compose_id).first()
    if not compose:
        raise RuntimeError("No compose with id %d in ODCS DB." % compose_id)
    return compose


def generate_compose(compose_id):
    """
    Generates the compose with id `compose_id`.
    """
    compose = get_odcs_compose(compose_id)
    compose.transition(COMPOSE_STATES["generating"], "Compose thread started")
    db.session.commit()
    backend_generate_compose(compose.id)


@celery_app.task
def generate_pungi_compose(compose_id):
    """
    Generates the Pungi based compose.
    """
    generate_compose(compose_id)


@celery_app.task
def generate_pulp_compose(compose_id):
    """
    Generates the Pungi based compose.
    """
    generate_compose(compose_id)


@celery_app.task
def run_cleanup():
    """
    Runs the cleanup.
    """
    remove_expired_compose_thread.do_work()
    composer_thread.fail_lost_generating_composes()
