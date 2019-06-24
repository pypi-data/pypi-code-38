from alas_ce0.common.client_base import EntityClientBase


class ShelfCellTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/shelf-cell-templates/'


class ShelfRowTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/shelf-row-templates/'


class ShelfTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/shelf-templates/'
