from singer.catalog import Catalog, CatalogEntry, Schema

from tap_hubplanner.schema import get_schemas


def discover():
    schemas = get_schemas()
    catalog = Catalog([])

    for schema_name, schema_dict in schemas.items():
        schema = Schema.from_dict(schema_dict)

        metadata = []
        metadata.append({
            'metadata': {
                'selected-by-default': False
            },
            'breadcrumb': []
        })
        for field_name in schema_dict['properties'].keys():
            if field_name is '_id':
                inclusion = 'automatic'
            else:
                inclusion = 'available'
            metadata.append({
                'metadata': {
                    'inclusion': inclusion
                },
                'breadcrumb': ['properties', field_name]
            })

        catalog.streams.append(CatalogEntry(
            stream=schema_name,
            tap_stream_id=schema_name,
            schema=schema,
            metadata=metadata,
            key_properties=['_id']
        ))

    return catalog
