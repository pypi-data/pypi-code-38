from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from saleboxdjango.models import BasketWishlist


class Command(BaseCommand):
    def handle(self, *args, **options):
        # delete baskets from expired sessions
        expired_keys = Session \
                        .objects \
                        .filter(expire_date__lte=timezone.now()) \
                        .values_list('session_key', flat=True)

        BasketWishlist \
            .objects \
            .filter(user__isnull=True) \
            .filter(session__in=list(expired_keys)) \
            .delete()

        # delete baskets from deleted sessions
        remaining_keys = Session \
                            .objects \
                            .values_list('session_key', flat=True)

        BasketWishlist \
            .objects \
            .filter(user__isnull=True) \
            .exclude(session__in=list(remaining_keys)) \
            .delete()
