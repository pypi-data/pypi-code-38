from django.db import models 


""" Category model managers. """
# Model Manager for ApptwoCategoryModel.
class CategoryModelSchemeQuerySet(models.QuerySet):

    def filter_publish(self):
        return self.filter(status='publish')


class CategoryModelSchemeManager(models.Manager):

    def get_queryset(self):
        return CategoryModelSchemeQuerySet(self.model, using=self._db)

    def filter_publish(self):
        return self.get_queryset().filter_publish()
# End here.        
""" end here. """


""" Model manager for ApptwoArticleModel. """
# model manager start here.
class ArticleModelSchemeQuerySet(models.QuerySet):

    def filter_publish(self):
        return self.filter(status='publish')

    def filter_promoted(self):
        return self.filter(is_promote=True)

    def filter_trending(self):
        return self.filter(is_trend=True)


class ArticleModelSchemeManager(models.Manager):

    def get_queryset(self):
        return ArticleModelSchemeQuerySet(self.model, using=self._db)

    def filter_publish(self):
        return self.get_queryset().filter_publish()

    def filter_promoted(self):
        return self.get_queryset().filter_promoted()

    def filter_trending(self):
        return self.get_queryset().filter_trending()    
#end model manager here.
""" End here. """
