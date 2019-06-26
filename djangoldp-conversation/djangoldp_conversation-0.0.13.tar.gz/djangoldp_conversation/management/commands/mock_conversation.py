from django.core.management.base import BaseCommand, CommandError
from djangoldp_conversation.factories import ConversationFactory, MessageFactory

class Command(BaseCommand):
    help = 'Mock data'

    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=0, help='Number of conversations to create')
        parser.add_argument('--sizeof', type=int, default=10, help='Number of message into each conversation created')

    def handle(self, *args, **options):
        for i in range(0, options['size']):
            conversation = ConversationFactory.create()
            MessageFactory.create_batch(options['sizeof'], conversation=conversation)

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
