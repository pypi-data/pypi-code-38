# -*- coding: utf-8 -*-
import ipaddress
import random
import subprocess
import tempfile
import os
import yaml

import click

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)

from spell.cli.utils import HiddenOption, is_installed, cluster_utils
from spell.cli.utils.kube_cluster_templates import (
    generate_gke_cluster_rbac_yaml,
    generate_cluster_ambassador_yaml,
)

INGRESS_PORTS = [22, 2376, 9999]  # SSH, Docker Daemon, and Jupyter respectively
SPELL_SERVICE_ACCOUNT = '193976455398-compute@developer.gserviceaccount.com'


@click.command(name="init-gcp",
               short_help="Sets up GCP VPC as a Spell cluster", hidden=True)
@click.pass_context
@click.option("-n", "--name", "name", required=True, prompt="Enter a display name for this cluster within Spell",
              help="This will be used by Spell for you to identify the cluster")
def create_gcp(ctx, name):
    """
    This command creates a Spell cluster within a GCP VPC of your choosing as an external Spell cluster.
    This will let your organization run runs in that VPC, so your data never leaves
    your VPC. You set an GCS bucket of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.

    NOTE: This command uses your GCP credentials, activated by running `gcloud auth application-default login`,
    to create the necessary GCP resources for Spell to access and manage those machines. Your GCP credentials will
    need permission to set up these resources.
    """

    # suppress gcloud authentication warnings
    import warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Verify the owner is the admin of an org
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        import google.oauth2
        import google.auth
        from googleapiclient import discovery
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    try:
        from google.cloud import storage
    except ImportError:
        click.echo("Please `pip install google-cloud-storage` and rerun this command")
        return

    click.echo("""This command will help you
    - Set up an Google Storage bucket to store your run outputs in
    - Setup a VPC network which Spell will spin up workers in to run your jobs
    - Create a subnet in the VPC
    - Upload spell-worker public to list of available keys in your account
    - Setup a Service Account allowing Spell to spin up and down machines and access the GS bucket
    We will also ask you for a set of S3 Interoperable Access keys to your GS bucket""")

    try:
        credentials, project_id = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    compute_service = discovery.build('compute', 'v1', credentials=credentials)
    iam_service = discovery.build('iam', 'v1', credentials=credentials)
    resource_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
    project_id = get_project(resource_service, project_id)
    service_account = get_service_account(iam_service, resource_service, project_id)
    if service_account is None:
        return

    bucket_name = get_bucket_name(ctx, storage, service_account)
    if bucket_name is None:
        return

    network_name, subnet_name, region = get_vpc(compute_service, name, project_id)

    gs_access_key_id, gs_secret_access_key = get_interoperable_s3_access_keys(project_id)

    with api_client_exception_handler():
        spell_client.create_gcp_cluster(name, service_account['email'], bucket_name,
                                        network_name, subnet_name, region, project_id, gs_access_key_id,
                                        gs_secret_access_key)
    cluster_utils.echo_delimiter()
    click.echo("Your cluster {} is initialized! Head over to the web console to create machine types "
               "to execute your runs on.".format(name))


@click.command(name="gke-init", short_help="Sets up a GKE cluster to host model servers",
               hidden=True)
@click.pass_context
@click.option("-c", "--cluster", "cluster_id", type=int,
              help="The spell cluster id that you would like to configure this "
                   "model serving GKE cluster to work with.")
@click.option("--auth-api-url", cls=HiddenOption, type=str,
              help="URL of the spell API server used by Ambassador for authentication. "
                   "This must be externally accessible")
@click.option("--gcp-project-name", type=str,
              help="Name of the GCP project to create the GKE cluster in")
@click.option("--gke-cluster-name", type=str, default="spell-model-serving",
              help="Name of the newly created GKE cluster")
@click.option("--nodes-min", type=int, default=1,
              help="Minimum number of nodes in the model serving cluster (default 1)")
@click.option("--nodes-max", type=int, default=2,
              help="Minimum number of nodes in the model serving cluster (default 2)")
@click.option("--node-disk-size", type=int, default=50,
              help="Size of disks on each node in GB (default 50GB)")
