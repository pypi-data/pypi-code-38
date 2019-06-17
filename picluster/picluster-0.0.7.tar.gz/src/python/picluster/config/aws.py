from .base import Config


class AWSConfig(Config):
    k8s_controller_ip = "52.82.5.226"
    kops_state_storage = "s3://kops-state-storage"
