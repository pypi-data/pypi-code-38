import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth
import azure.batch.models as batchmodels
import azure.storage.blob as azureblob
from dotmap import DotMap
import datetime
import json
import time
import sys
import os
import io

# from ..config.azure import AzureConfig
from ..primitives.resources import FileResource


class AzureBatch:
    def __init__(self, config):
        """
        azure_batch_config_file="/mnt/users/qinglong/json/azure.json"
        config_dict = open(azure_batch_config_file).read()
        file_resources = FileResource('/mnt/deployment/monte_carlo_simu_common_resources',
                                      '/mnt/users/qinglong/jupyters/simu_files/run_batch_simu.sh',
                                      '/mnt/users/qinglong/jupyters/mc_test/qinglong_test_main/main.mac')

        ab = AzureBatch(config_dict)

        :param config_dict: The Azure Batch Simulation Json API.
        """
        self.config = DotMap(load_API_as_dict(config))

        self.batch_client = batch.BatchServiceClient(
            batch_auth.SharedKeyCredentials(
                self.config.azure.batch.account.name,
                self.config.azure.batch.account.key,
            ),
            base_url=self.config.azure.batch.account.url,
        )

        pool_config = self.config.azure.batch.pool
        image_ref_config = (
            pool_config.virtual_machine_configuration.image.ubuntu_16_04_lts
        )

        self.pool = batch.models.PoolAddParameter(
            id=pool_config.pool_id,
            virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
                image_reference=batchmodels.ImageReference(
                    publisher=image_ref_config.publisher,
                    offer=image_ref_config.offer,
                    sku=image_ref_config.sku,
                    version=image_ref_config.version,
                ),
                container_configuration=batch.models.ContainerConfiguration(
                    container_image_names=self.config.azure.batch.pool.docker.image_names
                ),
                node_agent_sku_id=pool_config.node_agent_sku_id,
            ),
            vm_size=pool_config.pool_vm_size,
            target_dedicated_nodes=pool_config.target_dedicated_nodes,
        )

        self.job = batch.models.JobAddParameter(
            id=self.config.azure.batch.pool.job.job_id,
            pool_info=batch.models.PoolInformation(pool_id=self.pool.id),
        )

        self.blob_client = azureblob.BlockBlobService(
            account_name=self.config.azure.storage.account.name,
            account_key=self.config.azure.storage.account.key,
        )
        self.input_container_name = self.config.azure.storage.input_container_name
        self.output_container_name = self.config.azure.storage.output_container_name

    def create_blob_container(self):
        self.blob_client.create_container(
            self.input_container_name, fail_on_exist=False
        )
        self.blob_client.create_container(
            self.output_container_name, fail_on_exist=False
        )

    def create_pool(self):
        self.batch_client.pool.add(self.pool)

    def delete_pool(self):
        self.batch_client.pool.delete(self.pool.id)

    def create_job(self):
        self.batch_client.job.add(self.job)

    def delete_job(self):
        self.batch_client.job.delete(self.job.id)

    def upload_file_to_container(self, file_path):
        blob_name = os.path.basename(file_path)

        self.blob_client.create_blob_from_path(
            self.input_container_name, blob_name, file_path
        )

        sas_token = self.blob_client.generate_blob_shared_access_signature(
            self.input_container_name,
            blob_name,
            permission=azureblob.BlobPermissions.READ,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        )

        sas_url = self.blob_client.make_blob_url(
            self.input_container_name, blob_name, sas_token=sas_token
        )

        return batchmodels.ResourceFile(sas_url, file_path=blob_name)

    def submit_single_task(
        self,
        task_id: str,
        file_resources: FileResource,
        command="""
                /bin/bash -c
                \"
                cd $AZ_BATCH_TASK_WORKING_DIR &&
                bash run_batch_simu.sh
                \"
                """,
    ):
        tasks = list()

        task_container_settings = batch.models.TaskContainerSettings(
            image_name=self.config.azure.batch.pool.docker.image_names,
            container_run_options=self.config.azure.batch.pool.docker.run_option,
        )

        tasks.append(
            batch.models.TaskAddParameter(
                id=task_id,
                command_line=command,
                container_settings=task_container_settings,
                resource_files=[
                    self.upload_file_to_container(d) for d in file_resources.content
                ],
            )
        )

        self.batch_client.task.add_collection(self.job.id, tasks)


def get_file_from_task(
    azure_batch: AzureBatch, job_id: str, task_id: str, remote_url: str, dest_url: str
):
    """
    Get file on task workload machine back.
    :param azure_batch: AzureBatch obj with a batch client attaches to a azure.
    :param job_id: Azure batch job id
    :param task_id:
    :param remote_url: Directory of target file on task machine.
    :param dest_url: A local url that remote file supposed to be.
    :return:
    """
    with open(dest_url, "wb") as file_output:
        output = azure_batch.batch_client.file.get_from_task(
            job_id, task_id, remote_url
        )
        for data in output:
            file_output.write(data)


def wait_for_tasks_to_complete(batch_service_client, job_id, timeout):
    """
    Returns when all tasks in the specified job reach the Completed state.
    :param batch_service_client: A Batch service client.
    :type batch_service_client: `azure.batch.BatchServiceClient`
    :param str job_id: The id of the job whose tasks should be to monitored.
    :param timedelta timeout: The duration to wait for task completion. If all
    tasks in the specified job do not reach Completed state within this time
    period, an exception will be raised.
    """
    timeout_expiration = datetime.datetime.now() + timeout

    print(
        "Monitoring all tasks for 'Completed' state, timeout in {}...".format(timeout),
        end="",
    )

    while datetime.datetime.now() < timeout_expiration:
        print(".", end="")
        sys.stdout.flush()
        tasks = batch_service_client.task.list(job_id)

        incomplete_tasks = [
            task for task in tasks if task.state != batchmodels.TaskState.completed
        ]
        if not incomplete_tasks:
            print()
            return True
        else:
            time.sleep(1)

    print()
    raise RuntimeError(
        "ERROR: Tasks did not reach 'Completed' state within "
        "timeout period of " + str(timeout)
    )


def read_stream_as_string(stream, encoding):
    """Read stream as string
    :param stream: input stream generator
    :param str encoding: The encoding of the file. The default is utf-8.
    :return: The file content.
    :rtype: str
    """
    output = io.BytesIO()
    try:
        for data in stream:
            output.write(data)
        if encoding is None:
            encoding = "utf-8"
        return output.getvalue().decode(encoding)
    finally:
        output.close()


def load_API_as_dict(API_file):
    API_string = open(API_file).read()
    return json.loads(API_string)
