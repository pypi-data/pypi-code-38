import datetime

from unix_dates import UnixDate

import itculate_sdk as itsdk

itsdk.init(role="cloudoscope")

#############################
# create topology
#############################

collector_id = "kubernetes"

elb = itsdk.add_vertex(collector_id=collector_id,
                       name="analytics-elb",
                       vertex_type="AWS_ELB",
                       keys="analytics-kubernetes-elb",
                       data={
                           "availability-zones": ["us-east-1b", "us-east-1c"]
                       })

kubernetes = itsdk.add_vertex(name="lab-cluster",
                              vertex_type="Kubernetes",
                              keys="kubernetes-cluster",
                              collector_id=collector_id)

node1 = itsdk.add_vertex(name="node1 (i-1438811)",
                         vertex_type="EC2",
                         keys="i-1438811",
                         collector_id=collector_id,
                         data={
                             "platform": "kubernetes",
                             "instance-type": "m5.xlarge",
                             "estimated-cost": 41.2,
                             "availability-zone": "us-east-1b",
                             "compute-type": {"local_storage_gb": 0},
                             "state": "running",
                         })

node2 = itsdk.add_vertex(name="node1 (i-9434223)",
                         vertex_type="EC2",
                         keys="i-9434223",
                         collector_id=collector_id,
                         data={
                             "platform": "kubernetes",
                             "instance-type": "m5.xlarge",
                             "estimated-cost": 41.2,
                             "availability-zone": "us-east-1c",
                             "compute-type": {"local_storage_gb": 0},
                             "state": "running",
                         })

node3 = itsdk.add_vertex(name="node1 (i-6434311)",
                         vertex_type="EC2",
                         keys="i-6434311",
                         collector_id=collector_id,
                         data={
                             "platform": "kubernetes",
                             "instance-type": "m5.xlarge",
                             "estimated-cost": 41.2,
                             "availability-zone": "us-east-1d",
                             "compute-type": {"local_storage_gb": 0},
                             "state": "running",
                         })

node1_pods = [itsdk.add_vertex(name="pod-config-1-{}".format(i),
                               vertex_type="Pod",
                               keys="pod-config-1-{}".format(i),
                               collector_id=collector_id,
                               data={
                                   "availability-zone": "us-east-1b",
                               }
                               ) for i in range(3)]

node2_pods = [itsdk.add_vertex(name="pod-config-2-{}".format(i),
                               vertex_type="Pod",
                               keys="pod-config-2-{}".format(i),
                               collector_id=collector_id,
                               data={
                                   "availability-zone": "us-east-1c",
                               }
                               ) for i in range(4)]

node3_pods = [itsdk.add_vertex(name="pod-config-3-{}".format(i),
                               vertex_type="Pod",
                               keys="pod-config-3-{}".format(i),
                               collector_id=collector_id,
                               data={
                                   "availability-zone": "us-east-1d",
                               }
                               ) for i in range(2)]

pod1_containers = [itsdk.add_vertex(name="analytics-1-{}".format(i),
                                    vertex_type="Container",
                                    keys="container-1-{}".format(i),
                                    collector_id=collector_id,
                                    data={
                                        "availability-zone": "us-east-1b",
                                    }
                                    ) for i in range(6)]

pod2_containers = [itsdk.add_vertex(name="management-2-{}".format(i),
                                    vertex_type="Container",
                                    keys="container-2-{}".format(i),
                                    collector_id=collector_id,
                                    data={
                                        "availability-zone": "us-east-1c",
                                    }
                                    ) for i in range(4)]

efs = itsdk.add_vertex(collector_id=collector_id,
                       vertex_type="AWS_EFS",
                       name="efs_management",
                       keys="efs_management",
                       data={
                           "estimated-cost": 561,
                           "capacity": 561 * 3,
                           "availability-zones": ["us-east-1d", "us-east-1c"]
                       })

rds = itsdk.add_vertex(collector_id=collector_id,
                       name="MySQL analytics-db",
                       vertex_type="AWS_RDS",
                       keys="analytics-db-22",
                       data={
                           "instance-type": "db.m4.2xlarge",
                           "estimated-cost": 741,
                           "availability-zone": "us-east-1d",
                           "secondary-availability-zone": "us-east-1c"
                       })

itsdk.connect(source=elb,
              target=[node1, node2, node3],
              topology="elb-to-nodes",
              collector_id=collector_id)

itsdk.connect(source=kubernetes,
              target=[node1, node2, node3],
              topology="cluster-to-nodes",
              collector_id=collector_id)

itsdk.connect(source=node1,
              target=node1_pods,
              topology="node-to-pods",
              collector_id=collector_id)

itsdk.connect(source=node2,
              target=node2_pods,
              topology="node-to-pods",
              collector_id=collector_id)

itsdk.connect(source=node3,
              target=node3_pods,
              topology="node-to-pods",
              collector_id=collector_id)

itsdk.connect(source=node1_pods[0],
              target=pod1_containers,
              topology="pod-to-containers",
              collector_id=collector_id)

itsdk.connect(source=node2_pods[0],
              target=pod2_containers,
              topology="pod-to-containers",
              collector_id=collector_id)

itsdk.connect(source=pod1_containers[0:3],
              target=efs,
              topology="containers-to-efs",
              collector_id=collector_id)

itsdk.connect(source=pod2_containers[0:2],
              target=rds,
              topology="containers-to-rds",
              collector_id=collector_id)

# itsdk.connect(source=pod3_containers,
#               target=node1,
#               topology="containers-to-node",
#               collector_id=collector_id)

itsdk.flush_all()
