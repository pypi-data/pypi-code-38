"""Articles models."""

from django.db import models
from django.template.defaultfilters import slugify

# Create your models here.


class Category(models.Model):
    """Category class."""

    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE)

    def __str__(self):
        """Category print."""
        return self.name

    class Meta:
        """Category meta."""

        verbose_name_plural = "categories"


class Article(models.Model):
    """Article class."""

    title = models.CharField(max_length=50, unique=True)
    slug_title = models.SlugField(unique=True)
    tldr = models.CharField(max_length=80)
    content = models.TextField()

    image = models.ImageField(upload_to='article_header')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField(to=Category)

    def __str__(self):
        """Representation."""
        return self.title

    def save(self, *args, **kwargs):
        """Slugify the title before save."""
        self.slug_title = slugify(self.title)
        super(Article, self).save(*args, **kwargs)
