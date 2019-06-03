from django.db import models


class OrderQuerySet(models.query.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)
