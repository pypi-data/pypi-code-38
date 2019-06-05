import boto3
import six


class AwsBase(object):
    def __init__(self, aws_ctx, org):
        self.ctx = aws_ctx
        self.org = org

    @classmethod
    def client(cls, name, aws_ctx):
        return boto3.client(name, region_name=aws_ctx.region)

    @classmethod
    def resource(cls, name, aws_ctx):
        return boto3.resource(name, region_name=aws_ctx.region)

    @classmethod
    def ensure_str(cls, value):
        if isinstance(value, bytes):
            return value.decode('utf-8')

        if isinstance(value, six.string_types):
            return value

        if value is None:
            return ''

        return str(value)
