#!/usr/bin/env python3

import configargparse
import os.path
import pika


DEFAULTS = {
    'CONFIG_PATH': os.path.expanduser('~') + '/.config/amqp_txrc',
    'CONFIG_USAGE': """
You are missing configuration file with the proper format.
Example:
[global]
host = rabbit.opensuse.org
user = opensuse
password = opensuse
""",
}


def parse_args():
    parser = configargparse.ArgParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter, default_config_files=[DEFAULTS['CONFIG_PATH']])
    parser.add('-c', '--config', is_config_file=True, help="config file path")
    parser.add('-H', '--host', help="The AMQP host to connect to", default='rabbit.opensuse.org')
    parser.add('--user', default="opensuse", help="Username for the AMQP host")
    parser.add('--password', default="opensuse", help="Password for the AMQP host")
    parser.add('--amqp-options', default="heartbeat=5",
               help="AMQP options as query string, e.g. option1=X&option2=Y")
    parser.add('key', help="AMQP routing key")
    parser.add('messages', nargs='*')
    args = parser.parse_args()
    return args


def tx(args):
    connection = pika.BlockingConnection(pika.URLParameters("amqps://%s:%s@%s?%s" % (args.user, args.password, args.host, args.amqp_options)))
    channel = connection.channel()
    channel.exchange_declare(exchange='pubsub', exchange_type='topic', passive=True, durable=True)
    routing_key = args.key if args.key else args.routing_key
    message = ' '.join(args.messages) if args.messages else 'Hello World!'
    channel.basic_publish(exchange='pubsub', routing_key=routing_key, body=message)
    print(" [x] Sent %r:%r" % (routing_key, message))
    connection.close()


def main():
    args = parse_args()
    return tx(args)  # pragma: no cover


if __name__ == "__main__":
    main()
