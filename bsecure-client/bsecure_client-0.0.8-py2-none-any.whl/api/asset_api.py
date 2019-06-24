from ..utils import make_timestamp
from .base import API

push_asset_query = '''
  mutation pushAsset(
    $tenantUuid: UUID!,
    $category: String!,
    $code: String!,
    $make: String,
    $model: String,
    $installationTimestamp: DateTime,
    $expectedLifeYears: Float,
    $photo: String
  ) {
    pushAsset(input: {
      tenantUuid: $tenantUuid,
      category: $category,
      code: $code,
      model: $model,
      make: $make,
      installationTimestamp: $installationTimestamp,
      expectedLifeYears: $expectedLifeYears,
      photo: $photo
    }) {
      asset {
        uuid
      }
    }
  }
'''

update_asset_query = '''
  mutation updateAsset(
    $uuid: UUID!,
    $installationTimestamp: DateTime,
    $expectedLifeYears: Float,
    $photo: String
  ) {
    updateAsset(input: {
      uuid: $uuid,
      installationTimestamp: $installationTimestamp,
      expectedLifeYears: $expectedLifeYears,
      photo: $photo
    }) {
      asset {
        uuid
      }
    }
  }
'''

upload_asset_photo_query = '''
  mutation uploadAssetPhoto($filename: String!) {
    uploadAssetPhoto(input: {filename: $filename}) {
      fileId,
      presignedUrl
    }
  }
'''

push_remark_query = '''
  mutation pushRemark(
    $assetUuid: UUID!,
    $createdTimestamp: DateTime!,
    $resolvedTimestamp: DateTime,
    $description: String,
    $resolution: String
  ) {
    pushRemark(input: {
      assetUuid: $assetUuid,
      createdTimestamp: $createdTimestamp,
      resolvedTimestamp: $resolvedTimestamp,
      description: $description,
      resolution: $resolution
    }) {
      remark {
        uuid
      }
    }
  }
'''

push_service_query = '''
  mutation pushService(
    $assetUuid: UUID!,
    $name: String!,
    $createdTimestamp: DateTime!,
    $description: String,
    $dueTimestamp: DateTime,
    $performedTimestamp: DateTime,
    $result: String
  ) {
    pushService(input: {
      assetUuid: $assetUuid,
      name: $name,
      createdTimestamp: $createdTimestamp,
      description: $description,
      dueTimestamp: $dueTimestamp,
      performedTimestamp: $performedTimestamp,
      result: $result
    }) {
      service {
        uuid
      }
    }
  }
'''


class AssetAPI(API):
    @API.expose_method
    def push_asset(self, tenant_uuid, category, code=None, make=None,
                   model=None, installation_timestamp=None,
                   expected_life_years=None, photo=None):
        photo_file_id = self.upload_photo(photo)
        response_data = self.perform_query(
            push_asset_query,
            self.make_variables(
                tenantUuid=tenant_uuid,
                category=category,
                code=code,
                make=make,
                model=model,
                installationTimestamp=make_timestamp(installation_timestamp),
                expectedLifeYears=expected_life_years,
                photo=photo_file_id
            )
        )
        return response_data['pushAsset']['asset']['uuid']

    @API.expose_method
    def update_asset(self, uuid, installation_timestamp=None,
                     expected_life_years=None, photo=None):
        photo_file_id = self.upload_photo(photo)
        response_data = self.perform_query(
            update_asset_query,
            self.make_variables(
                uuid=uuid,
                installationTimestamp=make_timestamp(installation_timestamp),
                expectedLifeYears=expected_life_years,
                photo=photo_file_id
            )
        )
        return response_data['updateAsset']['asset']['uuid']

    def upload_photo(self, photo):
        return self.upload_file(
            photo,
            upload_asset_photo_query,
            'uploadAssetPhoto'
        )

    @API.expose_method
    def push_asset_remark(self, asset_uuid, created_timestamp,
                          resolved_timestamp=None, description=None,
                          resolution=None):
        response_data = self.perform_query(
            push_remark_query,
            self.make_variables(
                assetUuid=asset_uuid,
                createdTimestamp=make_timestamp(created_timestamp),
                resolvedTimestamp=make_timestamp(resolved_timestamp),
                description=description
            )
        )
        return response_data['pushRemark']['remark']['uuid']

    @API.expose_method
    def push_asset_service(self, asset_uuid, name, created_timestamp,
                           description=None, due_timestamp=None,
                           performed_timestamp=None, result=None):
        response_data = self.perform_query(
            push_service_query,
            self.make_variables(
                assetUuid=asset_uuid,
                name=name,
                description=description,
                createdTimestamp=make_timestamp(created_timestamp),
                dueTimestamp=make_timestamp(due_timestamp),
                performedTimestamp=make_timestamp(performed_timestamp),
                result=result
            )
        )
        return response_data['pushService']['service']['uuid']
