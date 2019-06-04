from treelab.grpc_treelab.messages.service_pb2 import EventPayload


def get_event_identifier(event: EventPayload):
    topic = event.eventName.split('.')[-1]
    # prefixes = []
    # if topic == 'CoreCreated':
    #     return event.eventName
    # if topic == 'TableCreated':
    #     prefixes.append(event.tableId)
    # elif topic == 'RowAddedToView':
    #     prefixes.append(event.rowId)
    # elif topic == 'ColumnAddedToView':
    #     prefixes.append(event.columnId)
    # elif topic == 'CellUpdated':
    #     prefixes.extend([event.rowId + event.columnId, event.tableId])
    # elif topic == 'ViewAdded':
    #     prefixes.append(event.view.id)
    #
    # return '.'.join(prefixes + [topic])
    if topic == 'CoreCreated':
        return event.eventName
    if topic == 'TableCreated':
        return event.eventName
    elif topic == 'RowAddedToView':
        return event.eventName
    elif topic == 'ColumnAddedToView':
        return event.eventName
    elif topic == 'CellUpdated':
        return event.eventName
    elif topic == 'ViewAdded':
        return event.eventName
