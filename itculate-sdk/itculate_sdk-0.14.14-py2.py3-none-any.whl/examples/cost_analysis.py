#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#
from itculate_sdk.examples.util import Service, mockup_samples

import itculate_sdk as itsdk

from unix_dates import UnixDate, UnixTimeDelta


# please contact admin@itculate.io for api_key and api_secret

# publish to pypi
# http://peterdowns.com/posts/first-time-with-pypi.html

cid = "cost"


def create_topology(ec2_version, ec2_instance_type, ec2_count, ec2_cost):
    default_az = ["us-east-1b", "us-east-1c", "us-east-1d"]
    # Create the s3 Vertex:
    bucket = itsdk.add_vertex(collector_id=cid,
                              name="uploaded_bucket",
                              vertex_type="S3",
                              keys="cdr-uploaded-bucket")
    # Defining the first service:
    # Create the s3 Vertex:
    a_lambda = itsdk.add_vertex(collector_id=cid,
                                name="payload-uploaded",
                                vertex_type="Lambda",
                                keys="cdr-lambda-payload-uploaded")
    # connect the  bucket to lambda to Microservice
    itsdk.connect(collector_id=cid,
                  source=bucket,
                  target=a_lambda,
                  topology="use-lambda")
    for i in range(len(default_az)):
        cdr_scanner = Service.create_service(name="cdr-scanner@chanel-{}".format(i + 1),
                                             collector_id=cid,
                                             default_az=[default_az[i]],
                                             ec2_count=6 + 2 * i,
                                             redis_count=1,
                                             ec2_cost=8)

        cdr_archive = Service.create_service(name="cdr-archive@chanel-{}".format(i + 1),
                                             collector_id=cid,
                                             default_az=[default_az[i]],
                                             ec2_count=2 + 2 * i,
                                             rds_count=1,
                                             rds_az=[default_az[i]] if i < 2 else [default_az[1]],
                                             ec2_cost=6)

        cdr_analyzer = Service.create_service(name="cdr-analyzer@chanel-{}".format(i + 1),
                                              collector_id=cid,
                                              default_az=[default_az[i]],
                                              ec2_count=2 + 2 * i,
                                              redis_count=2,
                                              rds_count=1 + i,
                                              ec2_cost=12)

        itsdk.connect(collector_id=cid,
                      source=a_lambda,
                      target=cdr_scanner.service,
                      topology="cdr-scanners")

        itsdk.connect(source=cdr_scanner.service,
                      target=cdr_archive.service,
                      topology="use-archive",
                      collector_id=cid)
        itsdk.connect(source=cdr_scanner.service,
                      target=cdr_analyzer.service,
                      topology="use-analyzer",
                      collector_id=cid)

    return Service.create_service(name="logs-scanner",
                                  collector_id=cid,
                                  ec2_count=ec2_count,
                                  redis_count=3,
                                  redis_az=["us-east-1b"],
                                  rds_count=1,
                                  ec2_version=ec2_version,
                                  ec2_instance_type=ec2_instance_type,
                                  ec2_cost=ec2_cost)


