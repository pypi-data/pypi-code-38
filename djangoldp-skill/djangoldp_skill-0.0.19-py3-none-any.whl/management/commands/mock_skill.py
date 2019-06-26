from django.core.management.base import BaseCommand, CommandError
from djangoldp_skill.factories import SkillFactory
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Mock data'

    def randomMember(self, quantity: int = 10):
        query_set = User.objects.order_by('?')[:quantity]
        return query_set

    def add_arguments(self, parser):
        parser.add_argument('--size', type=int, default=0, help='Number of skill to create')
        parser.add_argument('--sizeof', type=int, default=10, help='Number of members into each skill created')

    def handle(self, *args, **options):
        for i in range(0, options['size']):
            random_member = self.randomMember(options['sizeof']);
            SkillFactory.create(members=random_member);

        self.stdout.write(self.style.SUCCESS('Successful data mock install'))
