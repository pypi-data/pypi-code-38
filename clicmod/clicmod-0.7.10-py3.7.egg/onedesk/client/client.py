import logging

logger = logging.getLogger('main')


def get_client(session, instance, client_name):
    params = {'size': 10000}  # TODO this could be better
    client_list = session.get(instance + "/api/clients", params=params)
    logger.debug('Response: %s', client_list.status_code)

    for client in client_list.json()['content']:
        if client['code'] == client_name:
            return client

    logger.debug("No client with the provided name found, exiting...")
    raise SystemExit


def create_client(name):  # TODO implement this
    raise NotImplementedError
