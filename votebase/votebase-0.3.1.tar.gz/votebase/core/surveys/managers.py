from django.db import models


class RoundQuerySet(models.query.QuerySet):
    def get_last_round(self, survey):
        """ Gets last created round in survey """
        return self.filter(survey=survey).order_by('-created')[0]

    def by_user(self, user):
        """ Gets segments of surveys owned by user """
        return self.filter(survey__user=user)

    def by_slug(self, slug):
        """ Gets segments by slug """
        return self.filter(slug=slug)


class BrandingImageQuerySet(models.query.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)

    def by_survey(self, survey):
        return self.filter(survey=survey)
