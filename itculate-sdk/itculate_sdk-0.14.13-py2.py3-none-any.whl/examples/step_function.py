from collections import defaultdict
import random
from itculate_sdk.examples.util import Service, mockup_samples
from unix_dates import UnixDate, UnixTimeDelta

__author__ = 'ran'
import itculate_sdk as itsdk


# https://aws.amazon.com/step-functions/
# https://states-language.net/spec.html


class RequestsCostDataType(itsdk.DataTypeWithUnit):
    units_def = ("c", "$")
    bases_def = (100,)
    default_unit = "c"


parallel = {
    "Comment": "A simple example of the Steps language using an AWS Lambda Function",
    "StartAt": "ProcessPhoto",

    "States": {
        "ProcessPhoto": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:eu-west-1:99999999999:function:ProcessPhoto",
            "Next": "Parallel"
        },

        "Parallel": {
            "Type": "Parallel",
            "Next": "LoadInDatabase",
            "Branches": [
                {
                    "StartAt": "ExtractMetaData",
                    "States": {
                        "ExtractMetaData": {
                            "Type": "Task",
                            "Resource": "arn:aws:lambda:eu-west-1:9999999999:function:ExtractMetaData",
                            "End": True
                        }
                    }
                },

                {
                    "StartAt": "ResizeImage",
                    "States": {
                        "ResizeImage": {
                            "Type": "Task",
                            "Resource": "arn:aws:lambda:eu-west-1:99999999999:function:ResizeImage",
                            "End": True
                        }
                    }
                },
                {
                    "StartAt": "FacialRecognition",
                    "States": {
                        "FacialRecognition": {
                            "Type": "Task",
                            "Resource": "arn:aws:lambda:eu-west-1:99999999999:function:FacialRecognition",
                            "End": True
                        }
                    }
                }
            ]
        },

        "LoadInDatabase": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:eu-west-1:99999999999:function:LoadInDatabase",
            "End": True
        }
    }
}

LAMBDA_APPROXIMATE_PRICE_PER_MS = 0.000002396 / 100.0

# please contact admin@itculate.io for api_key and api_secret

# cloudoskope
# api_key = "61KA0DUPGPRB638RMJRQP8OMG"  # When None, the SDK will try to look for a 'credentials' file in '~/.itculate/'
# api_secret = "YR3SBqOmPq0WMLP4fZrwwdkweTKeiiHcRa2HfRS9s1Q"
# server_url = "http://localhost:5000/api/v1"

# itsdk.init(role="cloudoscope", server_url="http://localhost:5000/api/v1")
itsdk.init(role="cloudoscope")

cid = "step_function"


def local_mockup_samples(vertices):
    start_time = UnixDate.now() - UnixTimeDelta.calc(hours=72)

    index = 0

    for vertex in vertices:
        index += 1

        unhealthy_event_created = False

        for i in range(-720, 720, 5):
            timestamp = start_time + UnixTimeDelta.calc(minutes=i)

            event_interval = 120 < i < 210

            abs_i = abs(i)
            invocations = index * random.randint(720 - abs_i, 720 - abs_i + 100)
            duration = 1000 * index * 1.13 * random.randint(1, 5)
            queue_size = abs_i / 1000 + random.random()
            errors = 0.0

            invocations = invocations * (0.2 + 0.5 * random.random()) if event_interval else invocations
            queue_size = index * random.randint(75, 100) / 19.1 if event_interval else queue_size
            duration = random.randint(91, 111) / 3.1 if event_interval else duration
            cpu_utilization = 0.2 + 0.5 * random.random()
            network_utilization = cpu_utilization * random.random()
            latency = cpu_utilization + 20 * random.random()

            price = duration * invocations * LAMBDA_APPROXIMATE_PRICE_PER_MS

            if vertex.type == "AWS_Lambda":
                if vertex.name.find("Facial") > -1 and event_interval:
                    errors = 0.5 + 0.5 * random.random()
                    duration = random.random()
                    queue_size = 0

                    if not unhealthy_event_created:
                        unhealthy_event_created = True
                        itsdk.vertex_unhealthy(vertex=vertex,
                                               message="Facial Recognition - "
                                                       "Failed to connect to AWS ElasticCache Redis",
                                               timestamp=timestamp,
                                               attribute="memory-size",
                                               old_value=256,
                                               new_value=128,
                                               collector_id=cid)

                if vertex.name.find("event") > -1 and event_interval:
                    errors = 0
                    duration = random.random() / 2
                    queue_size = 0
                    invocations /= 20

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations",
                                 value=itsdk.CountDataType.value(value=invocations, importance=1))

                # duration = 1.13 * (random.randint(2000, 3000) if event_interval else random.randint(100, 150))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="duration",
                                 value=itsdk.DurationDataType.value(value=duration, importance=2))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="duration",
                                 value=itsdk.DurationDataType.value(value=duration, importance=2))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations-error-percent",
                                 value=itsdk.ErrorPercentDataType.value(value=errors, importance=3))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="estimated-invocation-cost",
                                 value=RequestsCostDataType.value(value=price, importance=3, unit='$'))

                print "invocations {} duration {} queue {} errors {}".format(invocations, duration, queue_size, errors)

            elif vertex.type == "AWS_RDS":
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="total-latency",
                                 value=itsdk.LatencyDataType.value(value=latency, importance=1))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="cpu-utilization",
                                 value=itsdk.CPUPercentDataType.value(value=cpu_utilization, importance=2))
                # itsdk.add_sample(vertex=vertex,
                #                  timestamp=timestamp,
                #                  counter="network-utilization",
                #                  value=itsdk.NetworkPercentDataType.value(value=network_utilization, importance=3))


