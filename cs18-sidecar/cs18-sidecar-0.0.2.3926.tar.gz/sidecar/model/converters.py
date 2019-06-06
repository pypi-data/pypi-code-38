from sidecar.model.objects import ISidecarConfiguration
from sidecar.model.schemas import KubernetesSidecarConfigurationSchema, AwsSidecarConfigurationSchema, \
    AzureSidecarConfigurationSchema


class SidecarConfigurationFactory:
    @staticmethod
    def get(data: dict) -> ISidecarConfiguration:
        if data["provider"] == "kubernetes":
            return KubernetesSidecarConfigurationSchema().load(data)
        if data["provider"] == "aws":
            return AwsSidecarConfigurationSchema().load(data)
        if data["provider"] == "azure":
            return AzureSidecarConfigurationSchema().load(data)
