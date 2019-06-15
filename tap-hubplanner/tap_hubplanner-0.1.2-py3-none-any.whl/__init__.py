#!/usr/bin/env python3
import json

import singer
from singer import utils, metadata

from tap_hubplanner.client import HubPlannerClient
from tap_hubplanner.discover import discover
from tap_hubplanner.sync import sync

REQUIRED_CONFIG_KEYS = ['api_key']
LOGGER = singer.get_logger()


def ensure_credentials_are_authorized(client):
    LOGGER.info('Testing authentication.')
    try:
        client.get('/billingRate', params={'limit': 1})
    except BaseException:
        raise Exception(
            'Error with Hub Planner authentication. Please ensure your configuration contains a valid API key.')


def do_discover(client):
    ensure_credentials_are_authorized(client)

    LOGGER.info('Starting discover')
    catalog = discover()
    print(json.dumps(catalog.to_dict(), indent=2))
    LOGGER.info('Finished discover')


def do_sync(client,
            catalog,
            state,
            start_date):
    ensure_credentials_are_authorized(client)

    LOGGER.info('Starting sync')
    sync(client,
         catalog,
         state,
         start_date)
    LOGGER.info("Finished sync")


@utils.handle_top_exception(LOGGER)
def main():
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    with HubPlannerClient(args.config) as client:
        if args.discover:
            do_discover(client)
        else:
            catalog = args.catalog or discover()
            state = args.state or {}
            do_sync(client,
                    catalog,
                    state,
                    args.config['start_date'])


if __name__ == "__main__":
    main()
