from .__init__ import *


def main(argv=None):
    parser = get_parser()
    args = parser.parse_args(argv)
    response_auth = auth_post(args.server, args.username, args.password, args.database)
    logger.info(f'Response obtained: {response_auth}')

    response_get_records = get_all_records(args.server, args.database, response_auth['response']['token'], args.layout)
    logger.info(f'Records found: {response_get_records}')
    response_close = close_api(args.server, args.database, response_auth['response']['token'])
    logger.info(f'Closing the connection: {response_close}')


if __name__ == "__main__":
    main()
