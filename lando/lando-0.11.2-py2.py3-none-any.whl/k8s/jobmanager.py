from lando.k8s.cluster import BatchJobSpec, SecretVolume, PersistentClaimVolume, \
    ConfigMapVolume, Container, FieldRefEnvVar
from lando.common.commands import StageDataCommand, OrganizeOutputCommand, SaveOutputCommand
from lando.common.names import BaseNames, Paths
import json
import os


DDSCLIENT_CONFIG_MOUNT_PATH = "/etc/ddsclient"
BESPIN_JOB_LABEL_VALUE = "true"


class JobLabels(object):
    BESPIN_JOB = "bespin-job"  # expected value is "true"
    JOB_ID = "bespin-job-id"
    STEP_TYPE = "bespin-job-step"


class JobStepTypes(object):
    STAGE_DATA = "stage_data"
    RUN_WORKFLOW = "run_workflow"
    ORGANIZE_OUTPUT = "organize_output"
    SAVE_OUTPUT = "save_output"
    RECORD_OUTPUT_PROJECT = "record_output_project"


class JobManager(object):
    def __init__(self, cluster_api, config, job):
        self.cluster_api = cluster_api
        self.config = config
        self.job = job
        self.paths = Paths(base_directory="/")
        names = Names(job, self.paths)
        self.names = names
        self.storage_class_name = config.storage_class_name
        self.default_metadata_labels = {
            JobLabels.BESPIN_JOB: BESPIN_JOB_LABEL_VALUE,
            JobLabels.JOB_ID: str(self.job.id),
        }
        label_ary = ['{}={}'.format(k,v) for k,v in self.default_metadata_labels.items()]
        self.label_selector = ','.join(label_ary)

    def make_job_labels(self, job_step_type):
        labels = dict(self.default_metadata_labels)
        labels[JobLabels.STEP_TYPE] = job_step_type
        return labels

    def create_job_data_persistent_volume(self, stage_data_size_in_g):
        self.cluster_api.create_persistent_volume_claim(
            self.names.job_data,
            storage_size_in_g=stage_data_size_in_g,
            storage_class_name=self.storage_class_name,
            labels=self.default_metadata_labels,
        )

    def create_output_data_persistent_volume(self):
        self.cluster_api.create_persistent_volume_claim(
            self.names.output_data,
            storage_size_in_g=self.job.volume_size,
            storage_class_name=self.storage_class_name,
            labels=self.default_metadata_labels,
        )

    def create_stage_data_persistent_volumes(self, stage_data_size_in_g):
        self.create_job_data_persistent_volume(stage_data_size_in_g)

    def create_stage_data_job(self, input_files):
        stage_data_config = StageDataConfig(self.job, self.config, self.paths)
        self._create_stage_data_config_map(name=self.names.stage_data,
                                           filename=stage_data_config.filename,
                                           workflow=self.job.workflow,
                                           input_files=input_files)
        volumes = [
            PersistentClaimVolume(self.names.job_data,
                                  mount_path=self.paths.JOB_DATA,
                                  volume_claim_name=self.names.job_data,
                                  read_only=False),
            ConfigMapVolume(self.names.stage_data,
                            mount_path=self.paths.CONFIG_DIR,
                            config_map_name=self.names.stage_data,
                            source_key=stage_data_config.filename,
                            source_path=stage_data_config.filename),
            SecretVolume(self.names.data_store_secret,
                         mount_path=stage_data_config.data_store_secret_path,
                         secret_name=stage_data_config.data_store_secret_name),
        ]
        container = Container(
            name=self.names.stage_data,
            image_name=stage_data_config.image_name,
            command=stage_data_config.command,
            args=[stage_data_config.path, self.names.workflow_input_files_metadata_path],
            env_dict=stage_data_config.env_dict,
            requested_cpu=stage_data_config.requested_cpu,
            requested_memory=stage_data_config.requested_memory,
            volumes=volumes)
        labels = self.make_job_labels(JobStepTypes.STAGE_DATA)
        job_spec = BatchJobSpec(self.names.stage_data,
                                container=container,
                                labels=labels)
        return self.cluster_api.create_job(self.names.stage_data, job_spec, labels=labels)

    def _create_stage_data_config_map(self, name, filename, workflow, input_files):
        stage_data_command = StageDataCommand(workflow, self.names, self.paths)
        config_data = stage_data_command.command_file_dict(input_files)
        payload = {
            filename: json.dumps(config_data)
        }
        self.cluster_api.create_config_map(name=name, data=payload, labels=self.default_metadata_labels)

    def cleanup_stage_data_job(self):
        self.cluster_api.delete_job(self.names.stage_data)
        self.cluster_api.delete_config_map(self.names.stage_data)

    def create_run_workflow_persistent_volumes(self):
        self.create_output_data_persistent_volume()

    def create_run_workflow_job(self):
        run_workflow_config = RunWorkflowConfig(self.job, self.config)
        system_data_volume = run_workflow_config.system_data_volume
        volumes = [
            PersistentClaimVolume(self.names.job_data,
                                  mount_path=self.paths.JOB_DATA,
                                  volume_claim_name=self.names.job_data,
                                  read_only=True),
            PersistentClaimVolume(self.names.output_data,
                                  mount_path=self.paths.OUTPUT_DATA,
                                  volume_claim_name=self.names.output_data,
                                  read_only=False),
        ]
        if system_data_volume:
            volumes.append(PersistentClaimVolume(
                self.names.system_data,
                mount_path=system_data_volume.mount_path,
                volume_claim_name=system_data_volume.volume_claim_name,
                read_only=True))
        command = run_workflow_config.command
        command.extend(["--cachedir", self.paths.TMPOUT_DATA + "/",
                        "--outdir", self.paths.OUTPUT_RESULTS_DIR + "/",
                        "--max-ram", self.job.job_flavor_memory,
                        "--max-cores", str(self.job.job_flavor_cpus),
                        "--usage-report", self.names.usage_report_path,
                        "--stdout", self.names.run_workflow_stdout_path,
                        "--stderr", self.names.run_workflow_stderr_path,
                        self.names.workflow_to_run,
                        self.names.job_order_path,
                        ])
        container = Container(
            name=self.names.run_workflow,
            image_name=run_workflow_config.image_name,
            command=command,
            env_dict={
                "CALRISSIAN_POD_NAME": FieldRefEnvVar(field_path="metadata.name")
            },
            requested_cpu=run_workflow_config.requested_cpu,
            requested_memory=run_workflow_config.requested_memory,
            volumes=volumes
        )
        labels = self.make_job_labels(JobStepTypes.RUN_WORKFLOW)
        job_spec = BatchJobSpec(self.names.run_workflow,
                                container=container,
                                labels=labels)
        return self.cluster_api.create_job(self.names.run_workflow, job_spec, labels=labels)

    def cleanup_run_workflow_job(self):
        self.cluster_api.delete_job(self.names.run_workflow)

    def create_organize_output_project_job(self, methods_document_content):
        organize_output_config = OrganizeOutputConfig(self.job, self.config, self.paths)
        self._create_organize_output_config_map(name=self.names.organize_output,
                                                filename=organize_output_config.filename,
                                                methods_document_content=methods_document_content)
        volumes = [
            PersistentClaimVolume(self.names.job_data,
                                  mount_path=self.paths.JOB_DATA,
                                  volume_claim_name=self.names.job_data,
                                  read_only=True),
            PersistentClaimVolume(self.names.output_data,
                                  mount_path=self.paths.OUTPUT_DATA,
                                  volume_claim_name=self.names.output_data,
                                  read_only=False),
            ConfigMapVolume(self.names.organize_output,
                            mount_path=self.paths.CONFIG_DIR,
                            config_map_name=self.names.organize_output,
                            source_key=organize_output_config.filename,
                            source_path=organize_output_config.filename),
        ]
        container = Container(
            name=self.names.organize_output,
            image_name=organize_output_config.image_name,
            command=organize_output_config.command,
            args=[organize_output_config.path],
            requested_cpu=organize_output_config.requested_cpu,
            requested_memory=organize_output_config.requested_memory,
            volumes=volumes)
        labels = self.make_job_labels(JobStepTypes.ORGANIZE_OUTPUT)
        job_spec = BatchJobSpec(self.names.organize_output,
                                container=container,
                                labels=labels)
        return self.cluster_api.create_job(self.names.organize_output, job_spec, labels=labels)

    def _create_organize_output_config_map(self, name, filename, methods_document_content):
        organize_output_command = OrganizeOutputCommand(self.job, self.names, self.paths)
        config_data = organize_output_command.command_file_dict(methods_document_content)
        payload = {
            filename: json.dumps(config_data)
        }
        self.cluster_api.create_config_map(name=name, data=payload, labels=self.default_metadata_labels)

    def cleanup_organize_output_project_job(self):
        self.cluster_api.delete_config_map(self.names.organize_output)
        self.cluster_api.delete_job(self.names.organize_output)

    def create_save_output_job(self, share_dds_ids):
        save_output_config = SaveOutputConfig(self.job, self.config, self.paths)
        self._create_save_output_config_map(name=self.names.save_output,
                                            filename=save_output_config.filename,
                                            share_dds_ids=share_dds_ids,
                                            activity_name=self.names.activity_name,
                                            activity_description=self.names.activity_description)
        volumes = [
            PersistentClaimVolume(self.names.job_data,
                                  mount_path=self.paths.JOB_DATA,
                                  volume_claim_name=self.names.job_data,
                                  read_only=True),
            PersistentClaimVolume(self.names.output_data,
                                  mount_path=self.paths.OUTPUT_DATA,
                                  volume_claim_name=self.names.output_data,
                                  read_only=False),  # writable so we can write project_details file
            ConfigMapVolume(self.names.stage_data,
                            mount_path=self.paths.CONFIG_DIR,
                            config_map_name=self.names.save_output,
                            source_key=save_output_config.filename,
                            source_path=save_output_config.filename),
            SecretVolume(self.names.data_store_secret,
                         mount_path=save_output_config.data_store_secret_path,
                         secret_name=save_output_config.data_store_secret_name),
        ]
        container = Container(
            name=self.names.save_output,
            image_name=save_output_config.image_name,
            command=save_output_config.command,
            args=[save_output_config.path, self.names.annotate_project_details_path],
            working_dir=self.paths.OUTPUT_RESULTS_DIR,
            env_dict=save_output_config.env_dict,
            requested_cpu=save_output_config.requested_cpu,
            requested_memory=save_output_config.requested_memory,
            volumes=volumes)
        labels = self.make_job_labels(JobStepTypes.SAVE_OUTPUT)
        job_spec = BatchJobSpec(self.names.save_output,
                                container=container,
                                labels=labels)
        return self.cluster_api.create_job(self.names.save_output, job_spec, labels=labels)

    def _create_save_output_config_map(self, name, filename, share_dds_ids, activity_name, activity_description):
        save_output_command = SaveOutputCommand(self.names, self.paths, activity_name, activity_description)
        config_data = save_output_command.command_file_dict(share_dds_ids, started_on="", ended_on="")
        payload = {
            filename: json.dumps(config_data)
        }
        self.cluster_api.create_config_map(name=name, data=payload, labels=self.default_metadata_labels)

    def cleanup_save_output_job(self):
        self.cluster_api.delete_job(self.names.save_output)
        self.cluster_api.delete_config_map(self.names.save_output)
        self.cluster_api.delete_persistent_volume_claim(self.names.job_data)

    def create_record_output_project_job(self):
        config = RecordOutputProjectConfig(self.job, self.config)
        volumes = [
            PersistentClaimVolume(self.names.output_data,
                                  mount_path=self.paths.OUTPUT_DATA,
                                  volume_claim_name=self.names.output_data,
                                  read_only=True),
        ]
        container = Container(
            name=self.names.record_output_project,
            image_name=config.image_name,
            command=["sh"],
            args=[self.names.annotate_project_details_path],
            working_dir=self.paths.OUTPUT_RESULTS_DIR,
            env_dict={"MY_POD_NAME": FieldRefEnvVar(field_path="metadata.name")},
            requested_cpu=config.requested_cpu,
            requested_memory=config.requested_memory,
            volumes=volumes)
        labels = self.make_job_labels(JobStepTypes.RECORD_OUTPUT_PROJECT)
        job_spec = BatchJobSpec(self.names.record_output_project,
                                container=container,
                                labels=labels,
                                service_account_name=config.service_account_name)
        return self.cluster_api.create_job(self.names.record_output_project, job_spec, labels=labels)

    def read_record_output_project_details(self):
        job_step_selector='{},{}={}'.format(self.label_selector,
                                            JobLabels.STEP_TYPE, JobStepTypes.RECORD_OUTPUT_PROJECT)
        pods = self.cluster_api.list_pods(label_selector=job_step_selector)
        if len(pods) != 1:
            raise ValueError("Incorrect number of pods for record output step: {}".format(len(pods)))
        annotations = pods[0].metadata.annotations
        project_id = annotations.get('project_id')
        if not project_id:
            raise ValueError("Missing project_id in pod annotations: {}".format(pods[0].metadata.name))
        readme_file_id = annotations.get('readme_file_id')
        if not readme_file_id:
            raise ValueError("Missing readme_file_id in pod annotations: {}".format(pods[0].metadata.name))
        return project_id, readme_file_id

    def cleanup_record_output_project_job(self):
        self.cluster_api.delete_job(self.names.record_output_project)
        self.cluster_api.delete_persistent_volume_claim(self.names.output_data)

    def cleanup_all(self):
        self.cleanup_jobs_and_config_maps()

        # Delete all PVC
        for pvc in self.cluster_api.list_persistent_volume_claims(label_selector=self.label_selector):
            self.cluster_api.delete_persistent_volume_claim(pvc.metadata.name)

    def cleanup_jobs_and_config_maps(self):
        # Delete all Jobs
        for job in self.cluster_api.list_jobs(label_selector=self.label_selector):
            self.cluster_api.delete_job(job.metadata.name)

        # Delete all config maps
        for config_map in self.cluster_api.list_config_maps(label_selector=self.label_selector):
            self.cluster_api.delete_config_map(config_map.metadata.name)


