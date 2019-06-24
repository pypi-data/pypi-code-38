from django.utils import timezone
from django.db import models

from .managers import PublisherManager
from .utils import assert_draft
from .signals import (
    publisher_publish_pre_save_draft,
    publisher_pre_publish,
    publisher_post_publish,
    publisher_pre_unpublish,
    publisher_post_unpublish,
)


class PublisherModelBase(models.Model):
    publisher_linked = models.OneToOneField(
        'self',
        related_name='publisher_draft',
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
    )
    publisher_is_draft = models.BooleanField(
        default=True,
        editable=False,
        db_index=True,
    )
    publisher_is_published = models.BooleanField(
        default=True,
        db_index=True,
    )
    publisher_modified_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )
    publisher_published_at = models.DateTimeField(
        blank=True, null=True
    )

    publisher_fields = (
        'publisher_linked',
        'publisher_is_draft',
        'publisher_is_published',
        'publisher_modified_at',
        'publisher_draft',
    )
    publisher_ignore_fields = publisher_fields + (
        'pk',
        'id',
        'publisher_linked',
    )
    publisher_publish_empty_fields = (
        'pk',
        'id',
    )

    class Meta:
        abstract = True

    @property
    def is_draft(self):
        return self.publisher_is_draft

    @property
    def is_published(self):
        return self.publisher_is_published

    @property
    def is_dirty(self):
        if not self.is_draft:
            return False

        if not self.publisher_linked:
            return True

        if self.publisher_modified_at > self.publisher_linked.publisher_modified_at:
            return True

    @assert_draft
    def clone(self, overrides=None, deep=False):
        if overrides is None:
            overrides = []
        # Reference self for readability
        draft_obj = self
        # Duplicate the draft object and set to published
        cloned_obj = self.__class__.objects.get(pk=self.pk)
        cloned_obj.id = None
        cloned_obj.publisher_linked = None
        cloned_obj.publisher_draft = None
        cloned_obj.publisher_is_draft = True
        cloned_obj.publisher_is_published = False
        cloned_obj.publisher_published_at = None

        for override_field in overrides:
            setattr(cloned_obj, override_field[0], override_field[1])

        cloned_obj.save()

        # Check for translations, if so duplicate the object
        self.clone_translations(draft_obj, cloned_obj)

        # Clone relationships
        self.clone_relations(draft_obj, cloned_obj, deep)

        return cloned_obj

    @assert_draft
    def publish(self, overrides=None):
        if overrides is None:
            overrides = []

        publisher_pre_publish.send(sender=self.__class__, instance=self)

        # Reference self for readability
        draft_obj = self

        # Set the published date if this is the first time the page has been published
        if not draft_obj.publisher_linked:
            draft_obj.publisher_published_at = timezone.now()

        # Duplicate the draft object and set to published
        publish_obj = self.__class__.objects.get(pk=self.pk)

        if draft_obj.publisher_linked is None:
            publish_obj.id = None
        else:
            publish_obj.id = draft_obj.publisher_linked.id

        publish_obj.publisher_linked = None
        publish_obj.publisher_draft = draft_obj
        publish_obj.publisher_is_draft = False
        publish_obj.publisher_is_published = True
        publish_obj.publisher_published_at = draft_obj.publisher_published_at

        for override_field in overrides:
            setattr(publish_obj, override_field[0], override_field[1])

        draft_obj.save()

        publish_obj.save()

        # Check for translations, if so duplicate the object
        self.clone_translations(draft_obj, publish_obj)

        # Clone relationships
        self.clone_relations(draft_obj, publish_obj)

        # Link the draft obj to the current published version
        draft_obj.publisher_linked = publish_obj

        draft_obj.publisher_linked.save()

        draft_obj.save(suppress_modified=True)

        publisher_publish_pre_save_draft.send(sender=draft_obj.__class__, instance=draft_obj)

        publisher_post_publish.send(sender=draft_obj.__class__, instance=draft_obj)

    @assert_draft
    def discard(self, overrides=None):
        if overrides is None:
            overrides = []

        # Reference self for readability
        draft_obj = self

        # If the draft is not published, delete it
        if not draft_obj.publisher_linked:
            draft_obj.delete()

        # Duplicate the draft object and set to published
        new_draft_obj = self.__class__.objects.get(publish_linked=self.publisher_linked)

        # Copy ids from published to draft
        new_draft_obj.publisher_linked_id = new_draft_obj.id
        new_draft_obj.id = draft_obj.id
        new_draft_obj.publisher_is_draft = True
        new_draft_obj.publisher_is_published = False
        for override_field in overrides:
            setattr(new_draft_obj, override_field[0], override_field[1])

        draft_obj.save(suppress_modified=True)

        # Check for translations, if so duplicate the object
        self.clone_translations(draft_obj, new_draft_obj)

        # Clone relationships
        self.clone_relations(draft_obj, new_draft_obj)

        draft_obj.save(suppress_modified=True)

    @assert_draft
    def unpublish(self):
        if not self.is_draft or not self.publisher_linked:
            return

        publisher_pre_unpublish.send(sender=self.__class__, instance=self)
        self.publisher_linked.publisher_is_published = False
        self.publisher_linked.save()
        self.save()
        publisher_post_unpublish.send(sender=self.__class__, instance=self)

    def get_unique_together(self):
        return self._meta.unique_together

    def get_field(self, field_name):
        # return the actual field (not the db representation of the field)
        try:
            # return self._meta.get_field_by_name(field_name)[0]
            return self._meta.get_field(field_name)
        except models.fields.FieldDoesNotExist:
            return None

    @staticmethod
    def clone_translations(src_obj, dst_obj):
        if hasattr(src_obj, 'translations'):
            for translation in src_obj.translations.all():
                translation.pk = None
                translation.master = dst_obj
                translation.save()

    def clone_relations(self, src_obj, dst_obj, deep=True):
        """
        Since copying relations is so complex, leave this to the implementing class
        """
        pass

    def update_modified_at(self):
        self.publisher_modified_at = timezone.now()


class PublisherModel(PublisherModelBase):
    objects = models.Manager()
    publisher_manager = PublisherManager()

    class Meta:
        abstract = True
        permissions = (
            ('can_publish', 'Can publish'),
        )

    def save(self, suppress_modified=False, **kwargs):
        if suppress_modified is False:
            self.update_modified_at()

        super(PublisherModel, self).save(**kwargs)
