# coding=utf-8

"""Models for this app."""

import typing

import markdown
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy
from model_utils.managers import InheritanceManager


class PageBlockManager(models.Manager):

    """Manager for page block objects."""

    def get_language_version(
            self,
            block_type: str,
            desired_language: str
    ) -> typing.Optional['PageBlockTranslation']:
        """
        Get block of desired language and type. If either the
        type or translation is missing returns None.
        """
        try:
            block = self.get(block_type=block_type)
        except PageBlock.DoesNotExist:
            return None
        translations = BasePageBlockTranslation.objects.select_subclasses().filter(page_block=block)
        try:
            return translations.get(language=desired_language)
        except ObjectDoesNotExist:
            return translations.filter(default_translation=True).first()


class PageBlock(models.Model):
    """

    Page block.

    Represents single logical block that can have many translations.

    """

    block_type = models.CharField(
        unique=True, max_length=256,
        verbose_name="Block Name",
        help_text=ugettext_lazy("Name of the block, will be used in HTML as a reference. Please do not update.")
    )

    objects = PageBlockManager()

    def __str__(self):
        return self.block_type


class BasePageBlockTranslation(models.Model):

    """Translation for page block."""

    page_block = models.ForeignKey(
        PageBlock,
        related_name="translations",
        on_delete=models.CASCADE
    )
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)

    default_translation = models.BooleanField(default=False)

    objects = InheritanceManager()

    class Meta:
        """Meta class"""
        unique_together = (
            ("page_block", "language"),
        )


class PageBlockTranslation(BasePageBlockTranslation):

    """Translation with text."""

    base_ptr = models.OneToOneField(
        BasePageBlockTranslation,
        on_delete=models.CASCADE,
        parent_link=True,
    )

    cover_image = models.FileField(blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=False)
    contents_md = models.TextField(blank=False, null=False)
    contents_html = models.TextField(editable=False)


class PageBlockUrl(BasePageBlockTranslation):

    """Translation with url."""

    url = models.URLField()


@receiver(pre_save, sender=PageBlockTranslation)
def update_default_translation(instance, **kwargs):  # pylint: disable=unused-argument
    """If this is default translation make all other translations non-default."""
    if instance.default_translation:
        instance.page_block.translations.update(default_translation=False)


@receiver(pre_save, sender=PageBlockTranslation)
def set_html_contents(instance, **kwargs):  # pylint: disable=unused-argument
    """Update html contents."""
    instance.contents_html = markdown.markdown(instance.contents_md)
