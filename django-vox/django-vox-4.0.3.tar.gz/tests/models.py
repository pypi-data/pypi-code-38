import aspy
import django.contrib.auth.models as auth_models
from django.core import signing
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import crypto
from django.utils.translation import ugettext_lazy as _

from django_vox.base import Contact, full_iri
from django_vox.models import VoxModel, VoxNotification, VoxNotifications
from django_vox.registry import (
    objects,
    provides_contacts,
    Channel,
    Notification,
    Attachment,
    Registration,
    SignalRegistration,
)


class UserRegistration(SignalRegistration):

    vcard = Attachment(
        attr="make_vcard", mime_string="text/vcard", label=_("Contact Info")
    )

    @staticmethod
    def make_vcard(obj) -> str:
        """
        Returns the text content for a RFC 2426 vCard
        """
        params = {"name": obj.get_full_name(), "email": obj.email}

        for key, value in params.items():
            params[key] = value.replace(":", "\\:").replace(";", "\\;")

        return (
            "BEGIN:VCARD\n"
            "VERSION:3.0\n"
            "FN:{obj.first_name} {obj.last_name}\n"
            "EMAIL;TYPE=internet:{obj.email}\n"
            "END:VCARD".format(obj=obj)
        )

    @provides_contacts("email")
    def email_contact(self, obj, _notification):
        yield obj.email

    @provides_contacts("activity")
    def activity_contact(self, obj, *_):
        yield Contact(obj.get_full_name(), "activity", self._get_object_address(obj))

    def get_channels(self):
        return {"": Channel.self(self)}

    def get_activity_object(self, instance, **kwargs):
        return aspy.Person(
            id=self._get_object_address(instance), name=instance.get_full_name()
        )

    def has_activity_endpoint(self, instance):
        return True


