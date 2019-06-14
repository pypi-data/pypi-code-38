from datetime import datetime
import random
from unix_dates import UnixDate, UnixTimeDelta
import itculate_sdk as itsdk

LAMBDA_ESTIMATED_COST_PER_MS = 0.000002396 / 100.0


class ConnectionsDataType(itsdk.CountDataType):
    pass


class ConnectionsPercentDataType(itsdk.PercentDataType):
    default_importance = itsdk.Importance.KPI_SYSTEM + 20


def common_document(vertices):
    current_document = None
    for vertex in vertices:
        if current_document:
            current_document = intersect_dicts(current_document, vertex)
        else:
            # remove the "_" attributes
            current_document = intersect_dicts(vertex, vertex)
    return current_document


def calc_estimated_cost(instance_count, ec2_cost):
    if ec2_cost:
        return ec2_cost * instance_count
    return itsdk.PricePerPeriodDataType.value(value=int(instance_count * 0.480 * 24 * 30),
                                              visible=True,
                                              unit=itsdk.Units.MONTHLY)


def get_redis_estimated_cost():
    return itsdk.PricePerPeriodDataType.value(value=int(0.455 * 24 * 30),
                                              visible=True,
                                              unit=itsdk.Units.MONTHLY)


def get_elastic_search_estimated_cost():
    return itsdk.PricePerPeriodDataType.value(value=int(0.587 * 24 * 30),
                                              visible=True,
                                              unit=itsdk.Units.MONTHLY)


def get_rds_estimated_cost():
    return itsdk.PricePerPeriodDataType.value(value=int(0.910 * 24 * 30),
                                              visible=True,
                                              unit=itsdk.Units.MONTHLY)


def get_redshift_estimated_cost():
    return itsdk.PricePerPeriodDataType.value(value=int(277),
                                              visible=True,
                                              unit=itsdk.Units.MONTHLY)


def intersect_dicts(dict1, dict2):
    result = {}
    for k in dict1.viewkeys() & dict2.viewkeys():
        if k[0] == "_":
            continue

        v1 = dict1[k]
        v2 = dict2[k]
        if v1 and v2:
            if isinstance(v1, dict) and isinstance(v2, dict):
                sub_intersect = intersect_dicts(v1, v2)
                if sub_intersect:
                    result[k] = sub_intersect
            elif v1 == v2:
                result[k] = v1
    return result


