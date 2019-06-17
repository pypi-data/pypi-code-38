from kubernetes import client, config
from ..primitives.task import CLI


class KubeCLI(CLI):
    config.load_kube_config()
    v1 = client.CoreV1Api()

    @classmethod
    def get_nodes(cls):
        return super().cli("kubectl get nodes -o wide")


class AWSCLI:
    class S3(CLI):
        @staticmethod
        def list(url=""):
            return super().cli(f"aws s3 ls {url}")

        @staticmethod
        def cp(source: "url", target: "url"):
            return super().cli(f"aws s3 cp {source} {target}")