class Names(BaseNames):
    def __init__(self, job, paths):
        super(Names, self).__init__(job, paths)

        # Volumes
        self.job_data = 'job-data-{}'.format(self.suffix)
        self.output_data = 'output-data-{}'.format(self.suffix)
        self.tmpout = 'tmpout-{}'.format(self.suffix)
        self.tmp = 'tmp-{}'.format(self.suffix)

        # Job Names
        self.stage_data = 'stage-data-{}'.format(self.suffix)
        self.run_workflow = 'run-workflow-{}'.format(self.suffix)
        self.organize_output = 'organize-output-{}'.format(self.suffix)
        self.save_output = 'save-output-{}'.format(self.suffix)
        self.record_output_project = 'record-output-project-{}'.format(self.suffix)

        self.user_data = 'user-data-{}'.format(self.suffix)
        self.data_store_secret = 'data-store-{}'.format(self.suffix)
        self.workflow_download_dest = '{}/{}'.format(paths.WORKFLOW, os.path.basename(job.workflow.workflow_url))
        self.system_data = 'system-data-{}'.format(self.suffix)

        self.annotate_project_details_path = '{}/annotate_project_details.sh'.format(paths.OUTPUT_DATA)


class StageDataConfig(object):
    def __init__(self, job, config, paths):
        self.filename = "stagedata.json"
        self.path = '{}/{}'.format(paths.CONFIG_DIR, self.filename)
        self.data_store_secret_name = config.data_store_settings.secret_name
        self.data_store_secret_path = DDSCLIENT_CONFIG_MOUNT_PATH
        self.env_dict = {"DDSCLIENT_CONF": "{}/config".format(DDSCLIENT_CONFIG_MOUNT_PATH)}

        job_stage_data_settings = job.k8s_settings.stage_data
        self.image_name = job_stage_data_settings.image_name
        self.command = job_stage_data_settings.base_command
        self.requested_cpu = job_stage_data_settings.cpus
        self.requested_memory = job_stage_data_settings.memory