def mockup_samples(vertices,
                   feel_pain_vertices=None,
                   cause_pain_vertices=None,
                   contention_vertices=None,
                   message=None,
                   vertex_unhealthy=None,
                   rds_connection_utilization_vertices=None,
                   hour_of_event=14,
                   create_event=True,
                   instance_count=8,
                   end_time=None,
                   start_time=None,
                   factor=None,
                   ec2_cost=None):
    """

    :type vertices: list[itculate_sdk.Vertex]
    :type feel_pain_vertices: list[itculate_sdk.Vertex]
    :type cause_pain_vertices: list[itculate_sdk.Vertex]
    :type contention_vertices: list[itculate_sdk.Vertex]
    :return:
    """
    end_time = end_time if end_time else UnixDate.now()
    start_time = start_time if start_time else (end_time - UnixTimeDelta.calc(hours=48))

    now_less_24_hours = end_time - UnixTimeDelta.calc(hours=24)

    feel_pain_vertices_keys = {v.first_key for v in feel_pain_vertices} if feel_pain_vertices else {}
    cause_pain_vertices_keys = {v.first_key for v in cause_pain_vertices} if cause_pain_vertices else {}
    contention_vertices_keys = {v.first_key for v in contention_vertices} if contention_vertices else {}
    rds_connection_utilization_vertices_keys = {
        v.first_key for v in
        rds_connection_utilization_vertices
        } if rds_connection_utilization_vertices else {}

    event_timestamp = None

    for vertex in vertices:

        connections = 88
        connections_percent = connections / 256.0
        rds_connection_utilization_started = False

        for timestamp in range(int(start_time), int(end_time), 15):

            date = datetime.fromtimestamp(timestamp=timestamp)

            hour = date.hour

            the_factor = factor if factor else (max(1, (hour - 7) if hour < 13 else (21 - hour)))

            invocations = random.randint(200, 300) - (min(the_factor, 20) * random.randint(5, 10))
            duration = random.randint(91, 111)
            cpu_utilization = min(0.99, 0.1 * the_factor * random.random())
            memory_utilization = 5 + 2 * random.random()
            network_utilization = min(0.99, the_factor * random.random() / 20, )

            latency = max(1, int(random.randint(0, 10 * the_factor) + 10 * the_factor * random.random()))
            error_rate_1 = min(0.99, (the_factor + random.randint(1, 5)) / 100.0)
            error_rate_2 = min(0.99, (the_factor + random.randint(1, 5)) / 100.0)
            cache_miss = min(1.0, latency / 200.0)
            queue_io = random.randint(0, 2)

            price = duration * invocations * LAMBDA_ESTIMATED_COST_PER_MS

            cur_instance_count = instance_count

            if create_event:
                if hour == hour_of_event and timestamp > now_less_24_hours:
                    event_timestamp = event_timestamp if event_timestamp else timestamp
                    if vertex.first_key in feel_pain_vertices_keys:
                        latency = latency + random.randint(1000, 1200)
                        error_rate_1 = error_rate_1 * random.randint(2, 4)
                        error_rate_2 = 0
                        cpu_utilization = random.randint(8, 30) / 100.0
                        invocations *= 0.38
                    elif vertex.first_key in cause_pain_vertices_keys:
                        cpu_utilization = random.randint(80, 99) / 100.0
                        network_utilization *= 2
                        invocations = invocations * random.randint(3, 5)
                        latency /= 3.0
                        cache_miss /= 5.0
                        error_rate_2 = 0
                    elif vertex.first_key in contention_vertices_keys:
                        latency = latency + random.randint(290, 450)
                        cpu_utilization = random.randint(80, 99) / 100.0
                        network_utilization *= 2.3
                        queue_io = queue_io + random.randint(6, 10)

                if (hour == hour_of_event or rds_connection_utilization_started) and timestamp > now_less_24_hours:
                    if vertex.first_key in rds_connection_utilization_vertices_keys:
                        rds_connection_utilization_started = True
                        connections = 228
                        connections_percent = connections / 256.0
                        cur_instance_count = instance_count * 2
                        cpu_utilization *= 1.3

            if vertex.type == "AWS_Lambda":
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations",
                                 value=itsdk.CountDataType.value(value=invocations, importance=1))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="duration",
                                 value=itsdk.DurationDataType.value(value=duration, importance=2))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations-error-percent",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_1, importance=3))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="estimated-cost",
                                 value=itsdk.PricePerPeriodDataType.value(value=price, importance=4))
            if vertex.type in ("AWS_RDS", "AWS_Aurora", "AWS_DynamoDB", "Service",
                               "AWS_Auto_Scaling_Group", "AWS_Instance", "AWS_Redshift",
                               "AWS_Memcached", "AWS_Redis", "AWS_ELB", "AWS_ALB",
                               "NetApp_Volume", "AWS_EBS_Volume", "Ontap_Cloud", "Rubrik"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="total-latency",
                                 value=itsdk.LatencyDataType.value(value=latency, importance=3))

            if vertex.type in ("AWS_RDS", "AWS_Aurora", "AWS_DynamoDB", "Service",
                               "AWS_Auto_Scaling_Group", "AWS_Instance", "AWS_Redshift",
                               "AWS_Memcached", "AWS_Redis"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="cpu-utilization",
                                 value=itsdk.CPUPercentDataType.value(value=cpu_utilization, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="memory-utilization",
                                 value=itsdk.MemoryPercentDataType.value(value=memory_utilization, visible=False))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="network-utilization",
                                 value=itsdk.NetworkPercentDataType.value(value=network_utilization, visible=False))
            if vertex.type in ("AWS_RDS", "AWS_Aurora", "AWS_DynamoDB", "Service",
                               "AWS_Auto_Scaling_Group", "AWS_Instance", "AWS_Redshift",
                               "AWS_Memcached", "AWS_Redis", "NetApp_Volume", "AWS_EBS_Volume", "Ontap_Cloud",
                               "Rubrik",):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="queue-iops",
                                 value=itsdk.QueueSizeDataType.value(value=queue_io, importance=3))
            if vertex.type in ("AWS_RDS", "AWS_Aurora"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="connections",
                                 value=ConnectionsDataType.value(value=connections, visible=False))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="connections-percent",
                                 value=ConnectionsPercentDataType.value(value=connections_percent, visible=False))
            if vertex.type in ("AWS_Auto_Scaling_Group", "Service"):
                try:
                    itsdk.add_sample(vertex=vertex,
                                     timestamp=timestamp,
                                     counter="instance-count",
                                     value=itsdk.ObjectCountDataType.value(value=int(cur_instance_count), visible=True))
                    itsdk.add_sample(vertex=vertex,
                                     timestamp=timestamp,
                                     counter="estimated-cost",
                                     value=calc_estimated_cost(cur_instance_count, ec2_cost))
                except:
                    pass
            if vertex.type in ("AWS_Redshift", "AWS_Memcached", "AWS_Redis"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="cache-miss",
                                 value=itsdk.PercentDataType.value(value=cache_miss, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="estimated-cost",
                                 value=get_redis_estimated_cost())
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="total-commands",
                                 value=itsdk.RequestCountDataType.value(value=invocations, importance=3))
            if vertex.type in ("AWS_ELB", "AWS_ALB"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="request",
                                 value=itsdk.RequestCountDataType.value(value=invocations, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="http-5XX-error-rate",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_1, importance=3))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="http-4XX-error-rate",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_2, visible=False))

                # print "Flush timeseries for {}".format(vertex)
                # itsdk.flush_all()

    if vertex_unhealthy and message:
        itsdk.vertex_unhealthy(collector_id="mockup_util",
                               vertex=vertex_unhealthy,
                               message=message,
                               timestamp=event_timestamp)
        # itsdk.flush_all()


