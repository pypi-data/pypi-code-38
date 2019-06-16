import datetime
from django.db import models
from django.utils import timezone


class Post (models.Model):
    #author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def was_published_recently(self):
        return timezone.now() >= self.published_date >=\
               timezone.now() - datetime.timedelta(days=1)
    was_published_recently.admin_order_field = 'published_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    def __str__(self):
        return self.title


class Comment (models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    #author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    text = models.TextField()

    def publish(self):
        self.save()

    def __str__(self):
        return self.text