class RunWorkflowConfig(object):
    def __init__(self, job, config):
        job_run_workflow_settings = job.k8s_settings.run_workflow
        self.image_name = job_run_workflow_settings.image_name
        self.command = job_run_workflow_settings.base_command
        self.requested_cpu = job_run_workflow_settings.cpus
        self.requested_memory = job_run_workflow_settings.memory

        run_workflow_settings = config.run_workflow_settings
        self.system_data_volume = run_workflow_settings.system_data_volume


class OrganizeOutputConfig(object):
    def __init__(self, job, config, paths):
        self.filename = "organizeoutput.json"
        self.path = '{}/{}'.format(paths.CONFIG_DIR, self.filename)

        job_organize_output_settings = job.k8s_settings.organize_output
        self.image_name = job_organize_output_settings.image_name
        self.command = job_organize_output_settings.base_command
        self.requested_cpu = job_organize_output_settings.cpus
        self.requested_memory = job_organize_output_settings.memory


class SaveOutputConfig(object):
    def __init__(self, job, config, paths):
        self.filename = "saveoutput.json"
        self.path = '{}/{}'.format(paths.CONFIG_DIR, self.filename)
        self.data_store_secret_name = config.data_store_settings.secret_name
        self.data_store_secret_path = DDSCLIENT_CONFIG_MOUNT_PATH
        self.env_dict = {"DDSCLIENT_CONF": "{}/config".format(DDSCLIENT_CONFIG_MOUNT_PATH)}

        job_save_output_settings = job.k8s_settings.save_output
        self.image_name = job_save_output_settings.image_name
        self.command = job_save_output_settings.base_command
        self.requested_cpu = job_save_output_settings.cpus
        self.requested_memory = job_save_output_settings.memory


class RecordOutputProjectConfig(object):
    def __init__(self, job, config):
        job_record_output_project_settings = job.k8s_settings.record_output_project

        record_output_project_settings = config.record_output_project_settings
        self.image_name = job_record_output_project_settings.image_name
        self.requested_cpu = job_record_output_project_settings.cpus
        self.requested_memory = job_record_output_project_settings.memory
        self.service_account_name = record_output_project_settings.service_account_name
        self.project_id_fieldname = 'project_id'
        self.readme_file_id_fieldname = 'readme_file_id'
