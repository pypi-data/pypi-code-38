from azure.mgmt.compute.v2017_03_30.models import Resource


class AzureTagHelper:

    @staticmethod
    def safely_get_tag(resource: Resource, tag_name: str, value_if_missing: str = None) -> str:
        return resource.tags.get(tag_name, value_if_missing)