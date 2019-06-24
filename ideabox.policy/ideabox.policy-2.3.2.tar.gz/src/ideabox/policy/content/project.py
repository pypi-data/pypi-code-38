# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from collective.z3cform.select2.widget.widget import MultiSelect2FieldWidget
from plone import api
from plone.app.textfield import RichText
from plone.app.textfield.value import IRichTextValue
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.dexterity.browser import view
from plone.dexterity.content import Container
from plone.indexer.decorator import indexer
from plone.supermodel import model
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from plone.app.dexterity import _ as DXMF

from ideabox.policy import _


class IProject(model.Schema):
    """IProject"""

    title = schema.TextLine(title=DXMF(u"label_title", default=u"Title"), required=True)

    form.widget(project_theme=MultiSelect2FieldWidget)
    project_theme = schema.List(
        title=_(u"Domain(s) concerned"),
        value_type=schema.Choice(
            title=_(u"Domain(s) concerned"), vocabulary=u"collective.taxonomy.theme"
        ),
        required=True,
    )

    form.widget(project_district=MultiSelect2FieldWidget)
    project_district = schema.List(
        title=_(u"District(s) concerned"),
        value_type=schema.Choice(
            title=_(u"District(s) concerned"),
            vocabulary=u"collective.taxonomy.district",
        ),
        required=True,
    )

    body = RichText(title=_(u"Content"), required=True)
    form.widget("body", RichTextFieldWidget)
    model.primary("body")

    form.mode(original_author="hidden")
    original_author = schema.TextLine(title=_(u"Original author"), required=False)


class Project(Container):
    implements(IProject)


class ProjectView(view.DefaultView):

    _timeline_states = (
        "deposited",
        "project_analysis",
        "vote",
        "result_analysis",
        "study_in_progress",
        "in_progress",
        "realized",
    )
    _rating_states = ("vote", "result_analysis", "rejected")

    @property
    def can_edit(self):
        return api.user.has_permission(
            "cmf.ModifyPortalContent", obj=self.context, user=api.user.get_current()
        )

    @property
    def default_image(self):
        """Try to find the default image for the project, return `None` otherwise"""
        portal = api.portal.get()
        if "project_default_large.jpg" in portal:
            return portal["project_default_large.jpg"].absolute_url()

    @property
    def get_images_url(self):
        contents = self.context.listFolderContents(
            contentFilter={"portal_type": "Image"}
        )
        images_url = []
        for content in contents:
            images_url.append(content.absolute_url())
        if not images_url:
            default_image = self.default_image
            if default_image is not None:
                images_url.append(default_image)
        return images_url

    def get_news(self):
        return api.content.find(
            context=self.context,
            portal_type="News Item",
            sort_on="Date",
            sort_order="descending",
        )

    @property
    def review_state(self):
        return api.content.get_state(obj=self.context)

    @property
    def before_selected(self):
        return self.review_state in self._timeline_states[:4] + ("rejected",)

    @property
    def _workflow_history(self):
        history = [
            {
                "order": self._timeline_states.index(l.get("review_state")),
                "state": l.get("review_state"),
                "date": l.get("time"),
            }
            for l in self.context.workflow_history.values()[0]
            if l.get("review_state") in self._timeline_states
        ]
        return sorted(history, key=lambda x: x["order"])

    @property
    def can_view_timeline(self):
        return False  # Temporarily fix as requested
        if self.review_state == "rejected":
            return False
        return self.review_state in self._timeline_states

    @property
    def can_view_rating(self):
        return self.review_state in self._rating_states

    @property
    def timeline_states(self):
        history = self._workflow_history
        current_state = self.review_state
        first_timeline_states = self._timeline_states[:4]
        second_timeline_states = self._timeline_states[4:]
        selected_states = (
            self.review_state in first_timeline_states
            and first_timeline_states
            or second_timeline_states
        )
        states = [
            {"state": e, "date": "", "class": u"unfinished"} for e in selected_states
        ]
        idx = (
            current_state in self._timeline_states
            and self._timeline_states.index(current_state)
            or 0
        )
        for line in history:
            # Ensure that next steps that were completed in the past is not
            # displayed
            if line["order"] > idx:
                break
            state = [s for s in states if s["state"] == line["state"]]
            if len(state) == 1:
                state[0]["date"] = line["date"]
                state[0]["class"] = u"finished"
        return states

    @property
    def anonymous(self):
        return api.user.is_anonymous()

    def creator(self):
        return getattr(self.context, "original_author", self.context.Creator())

    def author(self):
        return api.user.get(self.creator())

    def authorname(self):
        author = self.author()
        if author:
            infos = [author.getProperty("first_name"), author.getProperty("last_name")]
            return " ".join([i for i in infos if i])
        return author and author["fullname"] or self.creator()

    def get_project_theme(self):
        factory = getUtility(IVocabularyFactory, "collective.taxonomy.theme")
        vocabulary = factory(self.context)
        values = []
        for token in self.context.project_theme:
            try:
                values.append(
                    translate(vocabulary.getTerm(token).title, context=self.context)
                )
            except KeyError:
                continue
        return ", ".join(values)

    def get_project_district(self):
        factory = getUtility(IVocabularyFactory, "collective.taxonomy.district")
        vocabulary = factory(self.context)
        values = []
        for token in self.context.project_district:
            try:
                values.append(
                    translate(vocabulary.getTerm(token).title, context=self.context)
                )
            except KeyError:
                continue
        return ", ".join(values)


@indexer(IProject)
def searchabletext_project(object, **kw):
    result = []

    fields = ["title", "description", "body", "original_author"]
    for field_name in fields:
        value = getattr(object, field_name, None)
        if type(value) is unicode:
            text = safe_unicode(value).encode("utf-8")
            result.append(text)
        elif IRichTextValue.providedBy(value):
            transforms = getToolByName(object, "portal_transforms")
            text = (
                transforms.convertTo(
                    "text/plain",
                    safe_unicode(value.raw).encode("utf-8"),
                    mimetype=value.mimeType,
                )
                .getData()
                .strip()
            )
            result.append(text.encode("utf8"))

    return " ".join(result)
