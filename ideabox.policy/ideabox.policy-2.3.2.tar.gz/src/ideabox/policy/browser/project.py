# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from plone import api

from ideabox.policy import _


class SummaryProgressionView(BrowserView):
    @property
    def title(self):
        return _("Projects in progression")

    @property
    def filter_widget(self):
        return "c6"

    def get_summary(self):
        return (
            {
                "title": "study_in_progress",
                "count": self.count("study_in_progress"),
                "description": _(u"diagnose and analysis"),
            },
            {
                "title": "in_progress",
                "count": self.count("in_progress"),
                "description": _(u"Setting up"),
            },
            {"title": "realized", "count": self.count("realized"), "description": None},
        )

    def count(self, state):
        return len(
            api.content.find(
                context=self.context, portal_type="Project", review_state=state
            )
        )


class SummaryThemeView(BrowserView):
    @property
    def title(self):
        return _("The 7 main themes")

    @property
    def filter_widget(self):
        return "c1"

    def get_summary(self):
        return [
            {
                "title": t.title,
                "count": self.count(t.remoteUrl[-4:]),
                "description": None,
                "code": t.remoteUrl[-4:],
            }
            for t in api.portal.get()["projets"]["par-theme"].listFolderContents()
        ]

    def count(self, theme):
        return len(
            api.content.find(
                context=self.context.get("projets", self.context),
                portal_type="Project",
                project_theme=theme,
            )
        )
