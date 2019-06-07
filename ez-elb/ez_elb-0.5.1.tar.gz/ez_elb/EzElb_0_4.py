import collections
import hashlib
import json
import yaml

from troposphere import Template, Ref, Sub, GetAtt, Output, Export
from troposphere.cloudwatch import Alarm, MetricDimension
from troposphere.ec2 import SecurityGroup, SecurityGroupRule
from troposphere.ecs import TaskDefinition, ContainerDefinition, Environment, PortMapping, Service, \
    DeploymentConfiguration
from troposphere.ecs import LoadBalancer as EcsLoadBalancer
from troposphere.elasticloadbalancingv2 import LoadBalancer, Listener, ListenerRule, TargetGroup, Certificate, Action, \
    TargetDescription, Condition, Matcher, TargetGroupAttribute, LoadBalancerAttributes
from troposphere.route53 import RecordSetGroup, RecordSet


def alpha_numeric_name(s):
    return s.replace('-', 'DASH').replace('.', 'DOT').replace('_', 'US')


class ValidationException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)


class TargetHost(object):
    def __init__(self, host, port, protocol="HTTP"):
        self.host = host
        self.port = port
        self.protocol = protocol

        if host[0] == 'i':
            self.type = "instance"
        else:
            self.type = "ip"

    def to_target_desc(self):
        ret = TargetDescription(Id=self.host, Port=self.port)
        if self.type == "ip":
            # TODO: Support specifying the AZ
            ret.AvailabilityZone = "all"
        return ret


class HasHosts(object):
    def __init__(self):
        self.hosts = []

    def add_host(self, host, port, protocol="HTTP"):
        self.hosts += [TargetHost(host, port, protocol)]


class TargetPath(HasHosts):
    def __init__(self):
        super(TargetPath, self).__init__()
        self.health_check_matcher = Matcher(HttpCode="200-399")

    def set_health_check_codes(self, codes):
        self.health_check_matcher = Matcher(HttpCode=codes)


class AltListener(HasHosts):
    def __init__(self, port, protocol="HTTPS"):
        super(AltListener, self).__init__()
        self.port = port
        self.protocol = protocol


