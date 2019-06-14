from .base import Base


class Issue(Base):
    template_name = "issuestracker/issue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["issue"] = kwargs["issue"]
        return context
