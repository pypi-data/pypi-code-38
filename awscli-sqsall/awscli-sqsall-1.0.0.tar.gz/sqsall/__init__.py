import sys
from textwrap import dedent
from datetime import datetime

from awscli.customizations.commands import BasicCommand

def awscli_initialize(cli):
    cli.register('building-command-table.sqs', inject_commands)


def inject_commands(command_table, session, **kwargs):
    for command in (
        SQSReceiveAllMessagesCommand,
        SQSSendAllMessagesCommand,
    ):
        command_table[command.NAME] = command(session)

MESSAGE_ID_SEPARATOR = '\t'

def decide_queue_url(args, sqs):
    if args.queue and args.queue_url:
        raise Exception(
            "Don't provide queue name and url, that's confusing. "
            "Refusing to operate."
        )
    if args.queue:
        return sqs.get_queue_url(QueueName=args.queue)['QueueUrl']

    if not args.queue_url:
        raise Exception("Provide either queue or queue-name.")

    return args.queue_url

class SQSReceiveAllMessagesCommand(BasicCommand):
    NAME = 'receive-all-messages'
    DESCRIPTION = dedent(f"""
For all messages: receive, print, delete.

If it's a FIFO queue, prefix each message with its MessageGroupId and {MESSAGE_ID_SEPARATOR!r}.
""")

    EXAMPLES = dedent(f"""
Redrive a DLQ except for messages that have some fault:
::

    aws sqs receive-all-messages --queue my-dlq | sed '/some fault/d' | aws sqs send-all-messages my-queue

Redrive a FIFO DLQ except for messages that have some fault:
::

  aws sqs receive-all-messages --queue my-dlq.fifo | sed '/some fault/d' | aws sqs send-all-messages my-queue.fifo
""")

    ARG_TABLE = [
        {
            'name': 'queue',
            'help_text':
                'Specifies the queue name. Mutually exclusive with queue-url.',
        },
        {
            'name': 'queue-url',
            'help_text':
                'Specifies the queue url. Mutually exclusive with queue.',
        },
        {
            'name': 'wait-time-seconds',
            'cli_type_name': 'integer',
            'default': '1',
            'help_text':
                'Pass along wait-time-seconds. Unlike receive-message, default '
                'is 1.',
        },
        {
            'name': 'max-number-of-messages',
            'cli_type_name': 'integer',
            'default': '10',
            'help_text':
                'Pass along max-number-of-messages. Unlike receive-message, '
                'the default is 10 (since this is natually a bulk operation).',
        },
    ]

    def _run_main(self, args, parsed_globals):
        sqs = self._session.create_client(
            'sqs',
            region_name=parsed_globals.region,
            verify=parsed_globals.verify_ssl,
            endpoint_url=parsed_globals.endpoint_url,
        )

        queue_url = decide_queue_url(args, sqs)

        seen_message_ids = set()

        while True:
            result = sqs.receive_message(
                QueueUrl=queue_url,
                WaitTimeSeconds=args.wait_time_seconds,
                MaxNumberOfMessages=args.max_number_of_messages,
                AttributeNames=[
                    'MessageGroupId',
                ],
            )
            if 'Messages' not in result:
                break

            receipt_handles = {}

            for msg in result['Messages']:
                msg_id = msg['MessageId']
                if msg_id in seen_message_ids:
                    continue
                seen_message_ids.add(msg_id)

                receipt_handles[msg_id] = msg['ReceiptHandle']

                print(MESSAGE_ID_SEPARATOR.join(filter(bool, [
                    msg.get('Attributes', {}).get('MessageGroupId', ''),
                    msg['Body']
                ])))

            sqs.delete_message_batch(
                QueueUrl=queue_url,
                Entries=[
                    {
                        'Id': id,
                        'ReceiptHandle': handle
                    } for id, handle in receipt_handles.items()
                ]
            )

class SQSSendAllMessagesCommand(BasicCommand):
    NAME = 'send-all-messages'
    DESCRIPTION = dedent(f"""
Send a message for each line read from standard input.

If it's a FIFO queue, each line must be prefixed with its MessageGroupId and {MESSAGE_ID_SEPARATOR!r}.
Non-conforming lines will be ignored.

The MessageDeduplicationId is going to be a timestamp to maximize the likelyhood
of messages being accepted. If you need more control, please use boto directly.
""")

    ARG_TABLE = [
        {
            'name': 'queue',
            'help_text':
                'Specifies the queue name. Mutually exclusive with queue-url.',
        },
        {
            'name': 'queue-url',
            'help_text':
                'Specifies the queue url. Mutually exclusive with queue.',
        },
    ]

    def _run_main(self, args, parsed_globals):
        sqs = self._session.create_client(
            'sqs',
            region_name=parsed_globals.region,
            verify=parsed_globals.verify_ssl,
            endpoint_url=parsed_globals.endpoint_url,
        )

        queue_url = decide_queue_url(args, sqs)

        fifo_mode = queue_url.endswith('.fifo')

        for line in sys.stdin:
            line = line.rstrip('\n')
            attrs = {}
            body = line

            if fifo_mode:
                parts = line.split(MESSAGE_ID_SEPARATOR, 1)
                if len(parts) != 2:
                    print(
                        f"Line `{line}` has no {MESSAGE_ID_SEPARATOR!r} and this is a fifo queue. Skiping.",
                        file=sys.stderr,
                    )
                    continue

                attrs['MessageGroupId'] = parts[0]
                body = parts[1]
                attrs['MessageDeduplicationId'] = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')

            sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=body,
                **attrs,
            )