class Article(models.Model):

    slug = models.SlugField(primary_key=True)
    author = models.ForeignKey(
        to=auth_models.User, on_delete=models.CASCADE, related_name="+"
    )
    title = models.CharField(_("title"), max_length=254)
    content = models.TextField(_("content"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tests:article", args=[self.slug])

    def save(self, *args, **kwargs):
        new = self.created_at is None
        super().save(*args, **kwargs)
        if new:
            ArticleRegistration.created.issue(self, actor=self.author, target=self)

    def get_subscribers(self):
        return Subscriber.objects.filter(Q(author=self.author) | Q(author=None))


class ArticleRegistration(Registration):
    # we're going to use auto generated activity entries here

    created = Notification(
        _("Notification that a new article was created."),
        actor_type="auth.user",
        # note that the target type here is also the same
        # as the object type (and we'll use the same object)
        # this is mostly pointless, and not a pattern I would
        # recommend, but it's useful for testing
        target_type="tests.article",
    )

    def get_absolute_url(self):
        return reverse("tests:article", args=[self.slug])

    def get_channels(self):
        return {
            "sub": Channel(_("Subscribers"), Subscriber, Article.get_subscribers),
            "author": Channel.field(Article.author),
        }


class Subscriber(models.Model):
    """
    A subscriber to blog articles.

    If the author field is set, only articles from those authors
    are subscribed to; otherwise they all are.
    """

    class Meta:
        unique_together = (("author", "email"),)

    author = models.ForeignKey(
        to=auth_models.User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("author"),
    )
    name = models.CharField(_("name"), max_length=254)
    email = models.EmailField(_("email"), max_length=254, unique=True)
    secret = models.CharField(
        _("secret"),
        max_length=32,
        default="",
        blank=True,
        help_text=_("Used for resetting passwords"),
    )

    def __str__(self):
        return "{} <{}>".format(self.name, self.email)

    @classmethod
    def load_from_token(cls, token):
        signer = signing.Signer()
        try:
            unsigned = signer.unsign(token)
        except signing.BadSignature:
            raise ValueError("Bad Signature")

        parts = unsigned.split(" | ")
        if len(parts) < 2:
            raise ValueError("Missing secret or key")
        secret = parts[0]
        email = parts[1]
        user = cls.objects.get(email=email)
        if user.secret != secret:
            raise LookupError("Wrong secret")
        return user

    def get_token(self):
        """Makes a verify to verify new account or reset password

        Value is a signed 'natural key' (email address)
        Reset the token by setting the secret to ''
        """
        if self.secret == "":
            self.secret = crypto.get_random_string(32)
            self.save()
        signer = signing.Signer()
        parts = (self.secret, self.email)
        return signer.sign(" | ".join(parts))

    def __activity__(self):
        return aspy.Person(name=self.name, id=full_iri(self.get_absolute_url()))

    def get_absolute_url(self):
        return reverse("tests:subscriber", args=[str(self.id)])


class SubscriberVox(SignalRegistration):
    @provides_contacts("email")
    def email_contact(self, obj, _notification):
        yield Contact(obj.name, "email", obj.email)

    @provides_contacts("activity")
    def activity_contact(self, obj, _notification):
        yield Contact(obj.name, "activity", self._get_object_address(obj))

    def get_channels(self):
        return {"": Channel.self(self)}


# this is here to test backwards compatibility
class Comment(VoxModel):
    class VoxMeta:
        notifications = VoxNotifications(
            created=VoxNotification(
                _("Notification that a comment was posted."),
                actor_type="tests.subscriber",
            )
        )

    content = models.TextField(_("content"))
    poster = models.ForeignKey(to=Subscriber, on_delete=models.CASCADE)
    article = models.ForeignKey(to=Article, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        new = self.id is None
        super().save(*args, **kwargs)
        if new:
            self.issue_notification("created", actor=self.poster)

    def get_posters(self):
        yield self.poster

    def get_article_authors(self):
        yield self.article.author

    def get_absolute_url(self):
        frag = "#comment-{}".format(self.id)
        return reverse("tests:article", args=[self.article.pk]) + frag

    def __activity__(self):
        # we're being hacky here to test out the automatic
        # id stuff
        obj = super().__activity__()
        return aspy.Note(id=obj["id"], name="Note", content=self.content)


class GroupRegistration(Registration):
    def get_channels(self):
        return {"users": Channel.field(auth_models.Group.user_set)}


# stuff for testing relationships


class Thing1(models.Model):

    email = models.EmailField()


class Thing2(models.Model):

    email = models.EmailField()


class Thing3(models.Model):

    email = models.EmailField()


class Thing(models.Model):

    thing1 = models.OneToOneField(
        to=Thing1, related_name="thing", on_delete=models.CASCADE
    )

    thing2 = models.ForeignKey(
        to=Thing2, related_name="thing", on_delete=models.CASCADE
    )

    thing3 = models.ManyToManyField(to=Thing3, related_name="thing")


class Thing4(models.Model):
    email = models.EmailField()

    thing = models.OneToOneField(
        to=Thing, related_name="thing4", on_delete=models.CASCADE
    )


class Thing5(models.Model):
    email = models.EmailField()

    thing = models.ForeignKey(to=Thing, related_name="thing5", on_delete=models.CASCADE)


class Thing6(models.Model):
    email = models.EmailField()

    thing = models.ManyToManyField(to=Thing, related_name="thing6")


class ThingThingRegistration(Registration):
    @provides_contacts("email")
    def email_contacts(self, obj, notification):
        return obj.email


class ThingRegistration(Registration):
    def get_channels(self):
        return {
            "thing1": Channel.field(Thing.thing1),
            "thing2": Channel.field(Thing.thing2),
            "thing3": Channel.field(Thing.thing3),
            "thing4": Channel.field(Thing.thing4),
            "thing5": Channel.field(Thing.thing5),
            "thing6": Channel.field(Thing.thing6),
        }


# adding channels & registrations the new way
objects.add(auth_models.User, UserRegistration, regex=r"^~(?P<id>[0-9]+)/$")

objects.add(Subscriber, SubscriberVox, regex=r"^\.(?P<id>[0-9]+)/$")

objects.add(Article, ArticleRegistration, regex=None)

# the old way

objects.add(Comment, regex=None)
objects[Comment].channels.add("poster", _("Poster"), Subscriber, Comment.get_posters)
objects[Comment].channels.add(
    "author", _("Article author"), auth_models.User, Comment.get_article_authors
)

# here to test the ManyToMany channel
objects.add(auth_models.Group, GroupRegistration, regex=None)

objects.add(Thing1, ThingThingRegistration, regex=None)
objects.add(Thing2, ThingThingRegistration, regex=None)
objects.add(Thing3, ThingThingRegistration, regex=None)
objects.add(Thing4, ThingThingRegistration, regex=None)
objects.add(Thing5, ThingThingRegistration, regex=None)
objects.add(Thing6, ThingThingRegistration, regex=None)
objects.add(Thing, ThingRegistration, regex=None)
