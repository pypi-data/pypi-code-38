# -*- coding: utf-8 -*-
import hashlib
import time
import password_generator

from cioppino.twothumbs.rate import loveIt, hateIt, setupAnnotations
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone import schema
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.autoform import directives as form
from z3c.form import button
from z3c.form.browser.radio import RadioFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import IFieldsForm
from zope.component import getUtility
from zope.interface import implements
from zope.i18n import translate

from ideabox.policy import _
from ideabox.policy.userdataschema import IEnhancedUserDataSchema


class IVoteEncoding(IEnhancedUserDataSchema):
    mail = schema.Email(title=_(u"Email"), required=False)

    form.widget(vote=RadioFieldWidget)
    vote = schema.Choice(
        title=_(u"Vote"), required=True, vocabulary=u"ideabox.vocabularies.vote"
    )

    form.widget(project=MultiSelect2FieldWidget)
    project = schema.List(
        title=_(u"Project(s)"),
        value_type=schema.Choice(
            title=_(u"Project"),
            vocabulary=u"ideabox.vocabularies.projects",
        ),
        required=True,
    )


class VoteEncodingForm(Form):
    label = _(u"Vote encoding")
    implements(IFieldsForm)
    fields = Fields(IVoteEncoding).select(
        "last_name",
        "first_name",
        "gender",
        "mail",
        "birthdate",
        "address",
        "zip_code",
        "iam",
        "vote",
        "project"
    )

    fields["project"].widgetFactory = MultiSelect2FieldWidget
    fields["vote"].widgetFactory = RadioFieldWidget
    fields["gender"].widgetFactory = RadioFieldWidget

    _required_fields = ("vote", "project")

    ignoreContext = True

    def update(self):
        for name, field in self.fields.items():
            field.field.required = name in self._required_fields
        super(VoteEncodingForm, self).update()

    def create_user(self, data):
        if data["mail"]:
            existing_user = api.user.get(userid=data["mail"].lower())
            if existing_user:
                self.update_user(existing_user, data)
                return existing_user
        properties = dict(
            last_name=data["last_name"]
            or translate(_(u"Anonymous"), context=self.request),
            first_name=data["first_name"],
            gender=data["gender"],
            birthdate=data["birthdate"],
            zip_code=data["zip_code"],
            iam=data["iam"],
            address=data["address"],
        )
        if not data["mail"]:
            normalizer = getUtility(IIDNormalizer)
            mail = "{0}_{1}@liege2025.be".format(
                normalizer.normalize(data["last_name"])[:15],
                hashlib.md5(str(time.time())).hexdigest()[:10],
            )
        else:
            mail = data["mail"]

        return api.user.create(
            email=mail.lower(),
            password="@1aA{0}".format(password_generator.generate()),
            properties=properties,
        )

    def update_user(self, user, data):
        updates = {}
        new_properties = {
            "last_name": data["last_name"]
            or translate(_(u"Anonymous"), context=self.request),
            "first_name": data["first_name"],
            "gender": data["gender"],
            "birthdate": data["birthdate"],
            "zip_code": data["zip_code"],
            "iam": data["iam"],
            "address": data["address"],
        }
        for field, new_value in new_properties.items():
            if not new_value:
                continue
            if user.getProperty(field) != new_value:
                updates[field] = new_value
        user.setMemberProperties(mapping=updates)

    def send_request(self, data):
        user = self.create_user(data)
        if data["vote"] == "FOR":
            for project in data["project"]:
                context = api.content.find(UID=project)[0].getObject()
                setupAnnotations(context)
                loveIt(context, userid=user.id)
        else:
            for project in data["project"]:
                context = api.content.find(UID=project)[0].getObject()
                setupAnnotations(context)
                hateIt(context, userid=user.id)
        self.request.response.redirect("{0}/vote_encoding".format(self.context.absolute_url()))

    @button.buttonAndHandler(_(u"Send"), name="send")
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.send_request(data)
