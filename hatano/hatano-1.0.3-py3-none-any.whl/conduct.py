from hatano.util import Conf
from hatano.iam import IamRole
from hatano.lmbda import Lambda
from hatano.apigateway import RestApi
from hatano.acm import Cert
from hatano.route53 import Route53
from hatano.s3 import S3
from hatano.errors import HatanoError

import os
import threading


class Conductor:
    def __init__(self, args):
        self.args = args
        c = Conf()
        if not c.exists():
            raise HatanoError("No config file found")
        self.conf = c.read()
        self.stage = args.stage
        self.project = self.conf["project"]
        stages = self.conf.get("stage", {})
        self.stg_conf = stages.get(self.stage, {})

        self.functions = []
        if args.function:
            self.functions = args.function
        else:
            self.functions = self.conf.get("function", {}).keys()

        self.api = None
        self.s3_path = self.stg_conf.get("bucket")
        self.s3 = None
        self.certified = False
        self.domain = ""
        if self.s3_path:
            self.s3 = S3(self.s3_path, self.project, self.stage)

        if not self.stg_conf:
            raise HatanoError(f"Stage {self.stage} not defined")

    def update(self):
        if self.args.bucket:
            self.deploy_s3()
        self.update_funcs()
        self.finish()

    def update_funcs(self):
        self.create_api()
        new = False
        threads = []
        for fname in self.functions:
            print(f"Updating function {fname}")
            try:
                self.update_func(fname)
            except:
                print(f"Function {fname} doesn't exist.  Creating...")
                t = threading.Thread(target=self.deploy_func, args=(fname,))
                threads.append(t)
                t.start()
                #self.deploy_func(fname)
                new = True
        for t in threads:
            t.join()
        if new:
            self.deploy_api()

    def update_func(self, name):
        fn = self.conf["function"][name]
        fn["name"] = name
        if self.s3:
            if "env" not in fn:
                fn["env"] = {}
            fn["env"]["DEFAULT_BUCKET"] = self.s3.name()

        lmb = Lambda(self.stage, fn)
        lmb.update_function()

    def deploy(self):
        self.deploy_s3()
        self.create_api()
        self.deploy_funcs()
        self.deploy_api()
        self.deploy_domain()
        self.finish()

    def deploy_s3(self):
        if self.s3:
            try:
                print(f"Creating s3 bucket {self.s3.name()}")
                self.s3.create()
            except Exception as e:
                print(f"Failed: {e}")
            
            try:
                print(f"Uploading contents of {self.s3_path} to s3 bucket {self.s3.name()}")
                self.s3.upload_all()
            except Exception as e:
                print(f"Failed: {e}")

    def create_api(self):
        # Create REST API
        print(f"Creating REST API for {self.project}")
        self.api = RestApi(self.project)

    def deploy_api(self):
        # Deploy the API
        print(f"Deploying API stage {self.stage}")
        self.api.deploy(self.stage)

    def deploy_funcs(self):
        # Create each function and link to and endpoint
        threads = []
        for fname in self.functions:
            print(f"Deploying function {fname}")
            t = threading.Thread(target=self.deploy_func, args=(fname,))
            threads.append(t)
            t.start()
            #self.deploy_func(fname)
        for t in threads:
            t.join()

    def deploy_func(self, name):
        if not self.api:
            self.api = RestApi(self.stage)

        fn = self.conf["function"][name]
        fn["name"] = name
        fn["runtime"] = self.conf["runtime"]
        if self.s3:
            if "env" not in fn:
                fn["env"] = {}
            fn["env"]["DEFAULT_BUCKET"] = self.s3.name()

        fullname = f"{self.project}-{name}-{self.stage}"
    
        http_method = fn.get("method", "")
        http_path = fn.get("path")
    
        # Create iam role
        print(f"  - Creating IAM role ({name})")
        iam = IamRole(self.stage, fn)
        role = iam.lambda_role()
        iam.put_custom_policy()
        role_arn = role['Role']['Arn']
    
        # Create lambda
        print(f"  - Creating lambda ({name})")
        lmb = Lambda(self.stage, fn, role_arn=role_arn)
        func = lmb.create_function()
        func_arn = func['FunctionArn']
        lmb.add_permission("apigateway", "InvokeFunction")
    
        # Create resource and endpoint
        print(f"  - Linking endpoint to lambda ({name})")
        resource = self.api.create_resource(http_path)
        resource.link_endpoint(http_method, func_arn)

    def deploy_domain(self):
        domain = self.stg_conf.get("domain")
        cert = self.stg_conf.get("cert")
        self.domain = domain

        # Create domain name
        if domain and cert:
            print(f"Creating custom domain name {domain}")
            cert = Cert(cert)
            try:
                r = self.api.create_domain(domain, cert.arn)
            except Exception as e:
                print("Error creating domain", e)
                return
            cloudfront = r['distributionDomainName']
            r53 = Route53()

            print("Creating cname record")
            try:
                r53.add_cname_record(domain, cloudfront)
            except Exception as e:
                print("Error adding cname record", e)
                return
            try:
                self.api.create_base_path_mapping(domain, "", stage)
            except Exception as e:
                print("Error creating base path mapping", e)
                return
            self.certified = True

    def finish(self):
        # Output
        print("-"*20)
        print("Project:", self.project)
        print("Stage:", self.stage)
        perm_url = f"{self.api.url}/{self.stage}"
        if self.certified:
            print(f"https://{self.domain} ({perm_url})")
        else:
            print(perm_url)
