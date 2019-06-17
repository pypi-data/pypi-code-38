from hatano.util import Conf
from hatano.iam import IamRole
from hatano.lmbda import Lambda
from hatano.apigateway import RestApi
from hatano.acm import Cert
from hatano.route53 import Route53

import os


def deploy(args):
    # Extract stage
    stage = args.stage

    # Get project configuration
    c = Conf()
    project, stg_conf = c.get_stage(stage)
    domain = stg_conf.get("domain")
    cert = stg_conf.get("cert")
    s3 = stg_conf.get("s3")

    # Create REST API
    print(f"Creating REST API for {project}")
    api = RestApi(project, create=True)

    # Create each function and link to and endpoint
    for fname in stg_conf.get("functions", {}):
        print(f"Deploying function {fname}")
        fn = stg_conf["functions"][fname]
        fn["name"] = fname
        fn["runtime"] = stg_conf["runtime"]
        deploy_func(stage, fn, api=api)

    # Deploy the API
    print(f"Deploying API stage {stage}")
    api.deploy(stage)

    # Create domain name
    certified = False
    if domain and cert:
        print(f"Creating custom domain name {domain}")
        cert = Cert(cert)
        r = api.create_domain(domain, cert.arn)
        cloudfront = r['distributionDomainName']
        r53 = Route53()
        print("Creating cname record")
        r53.add_cname_record(domain, cloudfront)
        api.create_base_path_mapping(domain, "", stage)
        certified = True

    # Output
    print("-"*20)
    print("Project:", project)
    print("Stage:", stage)
    perm_url = f"{api.url}/{stage}"
    if certified:
        print(f"https://{domain} ({perm_url})")
    else:
        print(perm_url)


def deploy_func(stage, fn, api=None):
    c = Conf()
    project, stg_conf = c.get_stage(stage)
    if not api:
        api = RestApi(stage, create=True)

    name = fn["name"]
    env = fn.get("env", {})
    fullname = f"{project}-{name}-{stage}"

    http_method = fn.get("method", "")
    http_path = fn.get("path")

    # Create iam role
    print("  - Creating IAM role")
    iam = IamRole(stage, fn)
    role = iam.lambda_role()
    iam.put_custom_policy()
    role_arn = role['Role']['Arn']

    # Create lambda
    print("  - Creating lambda")
    lmb = Lambda(stage, fn, role_arn=role_arn, env=env)
    func = lmb.create_function()
    func_arn = func['FunctionArn']
    lmb.add_permission("apigateway", "InvokeFunction")

    # Create resource and endpoint
    print("  - Linking endpoint to lambda")
    resource = api.create_resource(http_path)
    resource.link_endpoint(http_method, func_arn)