def gke_init(ctx, cluster_id, auth_api_url, gcp_project_name, gke_cluster_name,
             nodes_min, nodes_max, node_disk_size):
    """
    Configure an existing GKE cluster for model serving using your current
    `gcloud` credentials. You need to have both `kubectl` and `gcloud` installed.
    This command will install the necessary deployments and services to host
    model servers.
    """

    # suppress gcloud authentication warnings
    import warnings
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    try:
        import kubernetes.client
        import kubernetes.config
    except ImportError:
        raise ExitException("kubernetes (for Python) is required. "
                            "Please `pip install kubernetes` and rerun this command")

    try:
        import google.oauth2
        from googleapiclient import discovery
    except ImportError:
        click.echo("Please `pip install google-api-python-client` and rerun this command")
        return

    try:
        credentials, project = google.auth.default()
    except google.auth.exceptions.DefaultCredentialsError:
        click.echo("""Please run `gcloud auth application-default login` to allow Spell
        to use your user credentials to set up a cluster, and rerun this command""")
        return

    if not is_installed("gcloud"):
        raise ExitException("`gcloud` is required, please install it before proceeding")
    if not is_installed("kubectl"):
        raise ExitException("`kubectl` is required, please install it before proceeding")

    # Figure out gcp_project_name if not already provided
    if gcp_project_name is None:
        resource_service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
        gcp_project_name = get_project(resource_service, project)

    # Verify valid cluster_id
    spell_client = ctx.obj["client"]
    cluster = cluster_utils.get_spell_cluster(spell_client, ctx.obj["owner"], cluster_id)
    if cluster["cloud_provider"] != "GCP":
        raise ExitException("Input cluster is using cloud provider {} and therefore cannot use GKE. "
                            "Only GCP is supported".format(cluster["cloud_provider"]))
    region = cluster["networking"]["gcp"]["region"]
    role_creds_gcp = cluster["role_credentials"]["gcp"]

    compute_service = discovery.build('compute', 'v1', credentials=credentials)
    zone = get_zone_from_region(compute_service, project, region)

    response = click.prompt("Create a GKE cluster for model serving? "
                            "You may skip this step if you have previously run it.",
                            type=click.Choice(["create", "skip"])).strip()
    if response == "create":
        create_gke_cluster(gke_cluster_name, gcp_project_name, role_creds_gcp["service_account_id"],
                           zone, nodes_min, nodes_max, node_disk_size)

    elif response == "skip":
        click.echo("Skipping GKE cluster creation, existing contexts are:")
        subprocess.check_call(("kubectl", "config", "get-contexts"))
        kube_ctx = subprocess.check_output(("kubectl", "config", "current-context")).decode('utf-8').strip()
        correct_kube_ctx = click.confirm("Is context '{}' the GKE cluster to use for model serving?".format(kube_ctx))
        if not correct_kube_ctx:
            raise ExitException("Set context to correct GKE cluster with `kubectl config use-context`")

    # Create "serving" namespace
    cluster_utils.create_serving_namespace(kubernetes.config, kubernetes.client)

    # Give Spell permissions to the cluster (via RBAC)
    cluster_utils.echo_delimiter()
    click.echo("Giving Spell RBAC permissions to GKE cluster...")
    try:
        rbac_yaml = generate_gke_cluster_rbac_yaml(role_creds_gcp["service_account_id"])
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(rbac_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--namespace", "serving", "--filename", f.name))
        click.echo("RBAC permissions granted!")
    except Exception as e:
        click.echo("ERROR: Giving Spell RBAC permissions failed. Error was: {}".format(e), err=True)

    # Add Ambassador
    cluster_utils.echo_delimiter()
    click.echo("Setting up Ambassador...")
    try:
        ambassador_yaml = generate_cluster_ambassador_yaml(auth_api_url, cloud="gke")
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
            f.write(ambassador_yaml)
            f.flush()
            subprocess.check_call(("kubectl", "apply", "--namespace", "serving", "--filename", f.name))
        click.echo("Ambassador set up!")
    except Exception as e:
        click.echo("ERROR: Setting up Ambassador failed. Error was: {}".format(e), err=True)

    # Add StatsD
    cluster_utils.add_statsd()

    # Upload config to Spell API
    cluster_utils.echo_delimiter()
    click.echo("Uploading config to Spell...")
    try:
        with tempfile.NamedTemporaryFile(mode="r", suffix=".yaml") as f:
            cmd = ("gcloud", "container", "clusters", "get-credentials", gke_cluster_name,
                   "--zone", zone,
                   "--project", gcp_project_name)
            env = os.environ.copy()
            env["KUBECONFIG"] = f.name
            p = subprocess.Popen(cmd, env=env)
            p.communicate()
            if p.returncode != 0:
                raise Exception("gcloud command had exit code {}".format(p.returncode))
            parsed_yaml = yaml.load(f)

        # update kubeconfig to use the custom `gcp-svc` auth-provider
        if "users" not in parsed_yaml or \
           len(parsed_yaml["users"]) != 1 or \
           "user" not in parsed_yaml["users"][0] or \
           "auth-provider" not in parsed_yaml["users"][0]["user"]:
            raise Exception("Unexpected kubeconfig yaml generated from gcloud command")
        parsed_yaml["users"][0]["user"]["auth-provider"] = {
            "name": "gcp-svc",
            "config": {"service-acct": "%s"}
        }
        yaml_str = yaml.dump(parsed_yaml)

        with api_client_exception_handler():
            spell_client.set_kube_config(cluster["id"], yaml_str)
        click.echo("Config successfully uploaded to Spell!")
    except Exception as e:
        click.echo("ERROR: Uploading config to Spell failed. Error was: {}".format(e), err=True)

    cluster_utils.echo_delimiter()
    click.echo("Cluster setup complete!")


def get_bucket_name(ctx, storage_api, service_account):
    storage_client = storage_api.Client()

    cluster_utils.echo_delimiter()
    response = click.prompt("We recommend using an empty GS Bucket for Spell outputs. Would "
                            "you like to make a new bucket or use an existing",
                            type=click.Choice(['new', 'existing'])).strip()
    if response == "new":
        owner_name = ctx.obj["owner"]
        bucket_name = click.prompt(
            "Please enter a name for the GS Bucket Spell will create for run outputs",
            default=u"spell-{}".format(owner_name.lower())).strip()
        bucket = storage_client.create_bucket(bucket_name)
        click.echo("Created your new bucket {}!".format(bucket_name))
    else:
        req = storage_client.list_buckets()
        buckets = [bucket.name for bucket in req]
        bucket_name = click.prompt("Enter existing bucket name", type=click.Choice(buckets))
    # set bucket permissions
    bucket = storage_client.bucket(bucket_name)
    policy = bucket.get_iam_policy()
    service_account_tag = 'serviceAccount:{}'.format(service_account['email'])
    for role, value in policy.items():
        if role == 'roles/storage.admin' and service_account_tag in value:
            return bucket_name
    policy['roles/storage.admin'].add(service_account_tag)
    bucket.set_iam_policy(policy)
    return bucket_name


def get_vpc(compute_service, cluster_name, project):
    cluster_utils.echo_delimiter()
    request = compute_service.regions().list(project=project)
    regions = []
    while request is not None:
        response = request.execute()
        for region in response['items']:
            regions.append(region['name'])
        request = compute_service.regions().list_next(previous_request=request, previous_response=response)
    region = click.prompt("Please request a region for your cluster. This might affect machine availability",
                          type=click.Choice(regions))
    network_body = {
        'name': cluster_name,
        "autoCreateSubnetworks": False
    }

    click.echo("Creating network...")
    req = compute_service.networks().insert(project=project, body=network_body)
    response = req.execute()
    with click.progressbar(length=100, show_eta=False) as bar:
        while response['status'] != 'DONE':
            bar.update(response['progress'])
            response = compute_service.globalOperations().get(project=project, operation=response['name']).execute()
        bar.update(100)
    click.echo("Created a new VPC/network with name {}!".format(cluster_name))

    network_url = response['targetLink']
    network_name = cluster_name

    firewall_body = {
        "name": cluster_name,
        "description": "Ingress from Spell API for ssh (22), docker (2376), and jupyter (9999) traffic",
        "network": network_url,
        "source": "0.0.0.0/0",
        "allowed": [{
            "IPProtocol": "TCP",
            "ports": [str(port) for port in INGRESS_PORTS]
        }],
    }

    click.echo("Adjusting network ingress ports...")
    request = compute_service.firewalls().insert(project=project, body=firewall_body)
    response = request.execute()
    with click.progressbar(length=100, show_eta=False) as bar:
        while response['status'] != 'DONE':
            bar.update(response['progress'])
            response = compute_service.globalOperations().get(project=project, operation=response['name']).execute()
        bar.update(100)
    click.echo("Allowed ingress from ports {} on network {}!".format(INGRESS_PORTS, cluster_name))

    cidr = None
    while cidr is None:
        cidr = click.prompt("Enter a CIDR for your new VPC or feel free to use the default",
                            default=u"10.0.0.0/16").strip()
        try:
            ipaddress.ip_network(cidr)
        except ValueError:
            # handle bad ip
            click.echo("Invalid CIRD {}, try again".format(cidr))
            cidr = None

    subnetwork_body = {
        "name": cluster_name,
        "network": network_url,
        "ipCidrRange": cidr,
    }

    click.echo("Creating subnetwork...")
    request = compute_service.subnetworks().insert(project=project, body=subnetwork_body, region=region)
    response = request.execute()
    with click.progressbar(length=100, show_eta=False) as bar:
        while response['status'] != 'DONE':
            bar.update(response['progress'])
            response = compute_service.regionOperations().get(project=project,
                                                              region=region,
                                                              operation=response['name']
                                                              ).execute()
        bar.update(100)
    subnet_name = cluster_name

    click.echo("Created a new subnet {} within network {} in region {}!".format(cluster_name, cluster_name, region))

    return network_name, subnet_name, region


def get_project(resource_service, project_id):
    cluster_utils.echo_delimiter()
    projects = resource_service.projects().list().execute()

    if not click.confirm("All of this will be done within your project '{}' - continue?".format(project_id),
                         default=True):
        return click.prompt("Please choose a project id",
                            type=click.Choice([p['projectId'] for p in projects['projects']]))
    return project_id


def get_zone_from_region(compute_service, project, region):
    request = compute_service.regions().get(project=project, region=region)
    region_self_link = request.execute()["selfLink"]

    request = compute_service.zones().list(project=project, filter='region = "{}"'.format(region_self_link))
    response = request.execute()
    if 'items' not in response or len(response['items']) == 0:
        raise ExitException("No compute zones found for region {}".format(region))
    return response['items'][0]['name']


def get_interoperable_s3_access_keys(project):
    click.echo("Spell uses the S3 API to access GCS buckets. For this, we require the Interoperable S3 Access Keys. "
               "Please navigate to the following URL and select the 'Interoperability' tab: \n"
               "\t https://console.cloud.google.com/storage/settings?project={} \n"
               "Spell will have access (read and write) to all buckets that you have read and write access to. "
               "If you wish to restrict this, please contact us support@spell.run".format(project)
               )
    access_key = click.prompt("Access key").strip()
    secret = click.prompt("Secret").strip()
    return access_key, secret


def get_service_account(iam_service, resource_service, project):
    cluster_utils.echo_delimiter()
    suffix = str(random.randint(10**6, 10**7))
    role_name = "spell-access-{}".format(suffix)
    service_account = iam_service.projects().serviceAccounts().create(
        name='projects/{}'.format(project),
        body={
            'accountId': role_name,
            'serviceAccount': {
                'displayName': "spell-access"
            }
        }
    ).execute()
    service_account_name = service_account['name']
    service_account_email = service_account['email']
    try:
        # Allow Spell service account to create keys for external service account
        policy = iam_service.projects().serviceAccounts().getIamPolicy(resource=service_account_name).execute()
        # TODO(libeks): remove once we've fully migrated to tokens
        key_admin_binding = {
            'role': 'roles/iam.serviceAccountKeyAdmin',
            'members': ['serviceAccount:{}'.format(SPELL_SERVICE_ACCOUNT)]
        }
        # Service account needs to have access to use itself to attach itself to an instance
        account_user_binding = {
            'role': 'roles/iam.serviceAccountUser',
            'members': ['serviceAccount:{}'.format(SPELL_SERVICE_ACCOUNT),
                        'serviceAccount:{}'.format(service_account_email)]
        }
        token_create_binding = {
            'role': 'roles/iam.serviceAccountTokenCreator',
            'members': ['serviceAccount:{}'.format(SPELL_SERVICE_ACCOUNT)]
        }
        policy['bindings'] = [key_admin_binding, account_user_binding, token_create_binding]
        policy = iam_service.projects().serviceAccounts().setIamPolicy(
            resource=service_account_name,
            body={
                'resource': service_account_name,
                'policy': policy
            }).execute()
    except Exception as e:
        raise ExitException("Unable to create and attach IAM policies. GCP error: {}".format(e))

    suffix = str(random.randint(10**6, 10**7))
    role_name = "SpellAccess_{}".format(suffix)
    permissions = [
        'compute.disks.create',
        'compute.globalOperations.get',
        'compute.instances.create',
        'compute.instances.delete',
        'compute.instances.get',
        'compute.instances.list',
        'compute.instances.setLabels',
        'compute.instances.setMetadata',
        'compute.instances.setServiceAccount',
        'compute.subnetworks.use',
        'compute.subnetworks.useExternalIp',
        'compute.zones.list',
        'compute.regions.get',
        'storage.objects.get',
        'storage.objects.list',
    ]

    create_role_request_body = {
        "roleId": role_name,
        "role": {
            "title": role_name,
            "includedPermissions": permissions
        }
    }

    click.echo("Creating role {} with the following permissions: \n{} \n..."
               .format(role_name, "\n".join('\t'+p for p in permissions))
               )
    request = iam_service.projects().roles().create(parent='projects/{}'.format(project), body=create_role_request_body)
    response = request.execute()
    role_id = response['name']

    click.echo("Assigning role {} to service account {}...".format(role_name, service_account_email))
    request = resource_service.projects().getIamPolicy(resource=project, body={})
    response = request.execute()

    response['bindings'].append({
        'members': ["serviceAccount:{}".format(service_account_email)],
        'role': role_id
    })

    set_iam_policy_body = {
        "policy": response
    }

    request = resource_service.projects().setIamPolicy(resource=project, body=set_iam_policy_body)
    response = request.execute()

    click.echo("Successfully created Service Account {}".format(service_account_email))
    return service_account


def create_gke_cluster(cluster_name, gcp_project_name, service_account_id,
                       backplane_zone, nodes_min, nodes_max, node_disk_size):
    """Create the GKE cluster with `gcloud`"""

    try:
        cmd = [
            "gcloud", "container", "clusters", "create", cluster_name,
            "--project", gcp_project_name,
            "--zone", backplane_zone,
            "--node-locations", backplane_zone,
            "--addons=HorizontalPodAutoscaling",
            "--enable-autoscaling",
            "--num-nodes", "1", "--min-nodes", str(nodes_min), "--max-nodes", str(nodes_max),
            "--service-account", service_account_id,
            "--disk-size", str(node_disk_size),
            "--no-enable-cloud-logging",
            "--no-enable-cloud-monitoring",
            "--labels=spell=model_serving",
            "--no-enable-basic-auth",
        ]
        click.echo("Creating the cluster. This can take a while...")
        subprocess.check_call(cmd)
        click.echo("Cluster created!")

        click.echo("Giving current gcloud user cluster-admin...")
        cmd = ["gcloud", "config", "list", "account", "--format", "value(core.account)"]
        gcloud_user = subprocess.check_output(cmd).decode('utf-8').strip()
        cmd = [
            "kubectl", "create", "clusterrolebinding", "cluster-admin-binding",
            "--clusterrole", "cluster-admin",
            "--user", gcloud_user,
        ]
        subprocess.check_call(cmd)
        click.echo("Current gcloud user {} granted cluster-admin".format(gcloud_user))

    except subprocess.CalledProcessError:
        raise ExitException("Failed to run `gcloud`. Make sure it's installed correctly and "
                            "your inputs are valid. Error details are above in the `gcloud` output.")
