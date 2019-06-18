start_integration_query = '''
  mutation startIntegration($endpoint: String!, $host: String!) {
    startIntegration(input: {endpoint: $endpoint, host: $host}) {
      token
    }
  }
'''

finish_integration_query = '''
  mutation finishIntegration($host: String!) {
    finishIntegration(input: {host: $host}) {
      key
    }
  }
'''

push_property_query = '''
  mutation pushProperty(
    $name: String!,
    $formatted: String!,
    $latitude: BigFloat!,
    $longitude: BigFloat!,
    $client: String!
  ) {
    pushProperty(input: {
      name: $name,
      formatted: $formatted,
      latitude: $latitude,
      longitude: $longitude,
      client: $client
    }) {
      uuid
    }
  }
'''

push_asset_query = '''
  mutation pushAsset(
    $tenantGuid: UUID!,
    $category: String!,
    $code: String!,
    $make: String,
    $model: String,
    $photo: String
  ) {
    pushAsset(input: {
      tenantGuid: $tenantGuid,
      category: $category,
      code: $code,
      model: $model,
      make: $make,
      photo: $photo
    }) {
      asset {
        guid
      }
    }
  }
'''

push_remark_query = '''
  mutation pushRemark(
    $assetGuid: UUID!,
    $createdTime: Datetime!,
    $resolvedTime: Datetime,
    $description: String,
    $resolution: String
  ) {
    pushRemark(input: {
      assetGuid: $assetGuid,
      createdTime: $createdTime,
      resolvedTime: $resolvedTime,
      description: $description,
      resolution: $resolution
    }) {
      uuid
    }
  }
'''

push_service_query = '''
  mutation pushService(
    $assetGuid: UUID!,
    $name: String!,
    $description: String,
    $createdTime: Datetime!,
    $dueTime: Datetime,
    $performedTime: Datetime,
    $result: String
  ) {
    pushService(input: {
      assetGuid: $assetGuid,
      name: $name,
      description: $description,
      createdTime: $createdTime,
      dueTime: $dueTime,
      performedTime: $performedTime,
      result: $result
    }) {
      service {
        guid
      }
    }
  }
'''

route_to_place_query = '''
  mutation routeToPlace($tenantGuid: UUID!, $routeGuid: String!) {
    routeToPlace(input: {tenantGuid: $tenantGuid, routeGuid: $routeGuid}) {
      clientMutationId
    }
  }
'''

route_to_asset_query = '''
  mutation routeToAsset($assetGuid: UUID!, $routeGuid: String!) {
    routeToAsset(input: {assetGuid: $assetGuid, routeGuid: $routeGuid}) {
      clientMutationId
    }
  }
'''

create_place_document_by_tenant_query = '''
  mutation createPlaceDocumentByTenant($tenantGuid: UUID!, $title: String!, $filename: String!) {
    createPlaceDocumentByTenant(input: {tenantGuid: $tenantGuid, title: $title, filename: $filename}) {
      placeDocument {
        id
      }
    }
  }
'''

upload_place_document_query = '''
  mutation uploadPlaceDocument($filename: String!) {
    uploadPlaceDocumentFilename(input: {filename: $filename}) {
      filename,
      presignedUrl
    }
  }
'''

upload_asset_photo_query = '''
  mutation uploadAssetPhoto($filename: String!) {
    uploadAssetPhoto(input: {filename: $filename}) {
      filename,
      presignedUrl
    }
  }
'''

all_place_documents_by_tenant_query = '''
  query allPlaceDocumentsByTenant($tenantGuid: UUID!) {
    allPlaceDocumentsByTenant(tenantGuid: $tenantGuid) {
      nodes {
        title
      }
    }
  }
'''
