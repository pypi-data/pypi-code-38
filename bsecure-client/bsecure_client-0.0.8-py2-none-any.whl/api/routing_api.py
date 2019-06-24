from .base import API

route_to_tenant_query = '''
  mutation routeToTenant($tenantUuid: UUID!, $routeCode: String!) {
    routeToTenant(input: {tenantUuid: $tenantUuid, routeCode: $routeCode}) {
      route {
        id
      }
    }
  }
'''

route_to_asset_query = '''
  mutation routeToAsset($assetUuid: UUID!, $routeCode: String!) {
    routeToAsset(input: {assetUuid: $assetUuid, routeCode: $routeCode}) {
      route {
        id
      }
    }
  }
'''


class RoutingAPI(API):
    @API.expose_method
    def route_to_tenant(self, route_code, tenant_uuid):
        self.perform_query(
            route_to_tenant_query,
            {
                'routeCode': route_code,
                'tenantUuid': tenant_uuid
            }
        )

    @API.expose_method
    def route_to_asset(self, route_code, asset_uuid):
        self.perform_query(
            route_to_asset_query,
            {
                'routeCode': route_code,
                'assetUuid': asset_uuid
            }
        )
