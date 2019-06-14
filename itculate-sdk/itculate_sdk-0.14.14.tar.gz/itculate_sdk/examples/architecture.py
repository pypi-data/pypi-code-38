#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import itculate_sdk as itsdk
from unix_dates import UnixDate, UnixTimeDelta

from itculate_sdk.examples.util import Service, mockup_samples

if __name__ == '__main__':
    # Initialize SDK to send data directly to the cloud
    # itsdk.init(server_url="http://localhost:5000/api/v1", role="cloudoscope")
    itsdk.init(role="cloudoscope")

    cid = "architecture"

    web_api = Service.create_service(key_prefix=cid,
                                     name="web-api",
                                     collector_id=cid,
                                     ec2_count=3)

    web_ui = Service.create_service(key_prefix=cid,
                                    name="web-ui",
                                    collector_id=cid,
                                    ec2_count=3)

    web_internal = Service.create_service(key_prefix=cid,
                                          name="web-internal",
                                          collector_id=cid,
                                          ec2_count=3)

    web_ab = Service.create_service(key_prefix=cid,
                                    name="web-ab-test",
                                    collector_id=cid,
                                    ec2_count=3)

    query_cache = Service.create_service(key_prefix=cid,
                                         name="query-cache",
                                         collector_id=cid,
                                         ec2_count=3,
                                         redis_az=["us-east-1b"],
                                         redis_count=3)

    authentication = Service.create_service(key_prefix=cid,
                                            name="authentication",
                                            default_az=["us-east-1b"],
                                            collector_id=cid,
                                            ec2_count=2)

    rest_api = Service.create_service(key_prefix=cid,
                                      name="rest-api",
                                      default_az=["us-east-1b"],
                                      collector_id=cid,
                                      ec2_count=3,
                                      rds_count=1,
                                      efs_name="images",
                                      elastic_search_count=1,
                                      redis_count=3)

    rest_audit = Service.create_service(key_prefix=cid,
                                        name="rest-audit-api",
                                        collector_id=cid,
                                        ec2_count=3,
                                        rds_count=1,
                                        elastic_search_count=1,
                                        redis_az=["us-east-1b"],
                                        redis_count=3)

    rest_alert = Service.create_service(key_prefix=cid,
                                        name="rest-alert-api",
                                        collector_id=cid,
                                        ec2_count=3,
                                        elastic_search_count=1,
                                        default_az=["us-east-1c"],
                                        redis_count=1)

    rest_abnormal = Service.create_service(key_prefix=cid,
                                           name="rest-abnormal-api",
                                           default_az=["us-east-1c"],
                                           collector_id=cid,
                                           ec2_count=3,
                                           elastic_search_count=1,
                                           redis_count=1)

    drupal = Service.create_service(key_prefix=cid,
                                    name="drupal",
                                    collector_id=cid,
                                    default_az=["us-east-1b"],
                                    rds_count=2,
                                    ec2_count=3,
                                    efs_name="drupalDB")

    cassandra = Service.create_service(key_prefix=cid,
                                       name="cassandra",
                                       collector_id=cid,
                                       ec2_count=6,
                                       ec2_vertex_subtype="Cassandra")

    itsdk.connect(source=web_api.asg, target=rest_api.elb, topology="use-elb$group", collector_id=cid)
    itsdk.connect(source=web_ui.asg, target=rest_api.elb, topology="use-elb$group", collector_id=cid)
    itsdk.connect(source=web_internal.asg, target=rest_api.elb, topology="use-elb$group", collector_id=cid)
    itsdk.connect(source=web_ab.asg, target=rest_api.elb, topology="use-elb$group", collector_id=cid)

    itsdk.connect(source=web_api.asg, target=query_cache.elb, topology="use-cache$group", collector_id=cid)
    itsdk.connect(source=web_ui.asg, target=query_cache.elb, topology="use-cache$group", collector_id=cid)
    itsdk.connect(source=web_internal.asg, target=query_cache.elb, topology="use-cache$group", collector_id=cid)
    itsdk.connect(source=web_ab.asg, target=query_cache.elb, topology="use-cache$group", collector_id=cid)

    itsdk.connect(source=query_cache.asg, target=authentication.elb, topology="use-auth$group", collector_id=cid)

    itsdk.connect(source=rest_api.asg, target=authentication.elb, topology="use-auth$group", collector_id=cid)
    itsdk.connect(source=rest_api.asg, target=drupal.elb, topology="use-drupal$group", collector_id=cid)
    itsdk.connect(source=rest_api.asg, target=cassandra.asg, topology="use-cassandra$group", collector_id=cid)

    itsdk.connect(source=web_api.asg, target=rest_audit.elb, topology="use-audit$group", collector_id=cid)
    itsdk.connect(source=web_api.asg, target=rest_abnormal.elb, topology="use-abnormal$group", collector_id=cid)
    itsdk.connect(source=web_api.asg, target=rest_alert.elb, topology="use-alert$group", collector_id=cid)

    itsdk.flush_all()

    # time = UnixDate.now() - UnixTimeDelta.calc(hours=10)

    # itsdk.vertex_event(collector_id=cid,
    #                    vertex=rest_abnormal.asg,
    #                    message="Property tags.Version changed from 2.1.11 to 2.1.12",
    #                    event_type="Property Changed",
    #                    timestamp=time + UnixTimeDelta.calc(hours=3))
    # itsdk.vertex_event(collector_id=cid,
    #                    vertex=rest_abnormal.asg,
    #                    message="Property min-size changed from 4 to 8",
    #                    event_type="Property Changed",
    #                    timestamp=time + UnixTimeDelta.calc(hours=4))
    # itsdk.vertex_event(collector_id=cid,
    #                    vertex=rest_abnormal.asg,
    #                    message="Property instance-type changed from m4.2xlarge to c4.xlarge",
    #                    event_type="Property Changed",
    #                    timestamp=time + UnixTimeDelta.calc(hours=6))

    # itsdk.flush_all()

    vertices = []
    vertices.extend(web_api.vertices)
    vertices.extend(web_ui.vertices)
    vertices.extend(web_internal.vertices)
    vertices.extend(web_ab.vertices)
    vertices.extend(query_cache.vertices)
    vertices.extend(authentication.vertices)
    vertices.extend(rest_api.vertices)
    vertices.extend(rest_audit.vertices)
    vertices.extend(rest_alert.vertices)
    vertices.extend(rest_abnormal.vertices)
    vertices.extend(drupal.vertices)
    vertices.extend(cassandra.vertices)

    mockup_samples(vertices,
                   end_time=UnixDate.now() + UnixTimeDelta.calc(hours=12),
                   start_time=UnixDate.now() - UnixTimeDelta.calc(hours=12))
    itsdk.flush_all()
