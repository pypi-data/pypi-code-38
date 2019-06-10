from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
""" Local import. """
from .managers import CategoryModelManager
from .managers import ArticleModelManager


""" Category models here. """
# category model here.
class CategoryModel(models.Model):

    STATUS_CHOICES = (
            ('draft', 'Draft'),
            ('publish', 'Publish'),
            ('withdrow', 'Withdorw'),
    )

    serial        = models.IntegerField(blank=True, null=True)
    title         = models.CharField(max_length=35, unique=True, blank=False, null=False)
    slug          = models.SlugField(max_length=35, unique=True, blank=False, null=False)
    description   = models.TextField(blank=True, null=True)
    author        = models.ForeignKey(User, on_delete=models.CASCADE)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    verification  = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # register model managers here.
    objects = CategoryModelManager()

    # overright the save method.
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(CategoryModel, self).save(*args, **kwargs)

    # str method.
    def __str__(self):
        return self.title

    # create absolute urls here.
    def get_absolute_url_for_category_detail_view(self):
        return reverse("djangopost:category_detail_view", kwargs={'category_slug': self.slug})

    def get_absolute_url_for_category_update_view(self):
        return reverse("djangopost:category_update_view", kwargs={'category_slug': self.slug})

    def get_absolute_url_for_category_delete_view(self):
        return reverse("djangopost:category_delete_view", kwargs={'category_slug': self.slug})

    class Meta:
        ordering = ['serial', 'pk']
        verbose_name = "Djangopost category"
        verbose_name_plural = "Djangopost categories"
#end category model here.
""" end category model here. """


""" Article models here. """
# article model here.
class ArticleModel(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('publish', 'Publish'),
        ('withdrow', 'Withdorw'),
    )

    serial        = models.IntegerField(blank=True, null=True)
    cover_image   = models.ImageField(null=True, blank=True, upload_to='djangopost')
    title         = models.CharField(max_length=95, blank=False, null=False)
    slug          = models.CharField(max_length=95, unique=True, blank=False, null=False)
    category      = models.ForeignKey(CategoryModel, on_delete=models.CASCADE)
    description   = models.TextField(blank=True, null=True)
    shortlines    = models.TextField()
    content       = models.TextField()
    author        = models.ForeignKey(User, on_delete=models.CASCADE)
    verification  = models.BooleanField(default=False)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_promote    = models.BooleanField(default=False)
    is_trend      = models.BooleanField(default=False)
    total_views   = models.IntegerField(blank=True, null=True, default=0)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    # overright the save method.
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(ArticleModel, self).save(*args, **kwargs)

    # call all the model manager here.
    objects = ArticleModelManager()

    # str method here.
    def __str__(self):
        return self.title

    # get absolute url here.
    def get_absolute_url_for_article_detail_view(self):
        return reverse("djangopost:article_detail_view", kwargs={'article_slug': self.slug})

    def get_absolute_url_for_article_update_view(self):
        return reverse("djangopost:article_update_view", kwargs={'article_slug': self.slug})

    def get_absolute_url_for_article_delete_view(self):
        return reverse("djangopost:article_delete_view", kwargs={'article_slug': self.slug})

    def get_absolute_url_for_category_detail_view(self):
        return reverse("djangopost:category_detail_view", kwargs={'category_slug': self.category.slug})

    class Meta:
        ordering = ['serial', 'pk']
        verbose_name = "Djangopost article"
        verbose_name_plural = "Djangopost articles"
# form end here.        
""" end article model here. """