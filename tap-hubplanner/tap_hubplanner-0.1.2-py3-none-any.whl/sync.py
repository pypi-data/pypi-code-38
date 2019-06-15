import singer
from singer import metadata, metrics, Transformer, bookmarks

LOGGER = singer.get_logger()


def write_schema(catalog, stream_name):
    stream = catalog.get_stream(stream_name)
    schema = stream.schema.to_dict()
    singer.write_schema(stream_name, schema, stream.key_properties)


def process_records(catalog, stream_name, records):
    if records:
        stream = catalog.get_stream(stream_name)
        schema = stream.schema.to_dict()
        stream_metedata = metadata.to_map(stream.metadata)
        with metrics.record_counter(stream_name) as counter:
            for record in records:
                with Transformer() as transformer:
                    record = transformer.transform(record,
                                                   schema,
                                                   stream_metedata)
                singer.write_record(stream_name, record)
                counter.increment()


def sync_stream(client,
                catalog,
                state,
                start_date,
                streams_to_sync,
                stream_name,
                endpoint_config):
    write_schema(catalog, stream_name)

    LOGGER.info('Sycing {}'.format(stream_name))
    records = client.get(endpoint_config['path'])
    process_records(catalog, stream_name, records)
    singer.write_state(state)


def get_selected_streams(catalog):
    selected_streams = set()
    for stream in catalog.streams:
        mdata = metadata.to_map(stream.metadata)
        root_metadata = mdata.get(())
        if root_metadata and root_metadata.get('selected') is True:
            selected_streams.add(stream.tap_stream_id)
    return list(selected_streams)


def should_sync_stream(streams_to_sync, stream_name):
    selected_streams = streams_to_sync['selected_streams']
    last_stream = streams_to_sync['last_stream']
    if last_stream == stream_name or \
       (last_stream is None and stream_name in selected_streams):
        return True
    return False


def set_current_stream(state, stream_name):
    state['current_stream'] = stream_name
    singer.write_state(state)


def sync(client, catalog, state, start_date):
    streams_to_sync = {
        'selected_streams': get_selected_streams(catalog),
        'last_stream': state.get('current_stream')
    }

    if not streams_to_sync['selected_streams']:
        return

    endpoints = {
        'billingrate': {
            'path': '/billingRate'
        },
        'bookings': {
            'path': '/booking'
        },
        'clients': {
            'path': '/client'
        },
        'events': {
            'path': '/event'
        },
        'projectgroup': {
            'path': '/projectgroup'
        },
        'resourcegroup': {
            'path': '/resourcegroup'
        },
        'holiday': {
            'path': '/holiday'
        },
        'project-tag': {
            'path': '/project-tag'
        },
        'project': {
            'path': '/project'
        },
        'resource': {
            'path': '/resource'
        },
        'unassigned-work': {
            'path': '/unassigned-work'
        }
    }

    for stream_name, endpoint_config in endpoints.items():
        if should_sync_stream(streams_to_sync, stream_name):
            streams_to_sync['last_stream'] = None
            set_current_stream(state, stream_name)
            sync_stream(client,
                        catalog,
                        state,
                        start_date,
                        streams_to_sync,
                        stream_name,
                        endpoint_config)

    set_current_stream(state, None)
