from .base import API

route_to_tenant_query = '''
  mutation routeToTenant($tenantUuid: UUID!, $routeUuid: UUID!) {
    routeToTenant(input: {tenantUuid: $tenantUuid, routeUuid: $routeUuid}) {
      route {
        id
      }
    }
  }
'''

route_to_asset_query = '''
  mutation routeToAsset($assetUuid: UUID!, $routeUuid: UUID!) {
    routeToAsset(input: {assetUuid: $assetUuid, routeUuid: $routeUuid}) {
      route {
        id
      }
    }
  }
'''


class RoutingAPI(API):
    @API.expose_method
    def route_to_tenant(self, route_uuid, tenant_uuid):
        self.perform_query(
            route_to_tenant_query,
            {
                'routeUuid': route_uuid,
                'tenantUuid': tenant_uuid
            }
        )

    @API.expose_method
    def route_to_asset(self, route_uuid, asset_uuid):
        self.perform_query(
            route_to_asset_query,
            {
                'routeUuid': route_uuid,
                'assetUuid': asset_uuid
            }
        )