class Service(object):
    seed = 1

    DEFAULT_AZ = ["us-east-1b", "us-east-1c", "us-east-1d"]

    def __init__(self,
                 service,
                 elb,
                 asg,
                 ec2s,
                 rdses,
                 redshifts,
                 redises,
                 elastic_searches,
                 efs):
        self.service = service
        self.elb = elb
        self.asg = asg
        self.ec2s = ec2s
        self.rdses = rdses
        self.redshifts = redshifts
        self.redises = redises
        self.elastic_searches = elastic_searches
        self.efs = efs

    @property
    def vertices(self):
        result = [self.service, self.elb, self.asg]
        if self.ec2s:
            result += self.ec2s
        if self.rdses:
            result += self.rdses
        if self.redshifts:
            result += self.redshifts
        if self.redises:
            result += self.redises
        if self.elastic_searches:
            result += self.elastic_searches
        return result

    @classmethod
    def create_service(cls,
                       name,
                       collector_id,
                       ec2_count=3,
                       ec2_vertex_subtype=None,
                       default_az=None,
                       ec2_az=None,
                       rds_count=0,
                       rds_az=None,
                       redis_count=0,
                       redis_az=None,
                       redshift_count=0,
                       redshift_az=None,
                       elastic_search_count=0,
                       elastic_search_az=None,
                       efs_name=None,
                       efs_az=None,
                       key_prefix=None,
                       ec2_version=None,
                       ec2_cost=None,
                       ec2_instance_type="m4.2xlarge"):
        """
        :rtype: Service
        """
        # Simple helper method to create  a Microservice
        # Note that the vertex_type can be anything. The user decided what types are going to be available.

        key_prefix = "{}-".format(key_prefix) if key_prefix else ""

        default_az = default_az if default_az else cls.DEFAULT_AZ

        ec2_az = ec2_az if ec2_az and ec2_count else default_az
        rds_az = rds_az if rds_az and rds_count else default_az
        redis_az = redis_az if redis_az and redis_count else default_az
        redshift_az = redshift_az if redshift_az and redshift_count else default_az
        elastic_search_az = elastic_search_az if elastic_search_az and elastic_search_count else default_az
        efs_az = efs_az if efs_az and efs_name else default_az

        service_az = set()
        service_az.update(ec2_az if ec2_az else {})
        service_az.update(rds_az if rds_az else {})
        service_az.update(redis_az if redis_az else {})
        service_az.update(redshift_az if redshift_az else {})
        service_az.update(elastic_search_az if elastic_search_az else {})

        key_suffix = name.replace("@", "_").replace(" ", "_").replace("-", "_")

        cls.seed += 1

        # create the ELB vertex
        elb = itsdk.add_vertex(collector_id=collector_id,
                               name="{}-elb".format(name),
                               vertex_type="AWS_ELB",
                               keys="{}vfl-service-load-balancer-{}".format(key_prefix, key_suffix),
                               data={
                                   "availability-zones": Service.get_availability_zones(ec2_az, ec2_count)
                               })

        # create the Auto Scaling Group vertex
        asg = itsdk.add_vertex(collector_id=collector_id,
                               name="{}-asg".format(name),
                               vertex_type="AWS_Auto_Scaling_Group",
                               keys="{}vfl-service-auto-scaling-group-{}".format(key_prefix, key_suffix),
                               data={
                                   "instance-type": ec2_instance_type,
                                   "instance-count": ec2_count,
                                   "estimated-cost": ec2_cost if ec2_cost else calc_estimated_cost(ec2_count, ec2_cost),
                                   "availability-zones": Service.get_availability_zones(ec2_az, ec2_count),
                                   "min-size": ec2_count,
                                   "max-size": ec2_count + 10,
                                   "tags": {
                                       "Version": ec2_version if ec2_version else "{}.{}.{}".format(
                                           ord(name[0]) % 3,
                                           ord(name[1]) % 5,
                                           ord(name[2]) % 7,
                                       ),
                                   }
                               })

        # Connect elb and asg to the  Microservice

        itsdk.connect(collector_id=collector_id, source=elb, target=asg, topology="auto_scaling_group")

        # Create EC2 instances and connect them to the asg
        total_price = 0
        ec2s = []
        ec2_price = ec2_cost if ec2_cost else calc_estimated_cost(1, ec2_cost).value
        for i in range(ec2_count):
            total_price += ec2_price
            data = {
                "instance-type": ec2_instance_type,
                "estimated-cost": ec2_price,
                "availability-zone": ec2_az[i % len(ec2_az)] if ec2_az else None,
                "compute-type": {"local_storage_gb" : 0},
                "state": "running",
                "platform": "Linux",
                "tags": {
                    "Version": ec2_version if ec2_version else "{}.{}.{}".format(
                        ord(name[0]) % 3,
                        ord(name[1]) % 5,
                        ord(name[2]) % 7,
                    ),
                }
            }

            if ec2_vertex_subtype:
                data["_subtype"] = ec2_vertex_subtype,

            ec2 = itsdk.add_vertex(collector_id=collector_id,
                                   name="i-{}{}{}{}".format(cls.seed, 1 + i, int(UnixDate.now()), i),
                                   vertex_type="AWS_Instance",
                                   _subtype=ec2_vertex_subtype,
                                   keys="{}vfl-service-{}-ec2-{}".format(key_prefix, key_suffix, i),
                                   data=data)

            itsdk.connect(collector_id=collector_id, source=asg, target=ec2, topology="auto_scaling_group")
            ec2s.append(ec2)

        # Create RDS and connect them to the Microservice
        rdses = []
        rds_price = get_rds_estimated_cost()
        for i in range(rds_count):
            total_price += rds_price.value
            rds = itsdk.add_vertex(collector_id=collector_id,
                                   name="MySQL {}-db{}".format(name, i),
                                   vertex_type="AWS_RDS",
                                   keys="{}vfl-service-{}-db-{}".format(key_prefix, key_suffix, i),
                                   data={
                                       "instance-type": "db.m4.2xlarge",
                                       "estimated-cost": rds_price,
                                       "availability-zone": rds_az[i % len(rds_az)] if rds_az else None,
                                       "secondary-availability-zone": rds_az[(i + 1) % len(rds_az)] if rds_az else None
                                   })
            rdses.append(rds)

            itsdk.connect(collector_id=collector_id, source=asg, target=rds, topology="uses-rds$group")

            for ec2 in ec2s:
                itsdk.connect(collector_id=collector_id, source=ec2, target=rds, topology="uses-rds")

        # Create Redshift and connect them to the Microservice
        redshifts = []
        redshift_price = get_redshift_estimated_cost()
        for i in range(redshift_count):
            redshift = itsdk.add_vertex(collector_id=collector_id,
                                        name="Redshift db{}".format(i),
                                        vertex_type="AWS_Redshift",
                                        keys="{}vfl-service-{}-redshift-{}".format(key_prefix, key_suffix, i),
                                        data={
                                            "instance-type": "ds1.8xlarge",
                                            "estimated-cost": redshift_price,
                                            "availability-zones": Service.get_availability_zones(redshift_az,
                                                                                                 redshift_count)
                                        })

            redshifts.append(redshift)
            itsdk.connect(collector_id=collector_id, source=asg, target=redshift, topology="uses-redshift$group")
            for ec2 in ec2s:
                itsdk.connect(collector_id=collector_id, source=ec2, target=redshift, topology="uses-redshift")

        # Create Redis and connect them to the Microservice
        redises = []
        redis_price = get_redis_estimated_cost()
        for i in range(redis_count):
            total_price += redis_price.value
            redis = itsdk.add_vertex(collector_id=collector_id,
                                     name="Cache-{}-00{}".format("Master" if i == 0 else "Replica", i + 1),
                                     vertex_type="AWS_Redis",
                                     keys="{}vfl-service-{}-cache-00{}".format(key_prefix, key_suffix, i),
                                     data={
                                         "instance-type": "cache.r3.xlarge",
                                         "estimated-cost": redis_price,
                                         "availability-zones":
                                             Service.get_availability_zones(redis_az, redis_count)

                                     })

            redises.append(redis)
            itsdk.connect(collector_id=collector_id, source=asg, target=redis, topology="uses-redis$group")
            for ec2 in ec2s:
                itsdk.connect(collector_id=collector_id, source=ec2, target=redis, topology="uses-redis")

        # Create Elastic Search and connect them to the Microservice
        elastic_searches = []
        elastic_search_price = get_elastic_search_estimated_cost()
        for i in range(elastic_search_count):
            es = itsdk.add_vertex(collector_id=collector_id,
                                  name="ElasticSearch-{}".format(i),
                                  vertex_type="AWS_Elastic_Search",
                                  keys="{}vfl-service-{}-elastic-search{}".format(key_prefix, key_suffix, i),
                                  data={
                                      "instance-type": "c4.2xlarge.elasticsearch",
                                      "estimated-cost": elastic_search_price,
                                      "availability-zones":
                                          Service.get_availability_zones(elastic_search_az, elastic_search_count)
                                  })

            elastic_searches.append(es)
            itsdk.connect(collector_id=collector_id, source=asg, target=es, topology="uses-elastic-search$group")
            for ec2 in ec2s:
                itsdk.connect(collector_id=collector_id, source=ec2, target=es, topology="uses-elastic-search")

        # create the Microservice vertex
        service = itsdk.add_vertex(collector_id=collector_id,
                                   name=name,
                                   vertex_type="Service",
                                   keys="{}vfl-service-{}".format(key_prefix, key_suffix),
                                   data={
                                       "instance-type": "db.m4.2xlarge",
                                       "instance-count": ec2_count,
                                       "availability-zones": Service.get_availability_zones(list(service_az),
                                                                                            ec2_count),
                                       "estimated-cost": itsdk.PricePerPeriodDataType.value(
                                           value=total_price,
                                           visible=True,
                                           unit=itsdk.Units.MONTHLY)
                                   })

        itsdk.connect(collector_id=collector_id, source=service, target=elb, topology="use-elb")

        efs = None
        if efs_name:
            efs = itsdk.add_vertex(collector_id=collector_id,
                                   vertex_type="AWS_EFS",
                                   name=efs_name,
                                   keys="{}{}".format(key_prefix, efs_name),
                                   data={
                                       "estimated-cost": 561,
                                       "capacity": 561 * 3,
                                       "availability-zones": Service.get_availability_zones(efs_az, ec2_count)
                                   })
            itsdk.connect(collector_id=collector_id, source=asg, target=efs, topology="uses-efs$group")
            for ec2 in ec2s:
                itsdk.connect(collector_id=collector_id, source=ec2, target=efs, topology="uses-efs")

        return Service(service=service,
                       elb=elb,
                       asg=asg,
                       ec2s=ec2s,
                       rdses=rdses,
                       redshifts=redshifts,
                       redises=redises,
                       elastic_searches=elastic_searches,
                       efs=efs)

    @classmethod
    def get_availability_zones(cls, az, count):
        return az[0:count] if az else []
        # if az:
        #     return [{"zone-name": a} for a in az[0:count]]
        # else:
        #     return []
