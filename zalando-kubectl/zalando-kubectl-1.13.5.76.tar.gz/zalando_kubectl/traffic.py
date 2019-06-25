import json
import subprocess
import time
from datetime import datetime, timedelta

import clickclick
import dateutil.parser
import natsort

from zalando_kubectl.models.ingress import Ingress, RAW_WEIGHTS_ANNOTATION


def get_raw_backends(kubernetes_obj):
    """Return the names of all services of an ingress."""

    result = []
    default_backend = kubernetes_obj['spec'].get('backend')
    if default_backend:
        result.append(default_backend['serviceName'])

    rules = kubernetes_obj['spec'].get('rules', [])
    for rule in rules:
        for path in rule.get('http', {}).get('paths', []):
            for backend in path.values():
                result.append(backend['serviceName'])
    return frozenset(result)


def get_stackset_backends(kubectl, stack):
    """Returns all the stack names for a given stackset"""

    cmdline = kubectl.cmdline("get", "stacks", "-l", "stackset={}".format(stack), "-o", "json")
    try:
        data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode(
            "utf-8")
    except subprocess.CalledProcessError:
        return []
    result = json.loads(data)
    backends = [item['metadata']['name'] for item in result['items']]
    return backends


def stackset_managed(kubernetes_obj: dict) -> bool:
    if 'ownerReferences' in kubernetes_obj['metadata']:
        for ref in kubernetes_obj['metadata']['ownerReferences']:
            if ref['kind'] == 'StackSet':
                return True
    return False


def get_ingress(kubectl, ingress):
    """Fetch the backends weights from a Kubernetes Ingress using kubectl."""

    cmdline = kubectl.cmdline("get", "ingress", ingress, "-o", "json")

    data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    kubernetes_obj = json.loads(data)
    s_managed = stackset_managed(kubernetes_obj)
    if s_managed:
        stackset_backends = get_stackset_backends(kubectl, ingress)
    else:
        stackset_backends = []
    raw_backends = get_raw_backends(kubernetes_obj)
    return Ingress(json.loads(data), raw_backends=raw_backends, stackset_backends=stackset_backends,
                   stackset_managed=s_managed)


def natural_sorted(d):
    for key in natsort.natsorted(d.keys()):
        yield key, d[key]


def print_weights_table(ingress):
    """Print the backends and their weights in a user-friendly way."""
    if ingress.stackset_managed:
        columns = ["name", "desired", "actual"]
        rows = [
            {
                'name': backend,
                'actual': round(ingress.raw_weights.get(backend, 0.0), 1),
                'desired': round(weight, 1)
            } for backend, weight in natural_sorted(ingress.stackset_weights)
        ]
    else:
        columns = ['name', 'weight']
        rows = [
            {
                'name': backend,
                'weight': round(weight, 1)
            } for backend, weight in natural_sorted(ingress.raw_weights)
        ]
    clickclick.print_table(columns, rows)


def set_ingress_weights(kubectl, ingress, force):
    """Update the backend weights on a Kubernetes Ingress using kubectl."""

    cmdline = kubectl.cmdline("annotate", "ingress", ingress.name, "--overwrite")
    cmdline.append("{}={}".format(ingress.annotation, json.dumps(ingress.weights)))
    if ingress.stackset_managed and force:
        cmdline.append("{}={}".format(RAW_WEIGHTS_ANNOTATION, json.dumps(ingress.weights)))
    subprocess.run(cmdline, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def get_resource_events(kubectl, stackset, reason=""):
    """Get events (json) written to a given resource, given the resource name and optionally a reason"""
    if not reason:
        cmdline = kubectl.cmdline("get", "event", "--field-selector", "involvedObject.name={}".format(stackset),
                                  "-o", "json")
    else:
        cmdline = kubectl.cmdline("get", "event", "--field-selector", "involvedObject.name={}".format(stackset),
                                  "--field-selector", "reason={}".format(reason), "-o", "json")
    data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    if data:
        json_data = json.loads(data)
        return json_data.get("items", [])
    return []


def get_recent_events(events, age: timedelta):
    """Get events with lastTimestamp =< age"""
    recent_events = []
    for event in events:
        last_timestamp = event.get("lastTimestamp", "")
        five_minutes_ago = datetime.utcnow() - age

        datetime_obj = dateutil.parser.parse(last_timestamp).replace(tzinfo=None)
        if datetime_obj >= five_minutes_ago:
            recent_events.append(event)

    return recent_events


def get_traffic_warning(traffic_events):
    """returns the message from the latest 'TrafficNotSwitched' event"""

    def last_timestamp(event):
        timestamp = event.get("lastTimestamp", "")
        datetime_obj = dateutil.parser.parse(timestamp).replace(tzinfo=None)
        return datetime_obj

    # Only consider the latest message since the others are redundant
    traffic_events.sort(key=last_timestamp)
    if len(traffic_events) >= 1:
        message = traffic_events[-1].get("message", "")
        return message
    else:
        return ""


def print_traffic_status(kubectl, ingress_name, backend, weight, timeout):
    """Print the traffic table and the TrafficNotSwitched until traffic is switched or timeout."""
    old_actual_weights = {}
    old_desired_weights = {}
    deadline = time.time() + timeout  # 10 minutes from now
    events_since = timedelta(minutes=2)
    traffic_warning = ""
    while True:
        # respect the timeout
        if time.time() > deadline:
            clickclick.secho("Timed out: traffic switching took too long", fg='red')
            break

        ingress = get_ingress(kubectl, ingress_name)
        reason = "TrafficNotSwitched"
        events = get_resource_events(kubectl, ingress_name, reason)
        recent_events = get_recent_events(events, events_since)
        # to reduce noise, only print the traffic table when weights change
        # or when a new event gets published
        if old_actual_weights != ingress.raw_weights or old_desired_weights != ingress.stackset_weights \
                or traffic_warning != get_traffic_warning(recent_events):

            # Update the warning if it changed
            traffic_warning = get_traffic_warning(recent_events)
            print_weights_table(ingress)

            # save weights for the next iteration
            old_actual_weights = ingress.raw_weights
            old_desired_weights = ingress.stackset_weights

            # quit if the desired weight has been met
            if old_actual_weights.get(backend, 0.0) == weight:
                break

            # print the traffic switch events every because new events might get
            # aggregated with old ones
            clickclick.secho(traffic_warning, fg='yellow', bold=True)

        # to reduce noise, wait till the next iteration
        time.sleep(2)