class StateMachine(object):
    def __init__(self):
        super(StateMachine, self).__init__()

        self.name_to_next_names = defaultdict(list)

        # The state name, whose length MUST BE less than or equal to 128 Unicode characters, is the field name;
        # state names MUST be unique within the scope of the whole state machine.
        # States describe tasks (units of work), or specify flow control (e.g. Choice).
        self.name_to_state = {}

        self.vertices = []

    def create_topology(self, state_machine):
        self._parse_topology(state_machine)

        name_to_vertex = {}

        for name, state in self.name_to_state.iteritems():
            resource = state.get("Resource")
            function_resource = resource.find(":function:")
            if function_resource == -1:
                assert False, "only function resource supported not {}".format(resource)
            function_name = resource[function_resource + 10:]
            vertex = itsdk.add_vertex(collector_id=cid,
                                      vertex_type="AWS_Lambda",
                                      name=function_name,
                                      keys=resource,
                                      state=state)

            self.vertices.append(vertex)

            name_to_vertex[name] = vertex

        for name, next_names in self.name_to_next_names.iteritems():
            source_vertex = name_to_vertex[name]
            for next_name in next_names:
                target_vertex = name_to_vertex[next_name]
                itsdk.connect(collector_id=cid,
                              source=source_vertex,
                              target=target_vertex,
                              topology="process-photo-flow")

    def _parse_topology(self, state_machine):
        start_state_name = state_machine.get("StartAt")

        # Bootstrap the list from the initial vertices
        state_to_process = [start_state_name]
        states_visited = set()

        while state_to_process:
            # Get the next one off the list and work on it
            state_name = state_to_process.pop()
            states_visited.add(state_name)
            state = state_machine["States"].get(state_name)

            next_name = state.get("Next")
            resource = state.get("Resource")
            state["Start"] = state_name == start_state_name
            state["End"] = state.get("End", False)
            state["Intermediate"] = state["Start"] != state["End"]

            if resource:
                self.name_to_state[state_name] = state

            if next_name:
                next_state = state_machine["States"].get(next_name)
                branches = next_state.get("Branches")
                choices = state.get("Choices")
                if branches:
                    branches_next_state = next_state.get("Next")
                    if branches_next_state not in states_visited:
                        state_to_process.append(branches_next_state)

                    for branch in branches:
                        branch_start_state_name = branch.get("StartAt")
                        self.name_to_next_names[state_name].append(branch_start_state_name)
                        branch_state_machine = StateMachine()
                        branch_state_machine._parse_topology(state_machine=branch)

                        self.name_to_next_names.update(branch_state_machine.name_to_next_names)
                        self.name_to_state.update(branch_state_machine.name_to_state)

                        if branches_next_state:
                            self.name_to_next_names[branch_start_state_name].append(branches_next_state)

                elif choices:
                    assert False, "Choices is not supported"

                else:
                    self.name_to_next_names[state_name].append(next_name)
                    if next_name not in states_visited:
                        state_to_process.append(next_name)


s3_bucket = itsdk.add_vertex(collector_id=cid,
                             name="itculate.io-images",
                             vertex_type="AWS_S3_Bucket",
                             keys="s3")

rds = itsdk.add_vertex(collector_id=cid,
                       name="MySQL db1",
                       vertex_type="AWS_RDS",
                       keys="RDS")
rds_replica = itsdk.add_vertex(collector_id=cid,
                               name="MySQL db1_replica",
                               vertex_type="AWS_RDS",
                               keys="RDS-Mirror")

itsdk.connect(collector_id=cid,
              source=rds,
              target=rds_replica,
              topology="replica")

itsdk.connect(collector_id=cid,
              source=parallel["States"]["LoadInDatabase"]["Resource"],
              target="RDS",
              topology="process-photo-flow")

itsdk.connect(collector_id=cid,
              source=s3_bucket,
              target=parallel["States"]["ProcessPhoto"]["Resource"],
              topology="process-photo-flow")

a = StateMachine()
a.create_topology(parallel)

web_api = Service.create_service(key_prefix=cid,
                                 name="web-image-api",
                                 collector_id=cid,
                                 ec2_count=3)

itsdk.connect(source=web_api.asg, target=rds, topology="uses-rds$group", collector_id=cid)
itsdk.connect(source=web_api.ec2s, target=rds, topology="uses-rds", collector_id=cid)

local_mockup_samples(a.vertices)
local_mockup_samples([rds, rds_replica])
mockup_samples(vertices=web_api.vertices)

itsdk.flush_all()
