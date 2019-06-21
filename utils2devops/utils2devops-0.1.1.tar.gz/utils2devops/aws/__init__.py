def begin_block():
    # todo to read from config file
    return '{\n'


def end_block():
    # todo to read from config file
    return '}\n\n'


def format_item(name, value, indent: int = 1):
    """
    Format the data
    :param name:
    :param value:
    :param indent:
    :return:
    """
    return '\t' * indent + name + ' = "' + value + '"\n'


def format_item_bool(name, value, indent: int = 1):
    """
    Format the data in boolean
    :param name:
    :param value:
    :param indent:
    :return:
    """
    return '\t' * indent + name + ' = ' + 'true\n' \
        if value else 'false\n'


def format_item_cond(name, value, indent: int = 1):
    """
    Format the data if the data not None
    :param name:
    :param value:
    :param indent:
    :return:
    """
    if value is not None:
        return '\t' * indent + name + ' = "' + value + '"\n'
    else:
        return ''


class BlockTypeBase:
    """
    Described at: https://www.terraform.io/docs/configuration/index.html \n
    Generate the base block type with the format:

    <BLOCK TYPE> "<BLOCK LABEL>" "<BLOCK NAME>" {
      # Block body
      <IDENTIFIER> = <EXPRESSION> # Argument
    }

    """
    def __init__(self, btype, label, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        self.type = btype
        self.label = label
        self.name = name

    def __str__(self):
        return self.type + ' "' + self.label + '" "' + self.name + '" ' + begin_block()


class BlockTypeWithTagsBase(BlockTypeBase):
    """
    Described at: https://www.terraform.io/docs/configuration/index.html \n
    Generate the base block type with tags with the format:

    <BLOCK TYPE> "<BLOCK LABEL>" "<BLOCK NAME>" {
      # Block body
      <IDENTIFIER> = <EXPRESSION> # Argument
    }

    """
    def __init__(self, btype, label, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(BlockTypeWithTagsBase, self).__init__(
            btype='resource', label=label, name=name)
        self.tags = []

    def add_str_tags(self):
        the_str = '\ttags {\n'
        tags = self.tags
        if type(tags) == list:
            for tag in self.tags:
                if 'Key' in tag:
                    the_str += '\t\t"' + tag['Key'] + '" = "' + tag['Value'] + '"\n'
                else:
                    raise NotImplementedError()
                    # the_str += '\t\t"' + tag[0] + '" = "' + tag[1] + '"\n'
        else:
            for tag in self.tags.items():
                if 'Key' in tag:
                    raise NotImplementedError()
                    # the_str += '\t\t"' + tag['Key'] + '" = "' + tag['Value'] + '"\n'
                else:
                    the_str += '\t\t"' + tag[0] + '" = "' + tag[1] + '"\n'
        the_str += '\t}\n'
        return the_str


"""
Virtual Private Cloud
"""


class Vpc(BlockTypeWithTagsBase):
    """
    Virtual Private Cloud
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(Vpc, self).__init__(
            btype='resource', label='aws_vpc', name=name)
        self.cidr_block = ''
        self.enable_dns_hostnames = 'true'
        self.enable_dns_support = 'true'
        self.instance_tenancy = 'default'

    def __str__(self):
        the_str = super(Vpc, self).__str__()
        the_str += format_item('tcidr_block', self.cidr_block)
        the_str += format_item_bool('enable_dns_hostnames', self.enable_dns_hostnames)
        the_str += format_item_bool('enable_dns_support', self.enable_dns_support)
        the_str += format_item('instance_tenancy', self.instance_tenancy)
        the_str += self.add_str_tags()
        the_str += end_block()
        return the_str


class Subnet(BlockTypeWithTagsBase):
    """
    Subnet
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(Subnet, self).__init__(
            btype='resource', label='aws_subnet', name=name)
        self.vpc_id = ''
        self.cidr_block = ''
        self.availability_zone = ''
        self.map_public_ip_on_launch = True

    def __str__(self):
        if any('Name' in d['Key'] for d in self.tags):
            for tag in self.tags:
                if tag['Key'] == 'Name':
                    self.name = self.name + '-' + tag['Value']
                    break
        the_str = super(Subnet, self).__str__()
        the_str += format_item('vpc_id', self.vpc_id)
        the_str += format_item('cidr_block', self.cidr_block)
        the_str += format_item('availability_zone', self.availability_zone)
        the_str += format_item_bool('map_public_ip_on_launch', self.map_public_ip_on_launch)
        the_str += self.add_str_tags()
        the_str += end_block()
        return the_str


class InternetGateway(BlockTypeWithTagsBase):
    """
    Internet Gateway
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(InternetGateway, self).__init__(
            btype='resource', label='aws_internet_gateway', name=name)
        self.vpc_id = ''

    def __str__(self):
        the_str = super(InternetGateway, self).__str__()
        the_str += format_item('vpc_id', self.vpc_id)
        the_str += self.add_str_tags()
        the_str += end_block()
        return the_str


class RouteTable(BlockTypeWithTagsBase):
    """
    Route Table
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(RouteTable, self).__init__(
            btype='resource', label='aws_route_table', name=name)
        self.vpc_id = ''
        self.route = {
            'cidr_block': '',
            'gateway_id': '',
        }

    def __str__(self):
        the_str = super(RouteTable, self).__str__()
        the_str += format_item('vpc_id', self.vpc_id)
        the_str += '\n\troute {\n'
        the_str += format_item('cidr_block', self.route['cidr_block'], 2)
        the_str += format_item('gateway_id', self.route['gateway_id'], 2)
        the_str += '\t}\n'
        the_str += self.add_str_tags()
        the_str += end_block()
        return the_str


"""
Security
"""


class Gress:
    """
    Gress part
    """
    def __init__(self, _=''):
        """
        Create new object, called automatically

        :param _:
        """
        self.rule_no = 100
        self.action = 'deny'
        self.cidr_block = "0.0.0.0/0"
        self.ipv6_cidr_block = ""
        self.protocol = "-1"
        self.from_port = 0
        self.to_port = 0
        self.icmp_code = 0
        self.icmp_type = 0

    def __str__(self):
        the_str = '\t\trule_no = "' + str(self.rule_no) + '"\n'
        the_str += '\t\taction = "' + self.action + '"\n'
        the_str += '\t\tcidr_block = "' + self.cidr_block + '"\n'
        the_str += '\t\tipv6_cidr_block = "' + self.ipv6_cidr_block + '"\n'
        the_str += '\t\tprotocol = "' + self.protocol + '"\n'
        the_str += '\t\tfrom_port = ' + str(self.from_port) + '\n'
        the_str += '\t\tto_port = ' + str(self.to_port) + '\n'
        the_str += '\t\ticmp_code = ' + str(self.icmp_code) + '\n'
        the_str += '\t\ticmp_type = ' + str(self.icmp_type) + '\n'
        return the_str

    @staticmethod
    def format_items(name, values, indent: int = 1):
        """
        Format the data
        :param name:
        :param value:
        :param indent:
        :return:
        """
        the_str = ''
        for i in values:
            the_str += '\t' * indent + name + ' ' + begin_block()
            the_str += str(i)
            the_str += '\t' * indent + end_block()
        return the_str


class NetworkAcl(BlockTypeWithTagsBase):
    """
    Network Acl
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(NetworkAcl, self).__init__(
            btype='resource', label='aws_network_acl', name=name)
        self.vpc_id = ''
        self.subnet_ids = []
        self.ingress = []
        self.egress = []

    def __str__(self):
        if any('Name' in d['Key'] for d in self.tags):
            for tag in self.tags:
                if tag['Key'] == 'Name' and tag['Value'] not in self.name:
                    self.name = self.name + '-' + tag['Value']
                    break
        the_str = super(NetworkAcl, self).__str__()
        the_str += format_item('vpc_id', self.vpc_id)
        the_str += '\tsubnet_ids = ['
        for sid in self.subnet_ids:
            the_str += '"' + sid + '",'
        the_str += ']\n\n'
        the_str += Gress.format_items('ingress', self.ingress)
        the_str += Gress.format_items('egress', self.egress)
        the_str += self.add_str_tags()
        the_str += end_block()
        return the_str


class SecurityGroup(BlockTypeBase):
    """
    Security Group
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(SecurityGroup, self).__init__(
            btype='resource', label='aws_security_group', name=name)
        self.name = ''
        self.description = ''
        self.vpc_id = ''
        self.ingress = []
        self.egress = []

    def __str__(self):
        the_str = super(SecurityGroup, self).__str__()
        the_str += format_item('name', self.name)
        the_str += format_item('description', self.description)
        the_str += format_item('vpc_id', self.vpc_id)
        for i in self.ingress:
            the_str += '\n\tingress {\n'
            the_str += str(i)
            the_str += '\t}\n'
        for e in self.egress:
            the_str += '\n\tegress {\n'
            the_str += str(e)
            the_str += '\t}\n'
        the_str += '}\n'
        return the_str


"""
Lambda
"""


class Lambda(BlockTypeWithTagsBase):
    """
    Lambda
    https://www.terraform.io/docs/providers/aws/r/lambda_function.html
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(Lambda, self).__init__(
            btype='resource', label='aws_lambda_function', name=name)
        self.ofilename = None
        self.os3_bucket = None
        self.os3_key = None
        self.os3_object_version = None
        self.function_name = ''
        self.odead_letter_config = None
        self.handler = ''
        self.role = ''
        self.odescription = None
        self.olayers = None
        self.omemory_size = None
        self.runtime = ''
        self.otimeout = None
        self.oreserved_concurrent_executions = None
        self.opublish = None
        self.ovpc_config = None
        self.oenvironment = None
        self.okms_key_arn = None
        self.osource_code_hash = None
        self.otarget_arn = None
        self.osubnet_ids = None
        self.osecurity_group_ids = None

    def __str__(self):
        the_str = super(Lambda, self).__str__()
        the_str += format_item_cond('filename', self.ofilename)
        the_str += format_item_cond('s3_bucket', self.os3_bucket)
        the_str += format_item_cond('s3_key', self.os3_key)
        the_str += format_item_cond('s3_object_version', self.os3_object_version)
        the_str += format_item('function_name', self.function_name)
        the_str += format_item_cond('dead_letter_config', self.odead_letter_config)
        the_str += format_item('handler', self.handler)
        the_str += format_item('role', self.role)
        the_str += format_item_cond('description', self.odescription)
        if self.olayers:
            the_str += '\tlayers = {' + self.olayers + '"\n'
            for layer in self.olayers:
                the_str += '\t\t"' + layer['Key'] + '" = "' + layer['Value'] + '"\n'
            the_str += '\t}\n'
        the_str += format_item_cond('memory_size', str(self.omemory_size))
        the_str += format_item('runtime', self.runtime)
        the_str += format_item_cond('timeout', str(self.otimeout))
        the_str += format_item_cond('reserved_concurrent_executions',
                                        self.oreserved_concurrent_executions)
        the_str += format_item_cond('publish', self.opublish)
        the_str += format_item_cond('vpc_config', self.ovpc_config)
        if self.oenvironment:
            the_str += '\tenvironment {\n'
            the_str += '\n\tvariables = {\n'
            for k, v in self.oenvironment.items():
                the_str += '\t\t"' + k + '" = "' + v + '"\n'
            the_str += '\t}\n'
        the_str += format_item_cond('kms_key_arn', self.okms_key_arn)
        the_str += format_item_cond('source_code_hash', self.osource_code_hash)
        the_str += self.add_str_tags()
        the_str += format_item_cond('target_arn', self.otarget_arn)
        the_str += format_item_cond('subnet_ids', self.osubnet_ids)
        the_str += format_item_cond('security_group_ids', self.osecurity_group_ids)
        the_str += '}\n'
        return the_str


"""
S3
"""


class S3Bucket(BlockTypeBase):
    """
    S3 Bucket
    https://www.terraform.io/docs/providers/aws/r/s3_bucket.html
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(S3Bucket, self).__init__(
            btype='resource', label='aws_s3_bucket', name=name)
        self.bucket = None
        self.acl = None
        self.versioning = None

    def __str__(self):
        the_str = super(S3Bucket, self).__str__()
        the_str += format_item('bucket', self.bucket)
        the_str += format_item_cond('acl', self.acl)
        if self.versioning:
            the_str += '\tversioning {\n\t\tenabled = ' + self.versioning + '\n\t}\n'
        the_str += end_block()
        # todo
        return the_str


"""
ApiGatewayV2
"""


class ApiGatewayV2(BlockTypeBase):
    """
    Api Gateway V2
    todo
    """
    def __init__(self, name=''):
        """
        Create new object, called automatically

        :param name:
        """
        super(ApiGatewayV2, self).__init__(
            btype='resource', label='aws_api_gateway_v2', name=name)
        # todo

    def __str__(self):
        the_str = super(ApiGatewayV2, self).__str__()
        the_str += end_block()
        # todo
        return the_str
