from alas_ce0.common.client_base import EntityClientBase


class CargoVehicleTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/cargo-vehicle-templates/'


class ShelfCargoVehicleTemplateClient(EntityClientBase):
    entity_endpoint_base_url = '/management/shelf-cargo-vehicle-templates/'