if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud

    # itsdk.init(server_url="http://localhost:5000/api/v1", role="cloudoscope")
    itsdk.init(role="cloudoscope")

    ########################################################################
    # Step 1 - Create Topology
    ########################################################################

    # Create the s3 Vertex:

    ec2_cost = 141
    ec2_count = 18

    event_analyzer = create_topology(ec2_version="2.1.6",
                                     ec2_instance_type="m4.large",
                                     ec2_count=ec2_count,
                                     ec2_cost=ec2_cost)
    itsdk.flush_all()

    now = UnixDate.now()

    vertices = [event_analyzer.service, event_analyzer.asg, event_analyzer.elb]
    start_time = now - UnixTimeDelta.calc(days=2)
    version_change_to_2_1_7_time = now - UnixTimeDelta.calc(hours=16)
    mockup_samples(vertices=vertices,
                   start_time=start_time,
                   end_time=version_change_to_2_1_7_time - 1,
                   instance_count=ec2_count,
                   create_event=False,
                   factor=4,
                   ec2_cost=ec2_cost)

    event = itsdk.vertex_property_change(collector_id=cid,
                                         vertex=event_analyzer.asg,
                                         attribute="Version",
                                         old_value="2.1.6",
                                         new_value="2.1.7",
                                         message="Version changed from '2.1.6' to '2.1.7'",
                                         timestamp=version_change_to_2_1_7_time)
    event["document"]["old-price"] = ec2_cost * ec2_count
    event["document"]["new-price"] = ec2_cost * ec2_count
    itsdk.flush_all()

    asd_instance_type_change_time = now - UnixTimeDelta.calc(hours=12, minutes=31)
    mockup_samples(vertices=vertices,
                   start_time=version_change_to_2_1_7_time,
                   end_time=asd_instance_type_change_time - 1,
                   instance_count=ec2_count,
                   create_event=False,
                   factor=1000,
                   ec2_cost=ec2_cost)
    event = itsdk.vertex_property_change(collector_id=cid,
                                         vertex=event_analyzer.asg,
                                         attribute="instance-type",
                                         old_value="m4.large",
                                         new_value="m4.2xlarge",
                                         message="instance-type changed from 'm4.large' to 'm4.2xlarge'",
                                         timestamp=asd_instance_type_change_time)
    event["document"]["old-price"] = ec2_cost * ec2_count
    event["document"]["new-price"] = 3.9 * ec2_cost * ec2_count
    itsdk.flush_all()

    version_change_to_2_1_8_time = now - UnixTimeDelta.calc(hours=8, minutes=ec2_count)
    mockup_samples(vertices=vertices,
                   start_time=asd_instance_type_change_time,
                   end_time=version_change_to_2_1_8_time - 1,
                   instance_count=ec2_count,
                   create_event=False,
                   factor=4,
                   ec2_cost=3.9 * ec2_cost)
    event = itsdk.vertex_property_change(collector_id=cid,
                                         vertex=event_analyzer.asg,
                                         attribute="Version",
                                         old_value="2.1.7",
                                         new_value="2.1.8",
                                         message="Version changed from '2.1.7' to '2.1.8'",
                                         timestamp=version_change_to_2_1_8_time)
    event["document"]["old-price"] = 3.9 * ec2_cost * ec2_count
    event["document"]["new-price"] = 3.9 * ec2_cost * ec2_count
    itsdk.flush_all()

    min_size_change_to_3_time = now - UnixTimeDelta.calc(hours=4, minutes=11)
    event = itsdk.vertex_property_change(collector_id=cid,
                                         vertex=event_analyzer.asg,
                                         attribute="asg-maz-size",
                                         old_value=ec2_count,
                                         new_value=4,
                                         message="Scaling Group minimum size changed from 18 to 4",
                                         timestamp=min_size_change_to_3_time)
    mockup_samples(vertices=vertices,
                   start_time=version_change_to_2_1_8_time,
                   end_time=min_size_change_to_3_time - 1,
                   instance_count=ec2_count,
                   create_event=False,
                   factor=1,
                   ec2_cost=3.9 * ec2_cost)

    event["document"]["old-price"] = 3.9 * ec2_cost * ec2_count
    event["document"]["new-price"] = 3.9 * ec2_cost * 4
    itsdk.flush_all()

    mockup_samples(vertices=vertices,
                   start_time=min_size_change_to_3_time,
                   end_time=now,
                   instance_count=4,
                   create_event=False,
                   factor=4,
                   ec2_cost=3.9 * ec2_cost)

    itsdk.flush_all()

    # mockup_samples(vertices=vertices,
    #                start_time=start_time,
    #                end_time=asd_min_instance_change_time,
    #                instance_count=6,
    #                create_event=False,
    #                factor=10)
