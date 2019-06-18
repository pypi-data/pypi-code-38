from .base import API

push_tenant_query = '''
  mutation pushTenant(
    $name: String!,
    $formattedAddress: String!,
    $latitude: Float!,
    $longitude: Float!,
    $clientName: String,
    $frontPhoto: String
  ) {
    pushTenant(input: {
      name: $name,
      formattedAddress: $formattedAddress,
      latitude: $latitude,
      longitude: $longitude,
      clientName: $clientName,
      frontPhoto: $frontPhoto
    }) {
      tenant {
        uuid
      }
    }
  }
'''

upload_place_front_photo_query = '''
  mutation uploadPlaceFrontPhoto($filename: String!) {
    uploadPlaceFrontPhoto(input: {filename: $filename}) {
      fileId,
      presignedUrl
    }
  }
'''

create_place_document_by_tenant_query = '''
  mutation createPlaceDocumentByTenant($tenantUuid: UUID!, $title: String!, $fileId: String!) {
    createPlaceDocumentByTenant(input: {tenantUuid: $tenantUuid, title: $title, fileId: $fileId}) {
      placeDocument {
        id
      }
    }
  }
'''

upload_place_document_query = '''
  mutation uploadPlaceDocument($filename: String!) {
    uploadPlaceDocument(input: {filename: $filename}) {
      fileId,
      presignedUrl
    }
  }
'''

all_place_documents_by_tenant_query = '''
  query allPlaceDocumentsByTenant($tenantUuid: UUID!) {
    allPlaceDocumentsByTenant(tenantUuid: $tenantUuid) {
      edges {
        node {
          title
        }
      }
    }
  }
'''


class PlaceAPI(API):
    @API.expose_method
    def push_tenant(self, name, formatted_address, gcs_coord, client_name=None,
                    front_photo=None):
        front_photo_file_id = self.upload_front_photo(front_photo)
        response_data = self.perform_query(
            push_tenant_query,
            self.make_variables(
                name=name,
                formattedAddress=formatted_address,
                longitude=gcs_coord[0],
                latitude=gcs_coord[1],
                clientName=client_name,
                frontPhoto=front_photo_file_id
            )
        )
        return response_data['pushTenant']['tenant']['uuid']

    def upload_front_photo(self, front_photo):
        return self.upload_file(
            front_photo,
            upload_place_front_photo_query,
            'uploadPlaceFrontPhoto'
        )

    @API.expose_method
    def create_place_document_by_tenant(self, tenant_uuid, title, document):
        document_file_id = self.upload_place_document(document)
        self.perform_query(
            create_place_document_by_tenant_query,
            {
                'tenantUuid': tenant_uuid,
                'title': title,
                'fileId': document_file_id
            }
        )

    @API.expose_method
    def all_place_documents_by_tenant(self, tenant_uuid):
        response_data = self.perform_query(
            all_place_documents_by_tenant_query,
            {
                'tenantUuid': tenant_uuid
            }
        )
        return [
            edge['node']
            for edge in response_data['allPlaceDocumentsByTenant']['edges']
        ]

    def upload_place_document(self, document):
        return self.upload_file(
            document,
            upload_place_document_query,
            'uploadPlaceDocument'
        )
