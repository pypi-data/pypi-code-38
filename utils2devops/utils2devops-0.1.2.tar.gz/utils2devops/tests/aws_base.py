from weakref import WeakValueDictionary


class Singleton(type):
    """
    from https://stackoverflow.com/questions/43619748/destroying-a-singleton-object-in-python
    A Sigleton

    Instead of defining a custom method for deleting the instance reference
    use a WeakValueDictionary.
    Now when there are no more references of MockObject anywhere it will be
    cleaned up from Singleton._instances automatically.
    """
    _instances = WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # This variable declaration is required to force a
            # strong reference on the instance.
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonClient(metaclass=Singleton):
    """
    Singleton Client, maybe that is a wrong way and we will need more to one
    but we will see, but it's for unit test and that should be enough.
    """

    def __init__(self, service_name: str, region_name: str):
        """
        Overwrite the new operator to return always the same instance,
        if the instance already exist we don't modify it, we just
        return it.

        :param service_name: a string with the name of service in AWS
        :param region_name: The AWS region to use.
        :return:
        """
        if service_name not in ['ec2', 'lambda', 's3']:
            message = 'the service name is not implemented or do not exist'
            self.error = message
            raise Exception(message)
        self.service_name = service_name
        if region_name not in ['us-east-1', 'us-east-2']:
            message = 'the region name is not implemented or do not exist'
            self.error = message
            raise Exception(message)
        self.region_name = region_name
        self.lambda_functions = {}
        self.lambda_conf = {}
        self.network_acls_elements = []
        self.s3_bucket_data = []
        self.error = None

    def describe_network_acls(self):
        if self.service_name == 'ec2':
            return self.network_acls_elements
        else:
            return []

    @staticmethod
    def get_public_access_block(Bucket):
        return {'PublicAccessBlockConfiguration': {'BlockPublicAcls': 'private'}}

    def list_buckets(self):
        if self.service_name == 's3':
            return self.s3_bucket_data
        return []

    def list_functions(self):
        if self.service_name == 'lambda':
            return self.lambda_functions
        return []

    def get_function(self, FunctionName):
        if self.service_name == 'lambda':
            return self.lambda_conf
        return []


class SingletonResource(metaclass=Singleton):
    """
    Singleton Client, maybe that is a wrong way and we will need more to one
    but we will see, but it's for unit test and that should be enough.
    """

    class _Conf:
        status = 'Disabled'

    def __init__(self, service_name: str, region_name: str):
        """
        Overwrite the new operator to return always the same instance,
        if the instance already exist we don't modify it, we just
        return it.

        :param service_name: a string with the name of service in AWS
        :param region_name: The AWS region to use.
        :return:
        """
        if service_name not in ['lambda', 's3']:
            message = 'the service name is not implemented or do not exist'
            self.error = message
            raise Exception(message)
        self.service_name = service_name
        if region_name not in ['us-east-1', 'us-east-2']:
            message = 'the region name is not implemented or do not exist'
            self.error = message
            raise Exception(message)
        self.region_name = region_name
        self.profile_exist = True
        self.conf = SingletonResource._Conf

    def BucketVersioning(self, bucket_name):
        return self.conf

    # def Bucket(self, bucket_name):
    #     return self
    #
    # def put_object(self, Key=None, Body=None, ACL='', Expires='', ContentType=''):
    #     # We do nothing here, but return the same data type without data
    #     return {}


class SingletonSession(metaclass=Singleton):
    """
    Singleton Client, maybe that is a wrong way and we will need more to one
    but we will see, but it's for unit test and that should be enough.
    """

    def __init__(self, profile_name: str):
        """
        Overwrite the new operator to return always the same instance,
        if the instance already exist we don't modify it, we just
        return it.

        :param profile_name: The AWS profile name to use.
        :return:
        """
        self.profile_name = profile_name
        self.profile_exist = True
        self.singletonClient = None

    # def __init__(self, profile_name: str):
    #     self.profile_name = profile_name
    #     # self.service_name = None
    #     # self.region_name = None
    #     self.client = None
    #     self.s3_bucket_data = None

    def client(self, service_name: str, region_name: str):
        # self.service_name = service_name
        # self.region_name = region_name
        self.singletonClient = SingletonClient(service_name, region_name)
        return self.singletonClient

    # def resource(self, name):
    #     return FakeResource()


if __name__ == '__main__':
    m = SingletonSession(profile_name='test1')
    n = SingletonSession(profile_name='test2')
    print(dict(Singleton._instances))
    del m
    print(dict(Singleton._instances))
    del n
    print(dict(Singleton._instances))
