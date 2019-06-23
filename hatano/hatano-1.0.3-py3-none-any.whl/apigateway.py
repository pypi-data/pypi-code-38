from hatano.util import region
from hatano.errors import HatanoError

import boto3
import os


class ResourceContainer:
    def __init__(self, rest_id, resource, path, agw):
        self.rest_id = rest_id
        self.resource = resource
        self.path = path
        self.agw = agw

    def link_endpoint(self, method, arn):
        self._put_method(method)
        self._put_integration(method, arn)

    def _put_method(self, http_method):
        method = self.agw.put_method(
                restApiId=self.rest_id,
                resourceId=self.resource['id'],
                httpMethod=http_method,
                authorizationType='NONE')

    def _put_integration(self, http_method, arn):
        uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations"
        integration = self.agw.put_integration(
                restApiId=self.rest_id,
                resourceId=self.resource['id'],
                httpMethod=http_method.upper(),
                integrationHttpMethod="POST",
                uri=uri,
                type="AWS_PROXY")


class RestApi:
    def __init__(self, name):
        self.agw = boto3.client('apigateway')
        apis = self.agw.get_rest_apis()
        for api in apis['items']:
            if api['name'] == name:
                self.api = api
                break
        else:
            self.api = self.agw.create_rest_api(
                    name=name,
                    description="Created automatically by Hatano")

        self.rest_id = self.api['id']
        self.url = f"https://{self.rest_id}.execute-api.{region}.amazonaws.com"
        self.resources = self.agw.get_resources(
                restApiId=self.rest_id)['items']
        root = self.get_resource_by_path('/')
        self.root_id = root['id']

    def get_resource_by_path(self, path):
        for resource in self.resources:
            if resource['path'] == path:
                return resource
        return None

    def _create_resource(self, http_fullpath):
        resource = self.get_resource_by_path(http_fullpath)
        if resource:
            return resource

        base, http_path = os.path.split(http_fullpath)
        parent = self.get_resource_by_path(base)
        if not parent:
            parent = self._create_resource(base)

        resource = self.agw.create_resource(
                restApiId=self.rest_id,
                parentId=parent['id'],
                pathPart=http_path)

        self.resources.append(resource)
        return resource

    def create_resource(self, http_fullpath):
        resource = self._create_resource(http_fullpath)
        r = ResourceContainer(
                self.rest_id,
                resource,
                http_fullpath,
                self.agw)
        return r

    def put_method(self, path, http_method):
        try:
            resource = self.get_resource_by_path(path)
        except HatanoError:
            print(f"Put method failed.  Resource does not exist: {path}")
            return

        method = self.agw.put_method(
                restApiId=self.rest_id,
                resourceId=resource['id'],
                httpMethod=http_method,
                authorizationType='NONE')

    def put_integration(self, path, http_method, arn):
        try:
            resource = self.get_resource_by_path(path)
        except HatanoError:
            print(f"Put integration failed.  Resource does not exist: {path}")
            return
    
        uri = f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations"
        integration = self.agw.put_integration(
                restApiId=self.rest_id,
                resourceId=resource['id'],
                httpMethod=http_method.upper(),
                integrationHttpMethod="POST",
                uri=uri,
                type="AWS_PROXY")

    def deploy(self, stage):
        self.agw.create_deployment(
                restApiId=self.rest_id,
                stageName=stage)


    def create_domain(self, domain, cert_arn):
        return self.agw.create_domain_name(
                domainName=domain,
                certificateArn=cert_arn)

    def create_base_path_mapping(self, domain, path, stage):
        self.agw.create_base_path_mapping(
                restApiId=self.rest_id,
                domainName=domain,
                basePath=path,
                stage=stage)


