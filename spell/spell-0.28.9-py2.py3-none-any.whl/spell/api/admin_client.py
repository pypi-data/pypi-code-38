from spell.api import base_client


ADMIN_RESOURCE_URL = "admin"
ORG_RESOURCE_URL = "orgs"


class AdminClient(base_client.BaseClient):

    def create_org(self, name, billing_email, admin_email):
        """Create a new org at the server

        Keyword arguments:
        name -- name of the new org (must be at least 4 characters)
        billing_email -- billing_email of the new org

        """
        payload = {
            "name": name,
            "billing_email": billing_email,
            "admin_email": admin_email,
        }
        r = self.request("post", ORG_RESOURCE_URL, payload=payload)
        self.check_and_raise(r)

    def create_gcp_cluster(self, cluster_name, org_name, storage_uri, bastion_key, service_account_id,
                           gs_access_key_id, gs_secret_access_key, vpc_id, subnets, region, project):
        """Create a new GCP cluster for an org

        Keyword arguments:
        cluster_name -- name of the new cluster
        org_name -- name of the org to add the cluster to
        storage_uri -- gs uri for external spell resources
        bastion_key -- ssh private key for bastion access
        vpc_id -- gcp id of vpc for worker machines
        subnets -- gcp ids of subnets for worker machines
        region -- gcp region for worker machines
        project -- gcp project for worker machines

        """
        payload = {
            "cloud_provider": "GCP",
            "org_name": org_name,
            "cluster_name": cluster_name,
            "storage_uri": storage_uri,
            "ssh_bastion_private_key": bastion_key,
            "service_account_id": service_account_id,
            "gs_access_key_id": gs_access_key_id,
            "gs_secret_access_key": gs_secret_access_key,
            "vpc_id": vpc_id,
            "subnets": subnets,
            "region": region,
            "project": project,
        }
        r = self.request("post", "{}/{}".format(ADMIN_RESOURCE_URL, "clusters"), payload=payload)
        self.check_and_raise(r)

    def create_aws_cluster(self, cluster_name, org_name, external_id, role_arn, read_policy,
                           security_group_id, storage_uri, bastion_key, vpc_id,
                           subnets, region):
        """Create a new AWS cluster for an org

        Keyword arguments:
        cluster_name -- name of the new cluster
        org_name -- name of the org to add the cluster to
        external_id -- internally-generated id for external aws requests
        role_arn -- aws arn for role to assume
        read_policy -- name of aws policy with s3 read permissions
        security_group_id -- id of security group with custom IP rules
        storage_uri -- s3 uri for external spell resources
        bastion_key -- ssh private key for bastion access
        vpc_id -- aws id of vpc for worker machines
        subnets -- aws ids of subnets for worker machines
        region -- aws region for worker machines

        """
        payload = {
            "cloud_provider": "AWS",
            "org_name": org_name,
            "cluster_name": cluster_name,
            "external_id": external_id,
            "role_arn": role_arn,
            "read_policy": read_policy,
            "security_group_id": security_group_id,
            "storage_uri": storage_uri,
            "ssh_bastion_private_key": bastion_key,
            "vpc_id": vpc_id,
            "subnets": subnets,
            "region": region,
        }
        r = self.request("post", "{}/{}".format(ADMIN_RESOURCE_URL, "clusters"), payload=payload)
        self.check_and_raise(r)

    def update_cluster_bastion_key(self, cluster_id, new_key):
        """Update the SSH bastion private key for a cluster

        Keyword arguments:
        cluster_id -- internal id of the cluster
        new_key -- new ssh private key for bastion access
        """
        payload = {
            "ssh_bastion_private_key": new_key,
        }
        url = "{}/{}/{}/{}".format(ADMIN_RESOURCE_URL, "clusters", cluster_id, "sshd_key")
        r = self.request("put", url, payload=payload)
        self.check_and_raise(r)

    def rotate_aws_cluster_worker_key(self, cluster_id):
        """Rotates the worker key for a cluster

        Keyword arguments:
        cluster_id -- internal (global) id of the cluster
        """
        url = "{}/{}/{}/{}".format(ADMIN_RESOURCE_URL, "clusters", cluster_id, "rotate_worker_key")
        r = self.request("post", url)
        self.check_and_raise(r)

    def delete_aws_cluster(self, cluster_id):
        """Marks a cluster as deleted in the db

        Keyword arguments:
        cluster_id -- internal (global) id of the cluster
        """
        url = "{}/{}/{}/".format(ADMIN_RESOURCE_URL, "clusters", cluster_id)
        r = self.request("delete", url)
        self.check_and_raise(r)
        return self.get_json(r)
