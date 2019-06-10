# this task is chief if task_index = 0
from common.global_variable import JOB_CONTENT_TYPE_CODE, JOB_CONTENT_TYPE_CUSTOM_DATASET, \
    JOB_CONTENT_TYPE_KNOWN_DATASETS


class TrainingTask(object):
    def __init__(self,
                 job_uuid=None,
                 task_uuid=None,
                 keep_alive_interval=None,
                 signal_finish=None,
                 ask_finish=None,
                 task_role=None,
                 container_image=None,
                 cluster_spec=None,
                 task_index=None,
                 download_info=None,
                 command=None,):

        # Validate task_uuid
        if job_uuid is None:
            raise ValueError("job_uuid is None")

        self.job_uuid = job_uuid

        # Validate task_uuid
        if task_uuid is None:
            raise ValueError("task_uuid is None")

        self.task_uuid = task_uuid

        # Validate job_uuid
        if job_uuid is None:
            raise ValueError("job_uuid is None")

        self.job_uuid = job_uuid

        # Validate keep_alive_interval
        if keep_alive_interval is None:
            raise ValueError("keep_alive_interval is None")

        try:
            self.keep_alive_interval = int(keep_alive_interval)
        except:
            raise ValueError("keep_alive_interval is not integer")

        if self.keep_alive_interval <= 0:
            raise ValueError("keep_alive_interval is not greater than 0")

        # Validate signal_finish
        if signal_finish is None:
            raise ValueError("signal_finish is None")

        try:
            self.signal_finish = bool(signal_finish)
        except:
            raise ValueError("signal_finish is not boolean")

        # Validate ask_finish
        if ask_finish is None:
            raise ValueError("ask_finish is None")

        try:
            self.ask_finish = bool(ask_finish)
        except:
            raise ValueError("ask_finish is not boolean")

        # Validate task cannot be both ask and signal finish
        if self.signal_finish and self.ask_finish:
            raise ValueError("unexpected task both signal and ask finish")

        # Validate task_role
        if task_role is None:
            raise ValueError("task_role is None")

        if task_role != "worker" and task_role != "ps":
            raise ValueError("task_role {} is not valid".format(task_role))

        self.task_role = task_role

        # Validate container_image
        if container_image is None:
            raise ValueError("container_image is None")

        self.container_image = container_image

        if command is None:
            raise ValueError("command is None")

        self.command = command

        self.cluster_spec = cluster_spec

        self.task_index = task_index

        # Validate download_info
        '''
        download_info should be 
            code: code presign url
            dataset: {
                'url': presigned url,
                'dataset_name': dataset_name, which is job_uuid
            known_datasets: [cifar10]
        '''

        if download_info is None or not isinstance(download_info, dict):
            raise ValueError("download_info is None or not dict")

        if download_info.get(JOB_CONTENT_TYPE_CODE, None) is None or \
           len(download_info.get(JOB_CONTENT_TYPE_CODE, None)) == 0:
           raise ValueError("invalid {} in download_urls".format(
                                JOB_CONTENT_TYPE_CODE))

        if JOB_CONTENT_TYPE_CUSTOM_DATASET in download_info:
            custom_dataset = download_info.get(JOB_CONTENT_TYPE_CUSTOM_DATASET, None)
            if custom_dataset is None \
                    or not isinstance(custom_dataset, dict) \
                    or custom_dataset.get('url') is None \
                    or custom_dataset.get('dataset_name') is None:
                raise ValueError("Invalid custom_dataset in download info: {}".format(custom_dataset))

        if JOB_CONTENT_TYPE_KNOWN_DATASETS in download_info:
            known_datasets = download_info.get(JOB_CONTENT_TYPE_KNOWN_DATASETS, None)
            if not isinstance(known_datasets, list) or len(known_datasets) == 0:
                raise ValueError("Invalid known_datasets in download info: {}".format(known_datasets))

        self.download_info = download_info

        # Task state is set to False by default. It is only set to true when
        # the worker reported to master that the task has terminated successfully.
        self.finished = False
        self.tensorboard_process = None
        self.dataset_local_path = None
        self.output_upload_urls = None

        # mapping between known dataset name and local path
        self.known_datasets = {}
