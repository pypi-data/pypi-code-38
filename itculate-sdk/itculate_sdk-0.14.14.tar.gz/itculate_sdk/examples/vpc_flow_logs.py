#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import itculate_sdk as itsdk

from itculate_sdk.examples.util import Service, mockup_samples

# please contact admin@itculate.io for api_key and api_secret

collector_id = "vpc_flow_logs"
topology = "payload-processing"


# publish to pypi
# http://peterdowns.com/posts/first-time-with-pypi.html


if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", api_key=api_key, api_secret=api_secret)
    itsdk.init(role="cloudoscope")
    # itsdk.init(server_url="http://localhost:5000/api/v1", role="cloudoscope")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:
    bucket = itsdk.add_vertex(collector_id=collector_id,
                              name="raw-payload",
                              vertex_type="S3",
                              keys="vfl-raw-payload")

    # Defining the first service:
    # Create the s3 Vertex:
    a_lambda = itsdk.add_vertex(collector_id=collector_id,
                                name="raw-payload-uploaded",
                                vertex_type="Lambda",
                                keys="vfl-lambda-payload-uploaded")

    tenant_management_service = Service.create_service(name="tenant-management",
                                                       collector_id=collector_id,
                                                       ec2_count=4,
                                                       redis_count=1,
                                                       rds_count=1)

    malware_analyzer = Service.create_service(name="malware-analyzer",
                                              collector_id=collector_id,
                                              ec2_count=6,
                                              rds_count=1,
                                              redis_count=2,
                                              elastic_search_count=1)

    # connect the  bucket to lambda to Microservice
    itsdk.connect(collector_id=collector_id,
                  source=bucket,
                  target=a_lambda,
                  topology=topology)

    itsdk.connect(collector_id=collector_id,
                  source=a_lambda,
                  target=malware_analyzer.service,
                  topology="malware_analyzer-service")

    for ec2 in malware_analyzer.ec2s:
        itsdk.connect(collector_id=collector_id,
                      source=ec2,
                      target=tenant_management_service.rdses[0],
                      topology="uses-rds")

    itsdk.connect(collector_id=collector_id,
                  source=malware_analyzer.asg,
                  target=tenant_management_service.rdses[0],
                  topology="uses-rds$group")

    # Flush and commit topology
    itsdk.flush_all()

    # mockup timeseries
    feel_pain_vertices = [tenant_management_service.service, tenant_management_service.elb,
                          tenant_management_service.asg] + tenant_management_service.ec2s
    cause_pain_vertices = [malware_analyzer.service, malware_analyzer.elb, malware_analyzer.asg] + malware_analyzer.ec2s
    contention_vertices = [tenant_management_service.rdses[0]]

    feel_pain = None
    for fp in feel_pain_vertices:
        if fp.type in ("AWS_ELB", "AWS_ALB"):
            feel_pain = fp
            break
    cause_pain = None
    for cp in cause_pain_vertices:
        if cp.type in ("AWS_ELB", "AWS_ALB"):
            cause_pain = cp
            break

    vertex_unhealthy = None
    for cv in contention_vertices:
        vertex_unhealthy = cv
        break

    message = "ELB {} is experiencing High Latency as a result of contention on RDS {}. " \
              "That contention is cause by high request activity from ELB {}".format(feel_pain.name,
                                                                                     vertex_unhealthy.name,
                                                                                     cause_pain.name)

    mockup_samples(vertices=tenant_management_service.vertices + malware_analyzer.vertices + [a_lambda],
                   feel_pain_vertices=feel_pain_vertices,
                   cause_pain_vertices=cause_pain_vertices,
                   contention_vertices=contention_vertices,
                   message=message,
                   vertex_unhealthy=vertex_unhealthy)
    itsdk.flush_all()