class EzElb(object):
    def __init__(self, env_name, vpc_id, name=None, internal=False):
        self.env_name = env_name
        self.vpc_id = vpc_id

        if len(env_name) > 10:
            raise ValidationException("env_name must be no more than 10 characters long")

        self.template = Template()
        self.subnet_ids = []
        self.cert_ids = []
        self.default_targets = []
        self.http_redirect_targets = []
        self.alt_listeners = []
        self.target_paths = collections.defaultdict(TargetPath)
        self._sticky = True
        self._json = None
        self._priority_cache = []
        self._global_tags = []
        self._alarm_topic = None
        self.alarm_namespace = "AWS/ApplicationELB"
        self._log_bucket = None
        self._ecs_redirect = False
        self.idle_timeout_seconds = 120
        self._custom_elb_sgs = None
        self._elb_name = name
        self._deletion_protection = False

        if internal:
            self._elb_scheme = "internal"
        else:
            self._elb_scheme = "internet-facing"

        self._sg_rules = [SecurityGroupRule(CidrIp="0.0.0.0/0", IpProtocol="tcp", FromPort=443, ToPort=443),
                          SecurityGroupRule(CidrIp="0.0.0.0/0", IpProtocol="tcp", FromPort=80, ToPort=80)]

        # The first call to allow() should clear the default _sg_rules,
        # subsequent calls should not.
        self._reset_sg_rules = True

    def deletion_protection(self, p):
        self._deletion_protection = p

    def allow(self, *rules):
        if self._reset_sg_rules:
            self._sg_rules = list(rules)
            self._reset_sg_rules = False
        else:
            self._sg_rules += list(rules)

    def allow_cidr(self, *cidrs):
        self.allow(*list(SecurityGroupRule(CidrIp=c, IpProtocol="tcp", FromPort=443, ToPort=443) for c in cidrs))
        self.allow(*list(SecurityGroupRule(CidrIp=c, IpProtocol="tcp", FromPort=80, ToPort=80) for c in cidrs))

    def custom_security_groups(self, *ids):
        self._custom_elb_sgs = list(ids)

    def priority_hash(self, name):
        ret = int(hashlib.md5(name).hexdigest(), 16) % 50000
        while ret in self._priority_cache:
            ret += 1
        self._priority_cache.append(ret)
        return ret

    def subnet_id(self, *ids):
        self.subnet_ids += list(ids)

    def certificate_id(self, *ids):
        self.cert_ids += list(ids)

    def alarm_topic(self, arn):
        self._alarm_topic = arn

    def dns(self, host, zone, ttl=3600):
        if not zone.endswith('.'):
            zone = zone + '.'
        self.template.add_resource(RecordSetGroup(
            ("RSG" + hashlib.sha1(zone + host).hexdigest())[:10],
            Comment=Ref("AWS::StackName"),
            HostedZoneName=zone,
            RecordSets=[RecordSet(
                Name="%s.%s" % (host, zone),
                Type="CNAME",
                ResourceRecords=[GetAtt("ELB", "DNSName")],
                TTL=ttl
            )]
        ))

    def global_tag(self, key, value):
        self._global_tags.append({'Key': key, 'Value': value})

    def tags_with(self, **kwargs):
        ret = []
        ret += self._global_tags
        for k, v in kwargs.iteritems():
            ret.append({'Key': k, 'Value': v})
        return ret

    def default_target(self, host, port, protocol="HTTP"):
        self.default_targets.append(TargetHost(host, port, protocol))

    def http_redirect_target(self, host, port):
        self.http_redirect_targets.append(TargetHost(host, port))

    def target(self, host, port, path,
               protocol="HTTP", health_check_codes=None):
        target_path = self.target_paths[path]
        target_path.add_host(host, port, protocol)
        if health_check_codes is not None:
            target_path.set_health_check_codes(health_check_codes)

    def log_bucket(self, bucket):
        self._log_bucket = bucket

    def alt_listener(self, port, protocol="HTTPS"):
        ret = AltListener(port, protocol)
        self.alt_listeners.append(ret)
        return ret

    def elb_attributes(self):
        ret = [
            LoadBalancerAttributes(Key="idle_timeout.timeout_seconds",
                                   Value=str(self.idle_timeout_seconds)),
            LoadBalancerAttributes(Key="routing.http2.enabled",
                                   Value="true"),
            LoadBalancerAttributes(Key="deletion_protection.enabled",
                                   Value="true" if self._deletion_protection else "false")
        ]
        if self._log_bucket is not None:
            ret += [
                LoadBalancerAttributes(Key="access_logs.s3.enabled",
                                       Value="true"),
                LoadBalancerAttributes(Key="access_logs.s3.bucket",
                                       Value=self._log_bucket),
                LoadBalancerAttributes(Key="access_logs.s3.prefix",
                                       Value=Sub("${AWS::StackName}-ElbLogs"))
            ]
        return ret

    def attach_alarm(self, target_group):
        """

        :type target_group: TargetGroup
        """
        if self._alarm_topic is not None:
            self.template.add_resource(Alarm(
                target_group.title + "UnhealthyHostAlarm",
                AlarmName=Sub("${AWS::StackName}-UnhealthyHosts-" + target_group.title),
                AlarmDescription="Unhealthy hosts in target group: %s/%s" % (self.env_name, target_group.title),
                MetricName="UnHealthyHostCount",
                Namespace=self.alarm_namespace,
                Statistic="Minimum",
                Period=120,
                EvaluationPeriods=2,
                Threshold='0',
                AlarmActions=[self._alarm_topic],
                ComparisonOperator="GreaterThanThreshold",
                Dimensions=[
                    MetricDimension(Name="TargetGroup", Value=GetAtt(target_group, "TargetGroupFullName")),
                    MetricDimension(Name="LoadBalancer", Value=GetAtt("ELB", "LoadBalancerFullName"))
                ]
            ))

    def ecs_redirect(self, cluster, url):
        self._ecs_redirect = True
        self.template.add_resource(TaskDefinition(
            "RedirectTaskDef",
            Volumes=[],
            Family=Sub("${AWS::StackName}-redirect"),
            NetworkMode="bridge",
            ContainerDefinitions=[ContainerDefinition(
                Name="redirect",
                Cpu=1,
                Environment=[Environment(Name="REDIRECT", Value=url)],
                Essential=True,
                Hostname=Sub("${AWS::StackName}-redirect"),
                Image="cusspvz/redirect:0.0.2",
                Memory=512,
                MemoryReservation=128,
                PortMappings=[PortMapping(
                    ContainerPort=80,
                    Protocol="tcp"
                )]
            )]
        ))

        self.template.add_resource(Service(
            "RedirectService",
            TaskDefinition=Ref("RedirectTaskDef"),
            Cluster=cluster,
            DesiredCount=1,
            DeploymentConfiguration=DeploymentConfiguration(
                MaximumPercent=200,
                MinimumHealthyPercent=100
            ),
            LoadBalancers=[EcsLoadBalancer(
                ContainerName="redirect",
                ContainerPort=80,
                TargetGroupArn=Ref("DefaultTargetGroup")
            )]
        ))

    @property
    def sticky(self):
        return self._sticky

    @sticky.setter
    def sticky(self, b):
        self._sticky = b

    def to_yaml(self):
        return yaml.safe_dump(json.loads(self.to_json()), encoding='utf-8')

    def to_json(self):
        if self._json is not None:
            return self._json

        # Validity checks
        if len(self.subnet_ids) < 2:
            raise ValidationException("Use .subnet_id() to specify at least two ELB subnets")
        if len(self.cert_ids) < 1:
            raise ValidationException("Use .certificate_id() to specify at least one certificate")
        if not self._ecs_redirect and len(self.default_targets) < 1:
            raise ValidationException("Use .default_target() to specify at least one default target or .ecs_redirect("
                                      ") to set up a redirect container")
        for (name, tp) in self.target_paths.iteritems():
            if len(set(map(lambda h: h.type, tp.hosts))) != 1:
                raise ValidationException("Inconsistent target types for %s. All hosts for a given path must have the "
                                          "same type (ip or instance)." % name)

        # Build Security Group
        if self._custom_elb_sgs:
            elb_sgs = self._custom_elb_sgs
        else:
            elb_sg = SecurityGroup(
                "ElbSecurityGroup",
                GroupDescription=Sub("${AWS::StackName}-ElbSg"),
                Tags=self.tags_with(Name=Sub("${AWS::StackName}-ElbSg")),
                VpcId=self.vpc_id,
                SecurityGroupEgress=[SecurityGroupRule(CidrIp="0.0.0.0/0", IpProtocol="-1")],
                SecurityGroupIngress=self._sg_rules
            )
            self.template.add_resource(elb_sg)
            self.template.add_output(Output(
                "ElbSecurityGroupOutput",
                Description="Security group ID assigned to the ELB",
                Value=Ref(elb_sg),
                Export=Export(Sub("${AWS::StackName}-ElbSg"))
            ))

            # Build Attachment Security Group
            inst_sg = SecurityGroup(
                "InstanceSecurityGroup",
                GroupDescription=Sub("${AWS::StackName}-InstSg"),
                Tags=self.tags_with(Name=Sub("${AWS::StackName}-InstSg")),
                VpcId=self.vpc_id,
                SecurityGroupEgress=[SecurityGroupRule(CidrIp="0.0.0.0/0", IpProtocol="-1")],
                SecurityGroupIngress=[
                    SecurityGroupRule(IpProtocol="-1", SourceSecurityGroupId=Ref(elb_sg))
                ]
            )
            self.template.add_resource(inst_sg)
            self.template.add_output(Output(
                "InstanceSecurityGroupOutput",
                Description="Convenience SG to assign to instances",
                Value=Ref(inst_sg),
                Export=Export(Sub("${AWS::StackName}-InstSg"))
            ))
            elb_sgs = [Ref("ElbSecurityGroup")]

        # Build ELB
        elb = LoadBalancer(
            "ELB",
            SecurityGroups=elb_sgs,
            Scheme=self._elb_scheme,
            Subnets=self.subnet_ids,
            Tags=self.tags_with(Name=Ref("AWS::StackName")),
            LoadBalancerAttributes=self.elb_attributes()
        )
        if self._elb_name:
            elb.Name = self._elb_name
        self.template.add_resource(elb)
        self.template.add_output(Output(
            "ElbArnOutput",
            Description="ARN of the ELB",
            Value=Ref(elb),
            Export=Export(Sub("${AWS::StackName}-ElbArn"))
        ))
        self.template.add_output(Output(
            "ElbDnsOutput",
            Description="DNS name of the ELB",
            Value=GetAtt("ELB", "DNSName"),
            Export=Export(Sub("${AWS::StackName}-ElbDns"))
        ))

        # Build Default Target Group
        if self._ecs_redirect:
            default_tg_protocol = "HTTP"
        else:
            default_tg_protocol = self.default_targets[0].protocol
        default_tg = TargetGroup(
            "DefaultTargetGroup",
            Port=8080,
            Protocol=default_tg_protocol,
            Tags=self.tags_with(Name=Sub("${AWS::StackName}-Default")),
            VpcId=self.vpc_id,
            Targets=list(map(lambda h: TargetDescription(Id=h.host, Port=h.port), self.default_targets)),
            HealthyThresholdCount=2,
            Matcher=Matcher(HttpCode="200-399")
        )
        self.template.add_resource(default_tg)
        self.attach_alarm(default_tg)

        # Build Listener
        self.template.add_resource(Listener(
            "HttpsListener",
            Certificates=list(map(lambda i: Certificate(CertificateArn=i), self.cert_ids)),
            DefaultActions=[Action(Type="forward", TargetGroupArn=Ref("DefaultTargetGroup"))],
            LoadBalancerArn=Ref("ELB"),
            Port=443,
            Protocol="HTTPS"
        ))

        # Build HTTP redirect
        if len(self.http_redirect_targets) > 0:
            # Build Redirect Target Group
            http_tg = TargetGroup(
                "RedirectTargetGroup",
                Port=8080,
                Protocol=self.http_redirect_targets[0].protocol,
                Tags=self.tags_with(Name=Sub("${AWS::StackName}-Redirect")),
                VpcId=self.vpc_id,
                Targets=list(map(lambda h: TargetDescription(Id=h.host, Port=h.port), self.http_redirect_targets)),
                HealthyThresholdCount=2,
                Matcher=Matcher(HttpCode="200-399")
            )
            self.template.add_resource(http_tg)
            self.attach_alarm(http_tg)

        if self._ecs_redirect or len(self.http_redirect_targets) > 0:
            if self._ecs_redirect:
                redirect_tg = "DefaultTargetGroup"
            else:
                redirect_tg = "RedirectTargetGroup"
            # Build Listener
            self.template.add_resource(Listener(
                "HttpListener",
                DefaultActions=[Action(Type="forward", TargetGroupArn=Ref(redirect_tg))],
                LoadBalancerArn=Ref("ELB"),
                Port=80,
                Protocol="HTTP"
            ))

        # Build Target Groups & Rules
        for (name, tp) in self.target_paths.iteritems():
            name_an = alpha_numeric_name(name)

            g = TargetGroup(
                "PathTg" + name_an,
                Port=tp.hosts[0].port,
                Protocol=tp.hosts[0].protocol,
                Tags=self.tags_with(Name="%s/%s" % (self.env_name, name), TargetPath=name),
                Targets=list(map(lambda h: h.to_target_desc(), tp.hosts)),
                VpcId=self.vpc_id,
                HealthCheckPath="/%s" % name,
                HealthyThresholdCount=2,
                Matcher=tp.health_check_matcher
            )

            # TODO: We should probably explicitly specify this for every TG. Not
            #       doing that now because it will cause lots of updates. Maybe
            #       in 0.4?
            if len(tp.hosts) > 0 and tp.hosts[0].type != "instance":
                g.TargetType = tp.hosts[0].type

            if self.sticky:
                g.TargetGroupAttributes = [
                    TargetGroupAttribute(Key="stickiness.enabled", Value="true"),
                    TargetGroupAttribute(Key="stickiness.type", Value="lb_cookie")
                ]
            self.template.add_resource(g)
            self.attach_alarm(g)
            self.template.add_resource(ListenerRule(
                "PathRl" + name_an,
                Actions=[Action(Type="forward", TargetGroupArn=Ref(g))],
                Conditions=[Condition(Field="path-pattern", Values=["/%s/*" % name])],
                ListenerArn=Ref("HttpsListener"),
                Priority=self.priority_hash(name)
            ))
            self.template.add_resource(ListenerRule(
                "PathRln" + name_an,
                Actions=[Action(Type="forward", TargetGroupArn=Ref(g))],
                Conditions=[Condition(Field="path-pattern", Values=["/%s" % name])],
                ListenerArn=Ref("HttpsListener"),
                Priority=self.priority_hash(name)
            ))

        # Build Alternate Listeners
        for al in self.alt_listeners:
            tg_name = "AltTg%d" % al.port
            tg_protocol = al.hosts[0].protocol
            tg = TargetGroup(
                tg_name,
                Port=9999,
                Protocol=tg_protocol,
                Tags=self.tags_with(Name=Sub("${AWS::StackName}-%s" % tg_name)),
                VpcId=self.vpc_id,
                Targets=list(map(lambda h: TargetDescription(Id=h.host, Port=h.port), al.hosts)),
                HealthyThresholdCount=2,
                Matcher=Matcher(HttpCode="200-399")
            )
            self.template.add_resource(tg)
            self.attach_alarm(tg)

            listener = Listener(
                "AltListener%d" % al.port,
                DefaultActions=[Action(Type="forward", TargetGroupArn=Ref(tg_name))],
                LoadBalancerArn=Ref("ELB"),
                Port=al.port,
                Protocol=al.protocol
            )

            if al.protocol == "HTTPS":
                listener.Certificates = list(map(lambda i: Certificate(CertificateArn=i), self.cert_ids))

            self.template.add_resource(listener)

        self._json = self.template.to_json()
        return self._json
