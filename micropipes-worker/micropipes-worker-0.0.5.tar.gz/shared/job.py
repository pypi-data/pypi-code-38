import json
import uuid

from shared.utils import *
from shared.constants import *


class Job():

    def __init__(self):
        self.job_status = JOB_STATUS_WAIT
        self.id = track_uuid()
        self.autostart = False
        self.name = None
        self.priority = 0
        self.routes = []
        self.required_workers = []
        self.required_data_support = []
        # for choosing older job if prio is the same
        self.created = time.time()
        self.customer_id = None


    def from_dict(self, d):
        if not 'id' in d or d['id'] == None:
            d['id'] = track_uuid()
        self.id = d['id']
        self.name = d['name']
        if 'customer_id' in d:
            self.customer_id = d['customer_id']
        if 'autostart' in d:
            self.autostart = d['autostart']
        if 'priority' in d:
            self.priority = d['priority']
        if 'created' in d:
            self.created = d['created']

        for x in d['routes']:
            route = SequenceRoute()
            route.from_dict(x)
            self.routes.append(route)

        for x in d['required_workers']:
            worker = RequiredWorker()
            worker.from_dict(x)
            self.required_workers.append(worker)

        if 'required_data_support' in d:
            for x in d['required_data_support']:
                data_s = DataDef()
                data_s.from_dict(x)
                self.required_data_support.append(data_s)
        else:
            # default data support
            self.required_data_support.append(DataDef())

    def get_config(self, worker_type):
        for wrk in self.required_workers:
            if wrk.worker_type == worker_type:
                return wrk.configuration
        return None

    # becacuse id's are unique, we dont need route_id
    def get_next_step_(self, step_id):
        if not self.routes or len(self.routes) == 0:
            return None
        for route in self.routes:
            for x in range(len(route.steps)):
                step = route.steps[x]
                if step.id == step_id:
                    if x+1 < len(route.steps):
                        return route.steps[x+1]
                    else:
                        return None
        return None

    def get_first_step(self, route_name):
        for route in self.routes:
            if route.name == route_name:
                if route.steps and len(route.steps) > 0:
                    return route.steps[0]
                    # queue = route.steps[0].worker_type
                    # step_id = route.steps[0].id
                    # return queue, step_id



class RequiredWorker():
    def __init__(self):
        self.id = track_uuid()
        self.assignements = []
        self.ready_confirmation = []

    def from_dict(self, d):
        if not 'id' in d:
            d['id'] = track_uuid()
        self.id = d['id']
        self.worker_type = d['worker_type']
        if 'configuration' in d:
            self.configuration = d['configuration']
        else:
            self.configuration = []


    def has_assignement(self, worker_id):
        rt = False
        for x in self.assignements:
            if worker_id == x.id:
                return True
        return rt

    def has_ready_confirmation(self, worker_id):
        rt = False
        for x in self.ready_confirmation:
            if worker_id == x.id:
                return True
        return rt

    def remove_assignment(self, worker_id):
        ob = None
        for x in self.assignements:
            if worker_id == x.id:
                ob = x
                break
        if ob:
            self.assignements.remove(ob)
            if ob in self.ready_confirmation:
                self.ready_confirmation.remove(ob)

class SequenceRoute():
    def __init__(self):
        self.id = track_uuid()
        self.steps = []
        self.data = None
        self.in_routing = track_uuid()
        self.out_routing = track_uuid()

    def from_dict(self,d):
        if not 'id' in d:
            d['id'] = track_uuid()
        self.id = d['id']
        if 'data' in d:
            self.data = d['data']
        self.name = d['name']
        self.type = d['type_name']
        if 'in_route' in d:
            self.in_routing = d['in_route']
        if 'out_route' in d:
            self.out_routing = d['out_route']
        if 'steps' in d:
            for x in d['steps']:
                step = Step()
                step.from_dict(x)
                self.steps.append(step)

class Step():
    def __init__(self):
        self.id = track_uuid()

    def from_dict(self, d):
        if not 'id' in d:
            d['id'] = track_uuid()
        self.id = d['id']
        self.name = d['name']
        self.worker_type = d['worker_type']



class DataDef():
    def __init__(self):
        self.id = track_uuid()
        self.name = 'default'
        self.content_type = 'application/json'
        self.content_encoding = 'utf-8'

    def from_dict(self, d):
        if not 'id' in d:
            d['id'] = track_uuid()
        self.id = d['id']
        self.name = d['name']
        if 'content_type' in d:
            self.content_type = d['content_type']
        if 'content_encoding' in d:
            self.content_encoding = d['content_encoding']



class JobJsonEncoder(json.JSONEncoder):

    def default(self, z):
        if isinstance(z, Job):
            return {
                'id':z.id,
                'name': z.name,
                'customer_id': z.customer_id,
                'autostart': z.autostart,
                'priority': z.priority,
                'created': z.created,
                'routes': z.routes,
                'required_workers': z.required_workers
            }
        elif isinstance(z, RequiredWorker):
            return {
                'id': z.id,
                'worker_type':z.worker_type,
                'configuration': z.configuration
            }
        elif isinstance(z, DataDef):
            return {
                'id': z.id,
                'name': z.name,
                'content_type':z.content_type,
                'content_encoding': z.content_encoding
            }
        elif isinstance(z, SequenceRoute):
            return {
                'id': z.id,
                'name':z.name,
                'type_name': z.type,
                'steps': z.steps
            }
        elif isinstance(z, Step):
            return {
                'id': z.id,
                'name':z.name,
                'worker_type': z.worker_type
            }
        else:
            return super().default(z)



def job_to_jsonstring( job ):
    return json.dumps(job, cls=JobJsonEncoder)


def job_headers( job_id, step_id ):
    return {
        'job_id': job_id,
        'step_id': step_id
    }

def job_step_from_props( props ):
    if props and props.headers and 'job_id' in props.headers and 'step_id' in props.headers:
        return props.headers['job_id'], props.headers['step_id']


