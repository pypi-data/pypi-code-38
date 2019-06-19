from django.db import models
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string

import markdown


def generate_slug(length: int) -> str:
    """Generate a random slug"""
    chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return get_random_string(length, chars)


class Message(models.Model):
    """Model for a message"""
    
    slug = models.SlugField(unique=True, max_length=32)
    message = models.TextField()
    is_editable = models.BooleanField(default=False, verbose_name="Autoriser l'édition")
    is_deletable = models.BooleanField(default=False, verbose_name="Autoriser la suppression")
    
    @property
    def markdown(self):
        return markdown.markdown(self.message, output_format='html5')
    
    def save(self, *args, **kwargs):
        """Custom message saving to add a random slug"""
        
        # Three tries to generate unique slug
        for i in range(0, 3):
            
            if not self.slug:
                self.slug = generate_slug(5)
                
            try:
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                self.slug = generate_slug(5)
    
    def __str__(self):
        return self.slug
